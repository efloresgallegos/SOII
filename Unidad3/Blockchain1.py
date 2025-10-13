# -------------------------------------------------
# Ejemplo: envío de ALGO en Algorand TestNet
# Requisitos:
#   pip install py-algorand-sdk
# -------------------------------------------------

import json
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

# ------------------------------------------------------------------
# 1. Conexión al nodo Algorand (TestNet)
# ------------------------------------------------------------------
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN   = ""                     # No se necesita token para este endpoint público
algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

# ------------------------------------------------------------------
# 2. Crear o cargar una cuenta
# ------------------------------------------------------------------
# Opción A: generar una cuenta nueva (solo para pruebas)
#private_key, address = account.generate_account()
#print("Nueva cuenta generada:")
#print("  Dirección :", address)
#print("  Mnemonic   :", mnemonic.from_private_key(private_key))

# Opción B: usar una cuenta existente (descomenta y rellena)
mnemonic_phrase = "tu frase mnemónica aquí ..."
private_key = mnemonic.to_private_key(mnemonic_phrase)
address = account.address_from_private_key(private_key)

# ------------------------------------------------------------------
# 3. Consultar balance actual
# ------------------------------------------------------------------
account_info = algod_client.account_info(address)
balance = account_info.get('amount') / 1e6   # Convertir microAlgos a ALGO
print(f"\nBalance actual de {address}: {balance:.6f} ALGO")

# ------------------------------------------------------------------
# 4. Preparar la transacción de pago
# ------------------------------------------------------------------
receiver = "RECEIVER_ADDRESS_AQUI"          # Cambia por la dirección destino
amount   = int(0.5 * 1_000_000)              # 0.5 ALGO = 500 000 microAlgos

# Parámetros de la red (tarifa, última ronda, etc.)
params = algod_client.suggested_params()

# Construir la transacción
pay_txn = transaction.PaymentTxn(
    sender=address,
    sp=params,
    receiver=receiver,
    amt=amount,
    note=b"Oago Algorand"
)

# ------------------------------------------------------------------
# 5. Firmar y enviar la transacción
# ------------------------------------------------------------------
signed_txn = pay_txn.sign(private_key)
txid = algod_client.send_transaction(signed_txn)
print("\nTransacción enviada. TxID:", txid)

# Opcional: esperar a que la transacción sea confirmada
def wait_for_confirmation(client, txid, timeout=10):
    last_round = client.status().get('last-round')
    for _ in range(timeout):
        try:
            pending_txn = client.pending_transaction_info(txid)
            if pending_txn.get('confirmed-round', 0) > 0:
                return pending_txn
        except Exception:
            pass
        client.status_after_block(last_round + 1)
        last_round += 1
    raise Exception("Timeout esperando confirmación")

confirmed_txn = wait_for_confirmation(algod_client, txid)
print("\n✅ Transacción confirmada en la ronda:", confirmed_txn.get('confirmed-round'))
print("Detalles:", json.dumps(confirmed_txn, indent=2))
