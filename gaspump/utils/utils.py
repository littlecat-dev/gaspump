import asyncio

from pytoniq import LiteClient, LiteBalancer, BaseWallet
from pytoniq_core import Address


def calc_buy_ton_amount(desired_ton_amount: int) -> int:
    return int(round(desired_ton_amount / 0.99 + 0.12))


async def wait_until_contract_is_deployed(address: Address | str, provider: LiteClient | LiteBalancer,
                                          delay: float = 5):
    current_is_deployed = (await provider.get_account_state(address)).state.type_
    while not current_is_deployed:
        await asyncio.sleep(delay)
        try:
            current_is_deployed = (await provider.get_account_state(address)).state.type_
        except Exception:
            print("Error while getting contract state, retrying...")


async def wait_until_wallet_seqno_changes(wallet: BaseWallet, initial_seqno: int = 0, delay: int = 5):
    current_seqno = await wallet.get_seqno()

    while initial_seqno == current_seqno:
        await asyncio.sleep(delay)
        try:
            current_seqno = await wallet.get_seqno()
        except Exception:
            print("Error while getting seqno, retrying...")

    return current_seqno
