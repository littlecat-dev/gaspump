from typing import Type

from pytoniq import LiteBalancer, LiteClient, BaseWallet
from pytoniq_core import Address, begin_cell

from src.contracts.JettonWallet import JettonWallet
from src.enums import SendMode, TradeState

from src.models import BondingCurveParams, FullJettonData


class GaspumpJetton:
    def __init__(self, address: Address | str):
        self.address = Address(address) if isinstance(address, str) else address

    @classmethod
    def from_address(cls, address: Address | str) -> Type["GaspumpJetton"]:
        return cls(address)

    @classmethod
    def create_buy_cell(cls, do_buy: bool):
        return (begin_cell()
                .store_uint(1825825968, 32)
                .store_bit(do_buy)
                .end_cell())

    async def send_buy(self, wallet: BaseWallet, ton_amount: int, do_check_trade_state: bool = True):
        if ton_amount < 300000000:  # 0.3 TON
            raise ValueError("Minimum amount is 0.3 TON")

        if do_check_trade_state:
            full_jetton_data = await self.get_full_jetton_data(wallet.provider)
            if full_jetton_data.trade_state != TradeState.BONDING_CURVE:
                raise ValueError('Trade state is not BONDING_CURVE')

        message = wallet.create_wallet_internal_message(
            self.address,
            SendMode.PAY_GAS_SEPARATELY,
            ton_amount,
            self.create_buy_cell(True),
        )

        await wallet.raw_transfer([message])

    async def send_sell(self, wallet: BaseWallet, jetton_amount: int, jetton_wallet: JettonWallet,
                        do_check_trade_state: bool = True):
        if do_check_trade_state:
            full_jetton_data = await self.get_full_jetton_data(wallet.provider)
            if full_jetton_data.trade_state != TradeState.BONDING_CURVE:
                raise ValueError('Trade state is not BONDING_CURVE')

        gas_amount = 300000000  # 0.3 TON, most of it will be refunded
        await jetton_wallet.send_burn(wallet, jetton_wallet.address, jetton_amount, gas_amount)

    async def send_unwrap(self, wallet: BaseWallet, jetton_amount: int, jetton_wallet: JettonWallet,
                          do_check_trade_state: bool = True):
        if do_check_trade_state:
            full_jetton_data = await self.get_full_jetton_data(wallet.provider)
            if full_jetton_data.trade_state != TradeState.DEX:
                raise ValueError('Trade state is not DEX')

        gas_amount = 300000000  # 0.3 TON, most of it will be refunded
        await jetton_wallet.send_burn(wallet, jetton_wallet.address, jetton_amount, gas_amount)

    async def get_full_jetton_data(self, provider: LiteBalancer | LiteClient) -> FullJettonData:
        stack = await provider.run_get_method(self.address, 'get_full_jetton_data', [])

        total_supply = stack[0]
        mintable = stack[1]
        owner = stack[2].load_address()
        content = stack[3]
        wallet_code = stack[4]
        trade_state = TradeState(stack[5])
        bonding_curve_balance = stack[6]
        commission_balance = stack[7]
        version = stack[8]

        bonding_curve_params_tuple = stack[9]
        bonding_curve_params = BondingCurveParams(
            math_scale=bonding_curve_params_tuple[0],
            coin_scale=bonding_curve_params_tuple[1],
            alpha=bonding_curve_params_tuple[2],
            beta=bonding_curve_params_tuple[3],
            max_supply=bonding_curve_params_tuple[4],
            bonding_curve_max_supply=bonding_curve_params_tuple[5],
            max_ton_amount=bonding_curve_params_tuple[6],
            dex_fee_amount=bonding_curve_params_tuple[7]
        )

        commission_promille = stack[10]
        ton_balance = stack[11]
        price_nanotons = stack[12]
        supply_left = stack[13]
        max_supply = stack[14]

        return FullJettonData(
            total_supply=total_supply,
            mintable=mintable,
            owner=owner,
            content=content,
            wallet_code=wallet_code,
            trade_state=trade_state,
            bonding_curve_balance=bonding_curve_balance,
            commission_balance=commission_balance,
            version=version,
            bonding_curve_params=bonding_curve_params,
            commission_promille=commission_promille,
            ton_balance=ton_balance,
            price_nanotons=price_nanotons,
            supply_left=supply_left,
            max_supply=max_supply
        )

    async def get_unwrapped_jetton_address(self, provider: LiteBalancer | LiteClient) -> Address:
        stack = await provider.run_get_method(self.address, 'anotherMinterAddress', [])
        return stack[0].load_address()

    async def get_jetton_wallet_address(self, provider: LiteBalancer | LiteClient, owner: Address) -> Address:
        stack = await provider.run_get_method(self.address, 'get_wallet_address', [owner.to_cell().begin_parse()])
        return stack[0].load_address()

    async def get_estimate_buy_jetton_amount(self, provider: LiteBalancer | LiteClient, ton_amount: int) -> int:
        stack = await provider.run_get_method(self.address, 'getBuyAmount', [ton_amount])
        return stack[0]

    async def get_estimate_sell_ton_amount(self, provider: LiteBalancer | LiteClient, jetton_amount: int) -> int:
        stack = await provider.run_get_method(self.address, 'getSellAmount', [jetton_amount])
        return stack[0]
