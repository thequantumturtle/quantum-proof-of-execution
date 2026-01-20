import cirq


def build_circuit(n_qubits=3, depth=2, theta=1.234):
    qubits = [cirq.LineQubit(i) for i in range(n_qubits)]
    circuit = cirq.Circuit()
    for i, q in enumerate(qubits):
        circuit.append(cirq.ry(theta * (i + 1))(q))
    for layer in range(depth):
        for i in range(n_qubits - 1):
            circuit.append(cirq.CNOT(qubits[i], qubits[i + 1]))
        circuit.append(cirq.rz(theta * (layer + 1))(qubits[-1]))
    circuit.append(cirq.measure(*qubits, key="m"))
    return circuit


def run(n_qubits=3, depth=2, theta=1.234, shots=1024, seed=1234):
    circuit = build_circuit(n_qubits=n_qubits, depth=depth, theta=theta)
    simulator = cirq.Simulator(seed=seed)
    result = simulator.run(circuit, repetitions=shots)
    counts = dict(result.histogram(key="m"))

    width = n_qubits
    formatted = {}
    for key, value in counts.items():
        formatted[format(key, f"0{width}b")] = int(value)
    return formatted
