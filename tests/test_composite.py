"""Mimics anchor/tests/composite/tests/composite.js."""
from pathlib import Path
from typing import Tuple, AsyncGenerator

from pytest import mark, fixture
from solana.keypair import Keypair
from solana.sysvar import SYSVAR_RENT_PUBKEY

from anchorpy import Program, create_workspace, Context
from anchorpy.workspace import close_workspace
from anchorpy.pytest_plugin import localnet_fixture

PATH = Path("anchor/tests/composite/")

localnet = localnet_fixture(PATH)


@fixture(scope="module")
async def program(localnet) -> AsyncGenerator[Program, None]:
    """Create a Program instance."""
    workspace = create_workspace(PATH)
    yield workspace["composite"]
    await close_workspace(workspace)


@fixture(scope="module")
async def initialized_accounts(program: Program) -> Tuple[Keypair, Keypair]:
    """Generate keypairs and use them when callling the initialize function."""
    dummy_a = Keypair()
    dummy_b = Keypair()
    await program.rpc["initialize"](
        ctx=Context(
            accounts={
                "dummy_a": dummy_a.public_key,
                "dummy_b": dummy_b.public_key,
                "rent": SYSVAR_RENT_PUBKEY,
            },
            signers=[dummy_a, dummy_b],
            instructions=[
                await program.account["DummyA"].create_instruction(dummy_a),
                await program.account["DummyB"].create_instruction(dummy_b),
            ],
        ),
    )
    return dummy_a, dummy_b


@fixture(scope="module")
async def composite_updated_accounts(
    program: Program,
    initialized_accounts: Tuple[Keypair, Keypair],
) -> Tuple[Keypair, Keypair]:
    """Run composite_update and return the keypairs used."""
    dummy_a, dummy_b = initialized_accounts
    ctx = Context(
        accounts={
            "foo": {"dummy_a": dummy_a.public_key},
            "bar": {"dummy_b": dummy_b.public_key},
        },
    )
    await program.rpc["composite_update"](1234, 4321, ctx=ctx)
    return initialized_accounts


@mark.asyncio
async def test_composite_update(
    program: Program,
    composite_updated_accounts: Tuple[Keypair, Keypair],
) -> None:
    """Test that the call to composite_update worked."""
    dummy_a, dummy_b = composite_updated_accounts
    dummy_a_account = await program.account["DummyA"].fetch(dummy_a.public_key)
    dummy_b_account = await program.account["DummyB"].fetch(dummy_b.public_key)
    assert dummy_a_account.data == 1234
    assert dummy_b_account.data == 4321
