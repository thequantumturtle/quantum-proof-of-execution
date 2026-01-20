# Portability Notes

Running "the same" circuit in Qiskit and Cirq can differ in subtle ways:

- Gate decompositions and default gate sets can vary across SDKs.
- Measurement ordering and bitstring endianness are not consistent by default.
- Transpilation and optimization passes can change circuit depth and structure.
- Simulator randomness and seeding behavior differ between backends.
- Result formats are different (Qiskit counts use bitstrings; Cirq histograms use integers).
- Noise models, if enabled, are not directly comparable across toolchains.

The toy workloads in this repo normalize results into comparable count dictionaries, but this should not be treated as a rigorous portability guarantee.
