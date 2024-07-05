from pydantic import BaseModel, ConfigDict
from pytoniq_core import Address, Cell

from src.enums import TradeState


class BondingCurveParams(BaseModel):
    math_scale: int
    coin_scale: int
    alpha: int
    beta: int
    max_supply: int
    bonding_curve_max_supply: int
    max_ton_amount: int
    dex_fee_amount: int


class FullJettonData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    total_supply: int
    mintable: int
    owner: Address
    content: Cell
    wallet_code: Cell
    trade_state: TradeState
    bonding_curve_balance: int
    commission_balance: int
    version: int
    bonding_curve_params: BondingCurveParams
    commission_promille: int
    ton_balance: int
    price_nanotons: int
    supply_left: int
    max_supply: int
