import json
import sys
from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod

# ----------------------------------------------------------------------
# Configuración de la red (TestNet)
ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN   = ""                     # Algonode no necesita token
HEADERS       = {"User-Agent": "algod-python"}   # opcional

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)

# ----------------------------------------------------------------------
# Crear una nueva cuenta (solo la primera vez)
def crear_cuenta():
    private_key, address = account.generate_account()
    passphrase = mnemonic.from_private_key(private_key)
    print("\n=== NUEVA CUENTA ===")
    print(f"Dirección : {address}")
    print(f"Frase mnemónica (guárdala bien):\n{passphrase}\n")
    return private_key, address

# ----------------------------------------------------------------------
# Consultar saldo
def obtener_saldo(address):
    acct_info = algod_client.account_info(address)
    micro_algo = acct_info.get('amount', 0)
    algo = micro_algo / 1_000_000
    print(f"Saldo de {address[:6]}... : {algo} ALGO")
    return micro_algo

# ----------------------------------------------------------------------
# Enviar ALGO (0.1 ALGO = 100 000 micro‑ALGO)
def enviar_algo(sender_sk, sender_addr, receiver_addr, amount_micro):
    params = algod_client.suggested_params()
    unsigned_txn = transaction.PaymentTxn(
        sender=sender_addr,
        sp=params,
        receiver=receiver_addr,
        amt=amount_micro,
        note=b"Demo Algorand"
    )
    signed_txn = unsigned_txn.sign(sender_sk)

    txid = algod_client.send_transaction(signed_txn)
    print(f"\nTransacción enviada, ID: {txid}")

    # Esperar a que se confirme (máximo ~5 bloques)
    try:
        confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 5)
        print("✅ Confirmada en el bloque:", confirmed_txn.get('confirmed-round'))
    except Exception as e:
        print("⚠️ Error esperando confirmación:", e)

# ----------------------------------------------------------------------
if __name__ == "__main__":
    # 1️⃣ Generar o cargar una cuenta
    # Si ya tienes una frase mnemónica, reemplaza las líneas siguientes:
    #   my_mnemonic = "tu frase aquí ..."
    #   private_key = mnemonic.to_private_key(my_mnemonic)
    #   address = account.address_from_private_key(private_key)
    private_key, address = crear_cuenta()

    # 2️⃣ Ver saldo (debe ser 0 al principio)
    obtener_saldo(address)

    # ------------------------------------------------------------------
    # 👉 Paso manual: solicita fondos en la faucet de TestNet
    # URL: https://bank.testnet.algorand.network/
    # Copia la dirección mostrada arriba y pulsa “Fund Account”.
    # Espera unos segundos y vuelve a ejecutar este script (o llama a
    # obtener_saldo() de nuevo) para comprobar que ahora tienes 1 ALGO
    # (o más) en la cuenta.
    # ------------------------------------------------------------------

    input("\nPresiona ENTER después de haber recibido fondos de la faucet...")

    # Ver saldo actualizado
    obtener_saldo(address)

    # Definir una cuenta receptora de prueba (puedes generar otra o usar
    # una existente). Aquí generamos una segunda cuenta rápida:
    recv_sk, recv_addr = crear_cuenta()
    print("\nReceptor creado. Su dirección será usada para recibir 0.1 ALGO.")
    input("Presiona ENTER para continuar con la transferencia...")

    # Transferir 0.1 ALGO (100 000 micro‑ALGO)
    enviar_algo(private_key, address, recv_addr, 100_000)

    #Mostrar saldos finales
    print("\n=== Saldos finales ===")
    obtener_saldo(address)
    obtener_saldo(recv_addr)