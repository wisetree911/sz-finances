from enum import Enum


class Currency(str, Enum):
    RUB = 'RUB'
    USD = 'USD'


class AssetType(str, Enum):
    stock = 'stock'
    bond = 'bond'
    fund = 'fund'


class AssetSector(str, Enum):
    oil_gas = 'oil_gas'
    utilities = 'utilities'
    telecom = 'telecom'
    metals_mining = 'metals_mining'
    financials = 'financials'
    consumer = 'consumer'
    chemicals = 'chemicals'
    it = 'it'
    real_estate = 'real_estate'
    transport = 'transport'


class TradeDirection(str, Enum):
    buy = 'buy'
    sell = 'sell'


class Role(str, Enum):
    admin = 'admin'
    user = 'user'
