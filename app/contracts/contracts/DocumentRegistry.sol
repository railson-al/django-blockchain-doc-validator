pragma solidity ^0.8.21;

contract DocumentRegistry {
    mapping(bytes32 => bool) private documents;

    event DocumentRegistered(bytes32 indexed documentHash);

    function registerDocument(bytes32 documentHash) public {
        require(!documents[documentHash], "Document already registered");
        documents[documentHash] = true;
        emit DocumentRegistered(documentHash);
    }

    function verifyDocument(bytes32 documentHash) public view returns (bool) {
        return documents[documentHash];
    }
}