import argparse
import json
import importlib.util
import sys
from pathlib import Path

import qiskit


def load_workload(module_path):
    spec = importlib.util.spec_from_file_location("workload", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def positive_int(value, name):
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(f"{name} must be > 0")
    return parsed


def int_value(value, name):
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"{name} must be an integer") from exc


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=lambda v: positive_int(v, "shots"), default=1024)
    parser.add_argument("--seed", type=lambda v: int_value(v, "seed"), default=1234)
    parser.add_argument("--n-qubits", type=lambda v: positive_int(v, "n-qubits"), default=3)
    parser.add_argument("--depth", type=lambda v: positive_int(v, "depth"), default=2)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    workload = load_workload(root / "qiskit_impl" / "workload.py")

    try:
        counts = workload.run_workload(
            n_qubits=args.n_qubits,
            depth=args.depth,
            seed=args.seed,
            shots=args.shots,
        )
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    payload = {
        "workload": {
            "name": getattr(workload, "WORKLOAD_NAME", "clifford_t_sampling"),
            "n_qubits": args.n_qubits,
            "depth": args.depth,
            "seed": args.seed,
            "shots": args.shots,
        },
        "execution": {
            "framework": "qiskit",
            "framework_version": qiskit.__version__,
            "backend": "qiskit_aer.AerSimulator",
        },
        "results": {
            "counts": counts,
        },
    }
    print(json.dumps(payload, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
