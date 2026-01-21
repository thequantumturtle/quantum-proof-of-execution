import random
from typing import Dict

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

WORKLOAD_NAME = "clifford_t_sampling"
CLIFFORD_GATES = ("h", "s", "x", "y", "z")


def build_circuit(n_qubits: int, depth: int, seed: int) -> QuantumCircuit:
    rng = random.Random(seed)
    qc = QuantumCircuit(n_qubits, n_qubits)
    for _layer in range(depth):
        for qubit in range(n_qubits):
            gate = rng.choice(CLIFFORD_GATES)
            getattr(qc, gate)(qubit)
            if rng.random() < 0.15:
                qc.t(qubit)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def serialize_circuit(circuit: QuantumCircuit) -> str:
    return circuit.qasm()


def run_workload(n_qubits: int, depth: int, seed: int, shots: int) -> Dict[str, int]:
    qc = build_circuit(n_qubits=n_qubits, depth=depth, seed=seed)
    simulator = AerSimulator(seed_simulator=seed)
    result = simulator.run(qc, shots=shots).result()
    counts = result.get_counts(qc)
    return dict(counts)


def run(n_qubits: int, depth: int, seed: int, shots: int) -> Dict[str, int]:
    return run_workload(n_qubits=n_qubits, depth=depth, seed=seed, shots=shots)
