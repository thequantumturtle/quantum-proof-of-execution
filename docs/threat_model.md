# Threat Model

## Verified

- Record integrity via a SHA-256 hash of a canonical JSON payload.
- Signature verification when signature_alg is set (default ed25519).
- The hash anchored on-chain matches the local record hash when compared out of band.

## Not Verified

- Hardware attestation or provenance for any quantum device or simulator.
- That a quantum job actually executed on specific hardware.
- Correctness of SDK transpilation, compiler optimizations, or runtime noise models.
- Economic security, censorship resistance, or finality guarantees of any chain used for anchoring.
- Consensus safety or liveness; this is not a consensus protocol.
