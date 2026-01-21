// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract ProofRecord {
    event Submitted(bytes32 indexed recordHash, address indexed submitter, uint256 timestamp);

    struct Submission {
        address submitter;
        uint256 timestamp;
    }

    mapping(bytes32 => Submission) private submissions;

    function submit(bytes32 recordHash) external {
        require(recordHash != bytes32(0), "invalid hash");
        if (submissions[recordHash].timestamp == 0) {
            submissions[recordHash] = Submission({
                submitter: msg.sender,
                timestamp: block.timestamp
            });
        }
        emit Submitted(recordHash, msg.sender, block.timestamp);
    }

    function getSubmitter(bytes32 recordHash) external view returns (address) {
        return submissions[recordHash].submitter;
    }

    function getTimestamp(bytes32 recordHash) external view returns (uint256) {
        return submissions[recordHash].timestamp;
    }

    function exists(bytes32 recordHash) external view returns (bool) {
        return submissions[recordHash].timestamp != 0;
    }
}
