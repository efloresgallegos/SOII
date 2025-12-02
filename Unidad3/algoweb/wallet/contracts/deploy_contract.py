from pyteal import compileTeal, Mode
from .simple_contract import approval_program, clear_state_program

def compile_pyteal():
    approval_teal = compileTeal(approval_program(), mode=Mode.Application, version=6)
    clear_teal = compileTeal(clear_state_program(), mode=Mode.Application, version=6)

    with open("wallet/contracts/approval.teal", "w") as f:
        f.write(approval_teal)
    with open("wallet/contracts/clear.teal", "w") as f:
        f.write(clear_teal)

    return "Contratos TEAL generados correctamente."