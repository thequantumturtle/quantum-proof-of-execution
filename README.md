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

## Execution Records

Execution records capture the workload parameters, execution metadata, results, and hashes,
with an Ed25519 signature over the record hash.

### Expected Workflows

The typical flow is:

1. Run a workload (Qiskit or Cirq) to produce counts and confirm parameters.
2. Create a signed execution record with `make_record.py`.
3. Verify the record integrity and signature with `verify_record.py`.
4. (Optional) Extract and compare the `record_hash` for anchoring or audit logs.

If you are iterating on workloads, regenerate the record after any code or parameter change.
The `circuit_hash` and `record_hash` should change whenever the circuit or record core changes.

Create records:

```bash
python scripts/make_record.py --framework qiskit --n-qubits 4 --depth 10 --seed 123 --shots 2000 --out records/qiskit.json
python scripts/make_record.py --framework cirq --n-qubits 4 --depth 10 --seed 123 --shots 2000 --out records/cirq.json
```

Verify and inspect hashes:

```bash
python scripts/verify_record.py records/qiskit.json
python scripts/hash_record.py records/qiskit.json
```

Docker Compose workflow (containerized equivalent of the create/verify/hash steps above):

```bash
docker compose run --rm qiskit
docker compose run --rm cirq
```

Record hashing details:

- `circuit_hash` is `sha256` of the serialized circuit output.
- `record_hash` is `sha256` of the canonical JSON for the record core (no attestation, and
  `artifacts` includes only `circuit_hash`).
- Signatures use Ed25519 over the raw 32-byte digest for the `record_hash` value.

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
