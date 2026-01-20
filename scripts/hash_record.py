import argparse
import hashlib
import json
from pathlib import Path


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
    print(computed_hash)


if __name__ == "__main__":
    main()
