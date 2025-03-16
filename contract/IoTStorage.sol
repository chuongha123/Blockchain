// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IoTStorage {
    struct SensorData {
        uint256 timestamp;
        string deviceId;
        uint256 temperature;
    }

    SensorData[] public sensorData;

    event DataStored(uint256 index, uint256 timestamp, string deviceId, uint256 temperature);

    function storeData(string memory deviceId, uint256 temperature) public returns (uint256) {
        uint256 index = sensorData.length;
        sensorData.push(SensorData(block.timestamp, deviceId, temperature));
        emit DataStored(index, block.timestamp, deviceId, temperature);
        return index;
    }

    function getData(uint256 index) public view returns (string memory, uint256, uint256) {
        SensorData memory storedData = sensorData[index];
        return (storedData.deviceId, storedData.timestamp, storedData.temperature);
    }

    function getAllData() public view returns (SensorData[] memory) {
        return sensorData;
    }
}
