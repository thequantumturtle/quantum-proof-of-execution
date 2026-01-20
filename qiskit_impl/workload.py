from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator


def build_circuit(n_qubits=3, depth=2, theta=1.234):
    qc = QuantumCircuit(n_qubits, n_qubits)
    for i in range(n_qubits):
        qc.ry(theta * (i + 1), i)
    for layer in range(depth):
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
        qc.rz(theta * (layer + 1), n_qubits - 1)
    qc.measure(range(n_qubits), range(n_qubits))
    return qc


def run(n_qubits=3, depth=2, theta=1.234, shots=1024, seed=1234):
    qc = build_circuit(n_qubits=n_qubits, depth=depth, theta=theta)
    simulator = AerSimulator(seed_simulator=seed)
    result = simulator.run(qc, shots=shots).result()
    counts = result.get_counts(qc)
    return dict(counts)
