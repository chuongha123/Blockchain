from flask import Blueprint, request, jsonify

from api.blockchain import store_sensor_data, get_sensor_data, get_all_data

api = Blueprint("api", __name__)


@api.route("/store", methods=["POST"])
def store_data():
    data = request.json
    device_id = data.get("device_id")
    temperature = data.get("temperature")

    if not device_id or temperature is None:
        return jsonify({"error": "Missing data"}), 400

    tx_hash = store_sensor_data(device_id, temperature)
    return jsonify({"message": "Data has been stored", "transaction": tx_hash})


@api.route("/get/<int:index>", methods=["GET"])
def get_data(index):
    try:
        data = get_sensor_data(index)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Data not found", "details": str(e)}), 404


@api.route("/get-all", methods=["GET"])
def get_all():
    try:
        data = get_all_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": "Data not found", "details": str(e)}), 404
