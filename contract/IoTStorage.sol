// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

contract IoTStorage {
    struct Farm {
        uint256 timestamp;
        string farmId;
        uint256 temperature;
        uint256 humidity;
        uint256 waterLevel;
        string productId;
        uint256 lightLevel;
    }

    Farm[] public farms;

    mapping(string => Farm[]) private farmMapping;
    mapping(string => bool) private farmExists;

    function storeData(
        string memory farmId,
        uint256 temperature,
        uint256 humidity,
        uint256 waterLevel,
        string memory productId,
        uint256 lightLevel
    ) public returns (uint256) {
        uint256 index = farms.length;
        Farm memory farm = Farm(block.timestamp, farmId, temperature, humidity, waterLevel, productId, lightLevel);
        farms.push(farm);
        farmMapping[farmId].push(farm);
        farmExists[farmId] = true;
        return index;
    }

    function getAllData() public view returns (Farm[] memory) {
        return farms;
    }

    function getDataByFarmId(string memory farmId) public view returns (Farm[] memory) {
        require(farmExists[farmId], "Device ID does not exist");
        Farm[] memory result = farmMapping[farmId];
        return result;
    }
}