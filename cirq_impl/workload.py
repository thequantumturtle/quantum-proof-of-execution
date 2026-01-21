import random
from typing import Dict, Tuple

import cirq

WORKLOAD_NAME = "clifford_t_sampling"
FRAMEWORK_VERSION = cirq.__version__
CLIFFORD_GATES = (cirq.H, cirq.S, cirq.X, cirq.Y, cirq.Z)


def build_circuit(n_qubits: int, depth: int, seed: int) -> cirq.Circuit:
    rng = random.Random(seed)
    qubits = cirq.LineQubit.range(n_qubits)
    circuit = cirq.Circuit()
    for _layer in range(depth):
        for qubit in qubits:
            gate = rng.choice(CLIFFORD_GATES)
            circuit.append(gate(qubit))
            if rng.random() < 0.15:
                circuit.append(cirq.T(qubit))
    circuit.append(cirq.measure(*qubits, key="m"))
    return circuit


def serialize_circuit(circuit: cirq.Circuit) -> str:
    """Return a deterministic JSON representation suitable for hashing."""
    return cirq.to_json(circuit)


def _format_counts(results, n_qubits: int) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for row in results:
        bitstring = "".join(str(bit) for bit in row)
        counts[bitstring] = counts.get(bitstring, 0) + 1
    return counts


def run_workload(
    n_qubits: int,
    depth: int,
    seed: int,
    shots: int,
) -> Tuple[Dict[str, int], cirq.Circuit, str]:
    """Return counts where qubit 0 is the leftmost bit in each bitstring."""
    circuit = build_circuit(n_qubits=n_qubits, depth=depth, seed=seed)
    simulator = cirq.Simulator(seed=seed)
    result = simulator.run(circuit, repetitions=shots)
    measurements = result.measurements["m"]
    counts = _format_counts(measurements, n_qubits=n_qubits)
    return counts, circuit, "cirq.Simulator"


def run(n_qubits: int, depth: int, seed: int, shots: int) -> Dict[str, int]:
    counts, _circuit, _backend = run_workload(
        n_qubits=n_qubits,
        depth=depth,
        seed=seed,
        shots=shots,
    )
    return counts
