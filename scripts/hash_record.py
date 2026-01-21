import argparse
import hashlib
import json
import sys
from pathlib import Path


def canonical_json_bytes(obj):
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return payload.encode("utf-8")


def sha256_prefixed(data: bytes) -> str:
    digest = hashlib.sha256(data).hexdigest()
    return f"sha256:{digest}"


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("record_path")
    args = parser.parse_args()

    record = json.loads(Path(args.record_path).read_text(encoding="utf-8"))
    computed = sha256_prefixed(canonical_json_bytes(record_core(record)))
    print(computed)
    stored = record.get("artifacts", {}).get("record_hash")
    if stored and stored != computed:
        print("Warning: stored record_hash does not match computed value", file=sys.stderr)


if __name__ == "__main__":
    main()
