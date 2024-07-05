from enum import IntEnum


class GasAmount(IntEnum):
    STANDART = 0.3 * 1e9


class TradeState(IntEnum):
    BONDING_CURVE = 0
    DEPOSITING_TO_DEX = 1
    DEX = 2


class SendMode(IntEnum):
    NONE = 0
    PAY_GAS_SEPARATELY = 1
    IGNORE_ERRORS = 2
    DESTROY_ACCOUNT_IF_ZERO = 32
    CARRY_ALL_REMAINING_INCOMING_VALUE = 64
    CARRY_ALL_REMAINING_BALANCE = 128


class Opcode(IntEnum):
    TRANSFER = 0xf8a7ea5
    TRANSFER_NOTIFICATION = 0x7362d09c
    INTERNAL_TRANSFER = 0x178d4519
    BURN = 0x595f07bc
    EXCESSES = 0xd53276db
