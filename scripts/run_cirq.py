import argparse
import json
import importlib.util
from pathlib import Path


def load_workload(module_path):
    spec = importlib.util.spec_from_file_location("workload", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shots", type=int, default=1024)
    parser.add_argument("--seed", type=int, default=1234)
    parser.add_argument("--n-qubits", type=int, default=3)
    parser.add_argument("--depth", type=int, default=2)
    parser.add_argument("--theta", type=float, default=1.234)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    workload = load_workload(root / "cirq_impl" / "workload.py")

    counts = workload.run(
        n_qubits=args.n_qubits,
        depth=args.depth,
        theta=args.theta,
        shots=args.shots,
        seed=args.seed,
    )

    print(json.dumps(counts, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
