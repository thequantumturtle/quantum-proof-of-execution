import argparse
import base64
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def canonical_json_bytes(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return payload.encode("utf-8")


def sha256_prefixed(data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    return f"sha256:{digest}"


def load_workload(module_path):
    spec = importlib.util.spec_from_file_location("workload", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record_core(record):
    return {
        "schema": record["schema"],
        "workload": record["workload"],
        "execution": record["execution"],
        "results": record["results"],
        "artifacts": {
            "circuit_hash": record["artifacts"]["circuit_hash"],
        },
    }


def fail(message):
    print(f"FAIL: {message}")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("record_path")
    args = parser.parse_args()

    record = json.loads(Path(args.record_path).read_text(encoding="utf-8"))
    if "artifacts" not in record or "attestation" not in record:
        fail("Record missing artifacts or attestation section")

    framework = record["execution"].get("framework")
    if framework not in ("qiskit", "cirq"):
        fail("Unsupported framework in record")

    root = Path(__file__).resolve().parents[1]
    workload_path = root / f"{framework}_impl" / "workload.py"
    workload_module = load_workload(workload_path)

    workload = record["workload"]
    circuit = workload_module.build_circuit(
        n_qubits=int(workload["n_qubits"]),
        depth=int(workload["depth"]),
        seed=int(workload["seed"]),
    )
    serialized_circuit = workload_module.serialize_circuit(circuit)
    computed_circuit_hash = sha256_prefixed(serialized_circuit.encode("utf-8"))

    if computed_circuit_hash != record["artifacts"].get("circuit_hash"):
        fail("circuit_hash mismatch")

    core = record_core(record)
    computed_record_hash = sha256_prefixed(canonical_json_bytes(core))
    if computed_record_hash != record["artifacts"].get("record_hash"):
        fail("record_hash mismatch")

    attestation = record["attestation"]
    if attestation.get("signing_alg") != "ed25519":
        fail("Unsupported signing_alg")

    signature = base64.b64decode(attestation["signature"])
    public_key_bytes = base64.b64decode(attestation["public_key"])
    public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

    record_digest = bytes.fromhex(computed_record_hash.split(":", 1)[1])
    try:
        public_key.verify(signature, record_digest)
    except Exception:
        fail("Signature verification failed")

    print("OK")


if __name__ == "__main__":
    main()
