from algosdk.v2client import algod
import base64
import json

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def decode_state(state_array):
    """Convierte los valores codificados del estado global en texto legible."""
    decoded = {}
    for item in state_array:
        key = base64.b64decode(item["key"]).decode()
        value = item["value"]
        if value["type"] == 1:  # byte string
            decoded[key] = base64.b64decode(value["bytes"]).decode()
        else:
            decoded[key] = value["uint"]
    return decoded

def get_global_state(app_id: int):
    """Obtiene el estado global del contrato desde la blockchain."""
    try:
        app_info = client.application_info(app_id)
        global_state = app_info["params"].get("global-state", [])
        decoded = decode_state(global_state)
        return decoded
    except Exception as e:
        return {"error": str(e)}