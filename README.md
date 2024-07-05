# ⛽️ [GasPump](https://t.me/gaspump_bot) Python SDK

## High-level overview of trading on GasPump
When a token is deployed, it immediately becomes tradable using a bonding curve. When it collects the hardcap (currently 1000 TON), liquidity is automatically deposited to DeDust.

There are 2 phases of the token lifecycle:
1. Bonding Curve
    - During this phase, the token is tradable using the bonding curve formula.
    - Users can buy and sell tokens.
    - Users trade wrapped tokens ($gasXXX).

2. DEX (DeDust)
    - Before trading on DeDust, users need to unwrap their $gasXXX and get $XXX tokens.
    - Unwrapping is performed 1:1.
    - Unwrapping is required so that nobody can create (and break) a liquidity pool before the hardcap is reached.

## Features
- SDK for GasPump smart contract interactions
- (soon) SDK for GasPump API

## Installation
```bash
pip install gaspump
```

## Usage

Here's a quick buy and sell example of how to use the GasPump Python SDK:
    
```python
import asyncio

from pytoniq import LiteBalancer, WalletV4R2
from pytoniq_core import Address

from gaspump import GaspumpJetton
from gaspump import JettonWallet
from gaspump import calc_buy_ton_amount, wait_until_contract_is_deployed, wait_until_wallet_seqno_changes


async def main():
    jetton_address = Address(input("Enter the jetton master of gaspump token: "))
    wallet_mnemonics = input("Enter the wallet mnemonic via whitespaces 'we, ate, spoon, ...': ")

    wallet_mnemonic_list = wallet_mnemonics.split(" ")

    async with LiteBalancer.from_mainnet_config(trust_level=2, timeout=15) as client:
        wallet = await WalletV4R2.from_mnemonic(client, wallet_mnemonic_list)

        # setup contracts
        gaspump_jetton = GaspumpJetton(jetton_address)

        jetton_wallet_address = await gaspump_jetton.get_jetton_wallet_address(client, wallet.address)
        jetton_wallet = JettonWallet(jetton_wallet_address)

        # buy some jettons
        ton_amount = 300000000  # 0.3 TON
        buy_ton_amount = calc_buy_ton_amount(ton_amount)

        estimated_jetton_amount = await gaspump_jetton.get_estimate_buy_jetton_amount(client, buy_ton_amount)

        print(f"Buying for 0.3 TON...")
        seqno = await wallet.get_seqno()
        await gaspump_jetton.send_buy(wallet, buy_ton_amount, do_check_trade_state=True)
        await wait_until_wallet_seqno_changes(wallet, seqno)

        # check the balance
        await wait_until_contract_is_deployed(jetton_wallet.address, client)

        balance = await jetton_wallet.get_balance(client)
        print(f"✅ Successfully bought {balance / 1e9} jettons (estimated: {estimated_jetton_amount / 1e9})")

        # sell all the jettons
        print(f"Selling all {balance / 1e9} jettons...")

        seqno = await wallet.get_seqno()
        await gaspump_jetton.send_sell(wallet, balance, jetton_wallet, do_check_trade_state=True)
        await wait_until_wallet_seqno_changes(wallet, seqno)

        print(f"✅ Successfully sold {balance / 1e9} jettons")


if __name__ == "__main__":
    asyncio.run(main())
```
