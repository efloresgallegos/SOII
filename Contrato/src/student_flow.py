#!/usr/bin/env python3
import base64, json, os, sys, time
from algosdk import account, mnemonic, transaction as txn
from algosdk.v2client import algod
from algosdk.encoding import decode_address

ALGOD_ADDRESS = "https://testnet-api.algonode.cloud"
ALGOD_TOKEN = ""
HEADERS = {}

ADMIN_MNEMONIC   = """day best ocean hello gesture steak toilet obscure sail regret afford sample muscle buyer faith say theme scene harsh category mom claw ten about miss"""
STUDENT_MNEMONIC = """woman scale phrase door obscure inspire shed danger book lift helmet armor sign stable assume keep blade bench frequent pizza purity spot fresh abstract route"""
OFFICER_MNEMONIC = """earth dragon inflict paper inject buffalo minute harvest huge phone power keen remain effort cricket wide useless day matrix knock opera pudding pyramid above bird"""  



def normalize_mnemonic(raw: str) -> str:
    return " ".join(raw.strip().split())

def load_account(mnemonic_raw: str):
    mn = normalize_mnemonic(mnemonic_raw)
    words = mn.split()
    if len(words) != 25:
        raise ValueError(f"Mnemonic tiene {len(words)} palabras (debe ser 25).")
    sk = mnemonic.to_private_key(mn)
    addr = account.address_from_private_key(sk)
    return sk, addr

def sha256_file(path: str) -> bytes:
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.digest()

def compile_teal(filepath: str, client) -> bytes:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No existe TEAL: {filepath}")
    with open(filepath, "r") as f:
        src = f.read()
    resp = client.compile(src)
    return base64.b64decode(resp["result"])

# COnexion

algod_client = algod.AlgodClient(ALGOD_TOKEN, ALGOD_ADDRESS, HEADERS)

admin_sk, admin_addr     = load_account(ADMIN_MNEMONIC)
student_sk, student_addr = load_account(STUDENT_MNEMONIC)
officer_sk, officer_addr = load_account(OFFICER_MNEMONIC)

print("[+] Admin:", admin_addr)
print("[+] Student:", student_addr)
print("[+] Officer:", officer_addr)

# Cargar el documento

DOC_PATH = os.path.abspath("docs/plan_estudios.pdf")
if not os.path.exists(DOC_PATH):
    raise FileNotFoundError(f"No se encontró el documento: {DOC_PATH}")

doc_hash = sha256_file(DOC_PATH)
print("[+] Hash del documento:", doc_hash.hex())

# COmpilar contrato

approval_prog = compile_teal("../teal/student_contract.teal", algod_client)
clear_prog    = compile_teal("../teal/clear_state.teal",   algod_client)

# Aplicación

student_id = b"2025A00123"

global_schema = txn.StateSchema(
    num_uints=6,
    num_byte_slices=4
)
local_schema = txn.StateSchema(num_uints=0, num_byte_slices=0)

app_args = [
    doc_hash,
    decode_address(student_addr),
    decode_address(officer_addr),
    student_id
]

params = algod_client.suggested_params()

create_txn = txn.ApplicationCreateTxn(
    sender=admin_addr,
    sp=params,
    on_complete=txn.OnComplete.NoOpOC,
    approval_program=approval_prog,
    clear_program=clear_prog,
    global_schema=global_schema,
    local_schema=local_schema,
    app_args=app_args,
)

signed_create = create_txn.sign(admin_sk)
txid = algod_client.send_transaction(signed_create)
print("[*] Deploy txid:", txid)

txn.wait_for_confirmation(algod_client, txid, 4)
info = algod_client.pending_transaction_info(txid)
app_id = info["application-index"]

print("[+] Aplicación creada, ID =", app_id)

# Firmar el documento

def sign_document(signer_sk, signer_addr, app_id, doc_hash_bytes):
    params = algod_client.suggested_params()
    txn_call = txn.ApplicationNoOpTxn(
        sender=signer_addr,
        sp=params,
        index=app_id,
        app_args=[doc_hash_bytes]
    )
    signed_txn = txn_call.sign(signer_sk)
    txid = algod_client.send_transaction(signed_txn)
    print("➤ Tx enviada:", txid)
    txn.wait_for_confirmation(algod_client, txid, 4)
    print("   Documento firmado por:", signer_addr)

# Firmas

sign_document(student_sk, student_addr, app_id, doc_hash)
sign_document(officer_sk,  officer_addr, app_id, doc_hash)

# Estado Global

app_info = algod_client.application_info(app_id)
gstate = app_info["params"].get("global-state", [])

def decode_state(state):
    out = {}
    for kv in state:
        key = base64.b64decode(kv["key"]).decode()
        if "uint" in kv["value"]:
            out[key] = kv["value"]["uint"]
        else:
            out[key] = base64.b64decode(kv["value"]["bytes"])
    return out

state = decode_state(gstate)

print("\n=== ESTADO GLOBAL ===")
print(json.dumps({
    k: (v.hex() if isinstance(v, (bytes, bytearray)) else v)
    for k, v in state.items()
}, indent=2))

print("\n=== Estado en cadena ===")

def safe_decode(value):
    if value is None:
        return "(sin valor)"
    if isinstance(value, bytes):
        try:
            return value.decode()
        except:
            return value.hex()
    return str(value)

print(f"  - Hash del documento  : {safe_decode(state.get('document_hash'))}")
print(f"  - Dirección estudiante : {safe_decode(state.get('student_addr'))}")
print(f"  - Dirección oficial    : {safe_decode(state.get('officer_addr'))}")
print(f"  - Firmas requeridas    : {safe_decode(state.get('required_signatures'))}")
print(f"  - Id estudiante        : {safe_decode(state.get('student_id'))}")
print(f"  - Firmas actuales      : {safe_decode(state.get('signature_count'))}")
print(f"  - Estudiante firmó?    : {safe_decode(state.get('student_signed'))}")
print(f"  - Oficial firmó?       : {safe_decode(state.get('officer_signed'))}")

