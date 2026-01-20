import argparse
import base64
import hashlib
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("record_path")
    args = parser.parse_args()

    record = json.loads(Path(args.record_path).read_text(encoding="utf-8"))
    payload = payload_from_record(record)

    computed_hash = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    if computed_hash != record["record"]["hash"]:
        print("Hash mismatch")
        sys.exit(1)

    signature_alg = record["record"].get("signature_alg", "none")
    if signature_alg == "none":
        print("OK (unsigned record)")
        return

    signature = base64.b64decode(record["record"]["signature"])
    public_key_bytes = base64.b64decode(record["record"]["public_key"])
    public_key = Ed25519PublicKey.from_public_bytes(public_key_bytes)

    try:
        public_key.verify(signature, bytes.fromhex(computed_hash))
    except Exception:
        print("Signature verification failed")
        sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
