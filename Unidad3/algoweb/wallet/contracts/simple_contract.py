from pyteal import *

def approval_program():
    # Ejemplo educativo: contrato que aprueba si ya pasó cierta fecha
    release_time = Int(1735689600)  # 1 enero 2025
    program = Seq([
        Assert(Global.latest_timestamp() > release_time),
        Approve()
    ])
    return program

def clear_state_program():
    return Approve()