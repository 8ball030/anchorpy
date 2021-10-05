from typing import Dict

from anchorpy.coder.coder import Coder
from anchorpy.idl import IdlInstruction, Idl
from anchorpy.program.namespace.transaction import TransactionFn
from anchorpy.provider import Provider
from solana.publickey import PublicKey


def build_simulate_item(
    idl_ix: IdlInstruction,
    tx_fn: TransactionFn,
    idl_errors: Dict[int, str],
    provider: Provider,
    coder: Coder,
    program_id: PublicKey,
    idl: Idl,
):
    pass