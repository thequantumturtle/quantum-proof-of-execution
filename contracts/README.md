# ProofRecord Contract

This contract anchors record hashes without custody or economic guarantees. It stores a mapping from record hash to a timestamp, sender, and optional metadata.

Example usage:

- Deploy the contract.
- Call anchor(recordHash, metadata).
- Listen for the RecordAnchored event to detect anchors.

This contract does not attest to quantum hardware, consensus finality, or economic security. It simply provides a place to publish hashes.
