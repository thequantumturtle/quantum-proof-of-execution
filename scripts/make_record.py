import argparse
import base64
import hashlib
import importlib.util
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_json(data):
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def payload_from_record(record):
    return {
        "schema_version": record["schema_version"],
        "workload": record["workload"],
        "execution": record["execution"],
        "record": {
            "record_id": record["record"]["record_id"],
            "created_at": record["record"]["created_at"],
            "hash_alg": record["record"]["hash_alg"],
        },
    }


def load_workload(module_path):
    spec = importlib.util.spec_from_file_location("workload", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sdk", choices=["qiskit", "cirq"], default="qiskit")
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--n-qubits", type=int, default=3)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--theta", type=float, default=1.234)
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    workload_path = root / f"{args.sdk}_impl" / "workload.py"
    workload = load_workload(workload_path)

    started_at = now_iso()
    counts = workload.run(
        n_qubits=args.n_qubits,
        depth=args.depth,
        theta=args.theta,
        shots=args.shots,
        seed=args.seed,
    )
    finished_at = now_iso()

    result_digest = hashlib.sha256(canonical_json(counts).encode("utf-8")).hexdigest()

    record = {
        "schema_version": "0.1",
        "workload": {
            "name": "toy-param-circuit",
            "sdk": args.sdk,
            "parameters": {
                "n_qubits": args.n_qubits,
                "depth": args.depth,
                "theta": args.theta,
            },
            "shots": args.shots,
        },
        "execution": {
            "backend": "qasm_simulator" if args.sdk == "qiskit" else "cirq.Simulator",
            "started_at": started_at,
            "finished_at": finished_at,
            "result_summary": counts,
            "result_digest": result_digest,
        },
        "record": {
            "record_id": str(uuid.uuid4()),
            "created_at": finished_at,
            "hash_alg": "sha256",
            "hash": "",
            "signature_alg": "ed25519",
            "signature": "",
            "public_key": "",
        },
    }

    payload = payload_from_record(record)
    record_hash = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()

    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()
    signature = private_key.sign(bytes.fromhex(record_hash))

    record["record"]["hash"] = record_hash
    record["record"]["signature"] = base64.b64encode(signature).decode("ascii")
    record["record"]["public_key"] = base64.b64encode(
        public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )
    ).decode("ascii")

    output = json.dumps(record, sort_keys=True, indent=2)

    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    main()
