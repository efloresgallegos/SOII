from algosdk import account, mnemonic, transaction
from algosdk.v2client import algod
import base64
from pyteal import compileTeal, Mode
from .simple_contract import approval_program, clear_state_program

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""

mnemonic_phrase = "soon modify evoke arch cube birth width gasp twin soldier gun avoid envelope polar engine blanket gorilla joke assume police portion major guard abstract shoot"
private_key = mnemonic.to_private_key(mnemonic_phrase)
sender = account.address_from_private_key(private_key)

client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS)

def deploy_contract():
    with open("wallet/contracts/approval.teal", "r") as f:
        approval_source = f.read()
    with open("wallet/contracts/clear.teal", "r") as f:
        clear_source = f.read()

    approval = base64.b64decode(client.compile(approval_source)["result"])
    clear = base64.b64decode(client.compile(clear_source)["result"])

    global_schema = transaction.StateSchema(num_uints=1, num_byte_slices=1)
    local_schema = transaction.StateSchema(num_uints=0, num_byte_slices=0)
    sp = client.suggested_params()

    txn = transaction.ApplicationCreateTxn(
        sender,
        sp,
        on_complete=transaction.OnComplete.NoOpOC.real,
        approval_program=approval,
        clear_program=clear,
        global_schema=global_schema,
        local_schema=local_schema,
    )

    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    return f"Contrato enviado. TX ID: {txid}"