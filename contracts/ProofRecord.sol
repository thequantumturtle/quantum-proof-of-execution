// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ProofRecord {
    event RecordAnchored(bytes32 indexed recordHash, address indexed sender, string metadata);

    struct Anchor {
        uint256 timestamp;
        address sender;
        string metadata;
    }

    mapping(bytes32 => Anchor) public anchors;

    function anchor(bytes32 recordHash, string calldata metadata) external {
        require(anchors[recordHash].timestamp == 0, "Already anchored");
        anchors[recordHash] = Anchor({
            timestamp: block.timestamp,
            sender: msg.sender,
            metadata: metadata
        });
        emit RecordAnchored(recordHash, msg.sender, metadata);
    }
}
