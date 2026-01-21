# quantum-proof-of-execution

quantum-proof-of-execution is a small, experimental project that explores how quantum computation jobs can be recorded, verified, and anchored in external systems without making claims about cryptographic security or quantum advantage.

This repo demonstrates a toy "proof of execution" pipeline by running the same parameterized workload across multiple quantum SDKs, producing signed execution records, and anchoring record hashes on-chain with a non-custodial smart contract. It is intentionally minimal and focused on interfaces, portability limits, and trust boundaries.

## Experimental Status

This project is experimental and for research/education only. It is not a consensus protocol, not a security primitive, and does not claim quantum advantage.

## Quickstart

```bash
python -m pip install .
python scripts/make_record.py --framework qiskit --n-qubits 4 --depth 10 --seed 123 --shots 2000 --out records/qiskit.json
python scripts/verify_record.py records/qiskit.json
```

## Docker

```bash
docker build -t quantum-proof-of-execution .
docker run --rm quantum-proof-of-execution python scripts/run_qiskit.py --shots 256
```

## Docker Compose

```bash
docker compose run --rm qiskit
docker compose run --rm cirq
```

## Docker Quickstart (Records)

```bash
docker build -t quantum-proof-of-execution:dev .

docker run --rm -v "${PWD}:/app" quantum-proof-of-execution:dev \
  python scripts/make_record.py --framework qiskit --n-qubits 4 --depth 10 --seed 123 --shots 2000 --out records/qiskit.json

docker run --rm -v "${PWD}:/app" quantum-proof-of-execution:dev \
  python scripts/verify_record.py records/qiskit.json
```

## Execution Records

Execution records capture the workload parameters, execution metadata, results, and hashes,
with an Ed25519 signature over the record hash.

If you are iterating on workloads, regenerate the record after any code or parameter change.
The `circuit_hash` and `record_hash` should change whenever the circuit or record core changes.

## Record Schema (High Level)

Records are JSON documents with the following top-level fields:

- schema: string
- workload: { name, n_qubits, depth, seed, shots }
- execution: { framework, framework_version, backend, started_at, finished_at }
- results: { counts }
- artifacts: { circuit_hash, record_hash }
- attestation: { signing_alg, public_key, signature }

Hashing and signatures:

- `circuit_hash` is `sha256` of the serialized circuit output.
- `record_hash` is `sha256` of the canonical JSON for the record core (no attestation, and
  `artifacts` includes only `circuit_hash`).
- Signatures use Ed25519 over the raw 32-byte digest for the `record_hash` value.
