import argparse
import base64
import hashlib
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def canonical_json_bytes(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return payload.encode("utf-8")


def sha256_prefixed(data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    return f"sha256:{digest}"


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_workload(module_path):
    spec = importlib.util.spec_from_file_location("workload", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_private_key(args):
    if not args.private_key_b64 and not args.private_key_file:
        return Ed25519PrivateKey.generate()
    if args.private_key_b64 and args.private_key_file:
        raise ValueError("Provide only one of --private-key-b64 or --private-key-file")
    if args.private_key_file:
        key_b64 = Path(args.private_key_file).read_text(encoding="utf-8").strip()
    else:
        key_b64 = args.private_key_b64
    key_bytes = base64.b64decode(key_b64)
    return Ed25519PrivateKey.from_private_bytes(key_bytes)


def record_core(workload, execution, results, circuit_hash):
    return {
        "schema": "qpoe-0.1",
        "workload": workload,
        "execution": execution,
        "results": results,
        "artifacts": {
            "circuit_hash": circuit_hash,
        },
    }


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--framework", required=True)
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--n-qubits", type=int, default=3)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--out", type=str, default="")
    parser.add_argument("--private-key-b64", type=str, default="")
    parser.add_argument("--private-key-file", type=str, default="")
    return parser.parse_args()


def main():
    args = parse_args()

    root = Path(__file__).resolve().parents[1]
    workload_path = root / f"{args.framework}_impl" / "workload.py"
    workload_module = load_workload(workload_path)

    started_at = now_iso()
    counts, circuit, backend_name = workload_module.run_workload(
        n_qubits=args.n_qubits,
        depth=args.depth,
        seed=args.seed,
        shots=args.shots,
    )

    framework_version = workload_module.FRAMEWORK_VERSION

    finished_at = now_iso()
    serialized_circuit = workload_module.serialize_circuit(circuit)
    circuit_hash = sha256_prefixed(serialized_circuit.encode("utf-8"))

    workload = {
        "name": workload_module.WORKLOAD_NAME,
        "n_qubits": args.n_qubits,
        "depth": args.depth,
        "seed": args.seed,
        "shots": args.shots,
    }
    execution = {
        "framework": args.framework,
        "framework_version": framework_version,
        "backend": backend_name,
        "started_at": started_at,
        "finished_at": finished_at,
    }
    results = {
        "counts": counts,
    }

    core = record_core(workload, execution, results, circuit_hash)
    record_hash = sha256_prefixed(canonical_json_bytes(core))

    private_key = load_private_key(args)
    public_key = private_key.public_key()
    # Sign the raw 32-byte digest for the sha256:<hex> record_hash value.
    record_digest = bytes.fromhex(record_hash.split(":", 1)[1])
    signature = private_key.sign(record_digest)

    record = {
        **core,
        "artifacts": {
            "circuit_hash": circuit_hash,
            "record_hash": record_hash,
        },
        "attestation": {
            "signing_alg": "ed25519",
            "public_key": base64.b64encode(
                public_key.public_bytes(
                    encoding=serialization.Encoding.Raw,
                    format=serialization.PublicFormat.Raw,
                )
            ).decode("ascii"),
            "signature": base64.b64encode(signature).decode("ascii"),
        },
    }

    output = json.dumps(record, sort_keys=True, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
