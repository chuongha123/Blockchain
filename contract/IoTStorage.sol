// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IoTStorage {
    struct IoTData {
        string deviceId;
        string data;
        uint256 timestamp;
    }

    mapping(string => IoTData) private dataStorage;

    event DataStored(string deviceId, string data, uint256 timestamp);

    function storeData(string memory deviceId, string memory data) public {
        dataStorage[deviceId] = IoTData(deviceId, data, block.timestamp);
        emit DataStored(deviceId, data, block.timestamp);
    }

    function getData(string memory deviceId) public view returns (string memory, uint256) {
        IoTData memory storedData = dataStorage[deviceId];
        return (storedData.data, storedData.timestamp);
    }
}