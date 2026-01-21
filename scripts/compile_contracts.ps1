docker run --rm -v "${PWD}:/src" ethereum/solc:0.8.20 `
  /src/contracts/ProofRecord.sol --abi --bin
