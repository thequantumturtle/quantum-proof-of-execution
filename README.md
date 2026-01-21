# quantum-proof-of-execution

quantum-proof-of-execution is a small, experimental project that explores how quantum computation jobs can be recorded, verified, and anchored in external systems without making claims about cryptographic security or quantum advantage.

This repo demonstrates a toy "proof of execution" pipeline by running the same parameterized workload across multiple quantum SDKs, producing signed execution records, and anchoring record hashes on-chain with a non-custodial smart contract. It is intentionally minimal and focused on interfaces, portability limits, and trust boundaries.

## Experimental Status

This project is experimental and for research/education only. It is not a consensus protocol, not a security primitive, and does not claim quantum advantage.

## Quickstart

```bash
python -m pip install .
python scripts\make_record.py --sdk qiskit --out records\sample_record.json
```

## Docker

```bash
docker build -t quantum-proof-of-execution .
docker run --rm quantum-proof-of-execution python scripts/run_qiskit.py --shots 256
```

## Record Schema (High Level)

Records are JSON documents with the following top-level fields:

- schema_version: string
- workload: { name, sdk, parameters, shots }
- execution: { backend, started_at, finished_at, result_summary, result_digest }
- record: { record_id, created_at, hash_alg, hash, signature_alg, signature, public_key }

The record hash is computed over a canonical JSON payload containing:

- schema_version
- workload
- execution
- record: { record_id, created_at, hash_alg }

The signature (when present) signs the hash bytes. See scripts/make_record.py and scripts/verify_record.py for the exact logic.

Note: records/sample_record.json is intentionally unsigned (signature_alg: none) to keep it lightweight and illustrative. Run scripts/make_record.py to generate a signed record.
