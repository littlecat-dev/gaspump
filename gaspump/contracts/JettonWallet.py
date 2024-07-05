from pydantic import BaseModel, ConfigDict
from pytoniq import LiteBalancer, LiteClient, BaseWallet
from pytoniq_core import Address, begin_cell, Cell

from src.enums import SendMode, Opcode, GasAmount


class WalletData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    balance: int
    owner_address: Address
    minter_address: Address
    wallet_code: Cell


class JettonWallet:
    def __init__(self, address: Address | str):
        self.address = Address(address) if isinstance(address, str) else address

    @classmethod
    def from_address(cls, address: Address | str) -> "JettonWallet":
        return cls(address)

    @classmethod
    def create_burn_cell(cls, amount: int, address: Address | str):
        return (begin_cell()
                .store_uint(Opcode.BURN, 32)
                .store_uint(0, 64)
                .store_coins(amount)
                .store_address(address)
                .store_address(address)
                .end_cell())

    @classmethod
    def create_transfer_cell(cls, destination: Address | str, response_address: Address | str, amount: int,
                             custom_payload: Cell | None = None, forward_payload: Cell | None = None,
                             forward_amount: int = 0, query_id: int = 0, ):
        return (begin_cell()
                .store_uint(Opcode.TRANSFER, 32)
                .store_uint(query_id, 64)
                .store_coins(amount)
                .store_address(destination)
                .store_address(response_address)
                .store_maybe_ref(custom_payload)
                .store_coins(forward_amount)
                .store_maybe_ref(forward_payload)
                .end_cell())

    async def send_transfer(self, wallet: BaseWallet, jetton_wallet: Address | str, response_address: Address | str,
                            amount: int, gas_amount=GasAmount.STANDART):
        message = wallet.create_wallet_internal_message(
            jetton_wallet,
            SendMode.PAY_GAS_SEPARATELY,
            gas_amount,
            self.create_transfer_cell(destination=jetton_wallet, response_address=response_address, amount=amount),
        )

        await wallet.raw_transfer([message])

    async def send_burn(self, wallet: BaseWallet, jetton_wallet: Address | str, amount: int,
                        gas_amount: int = GasAmount.STANDART):
        message = wallet.create_wallet_internal_message(
            jetton_wallet,
            SendMode.PAY_GAS_SEPARATELY,
            gas_amount,
            self.create_burn_cell(amount, wallet.address),
        )

        await wallet.raw_transfer([message])

    async def get_wallet_data(self, provider: LiteBalancer | LiteClient) -> WalletData:
        stack = await provider.run_get_method(self.address, 'get_wallet_data', [])

        balance = stack[0]
        owner_address = stack[1].load_address()
        minter_address = stack[2].load_address()
        wallet_code = stack[3]

        return WalletData(
            balance=balance,
            owner_address=owner_address,
            minter_address=minter_address,
            wallet_code=wallet_code
        )

    async def get_balance(self, provider: LiteBalancer | LiteClient) -> int:
        wallet_data = await self.get_wallet_data(provider)
        return wallet_data.balance
