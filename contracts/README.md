# ProofRecord Contract

This contract anchors record hashes and emits an event for auditability. It stores the first
submitter and timestamp for each hash.

Example usage:

- Deploy the contract.
- Call submit(recordHash).
- Listen for Submitted events to detect anchors.

This contract does not verify quantum execution, provide custody, handle payouts, or act as a
consensus mechanism. It only anchors hashes.

Computing the bytes32 hash:

- The Python tooling outputs record hashes like `sha256:<hex>`.
- Extract the `<hex>` portion and prefix it with `0x` to get the `bytes32` value.

Example (JavaScript):

```javascript
const recordHashStr = "sha256:0123...abcd";
const recordHash = "0x" + recordHashStr.split(":")[1];
await contract.submit(recordHash);
```
