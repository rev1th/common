from enum import StrEnum

class Currency(StrEnum):

    USD = 'USD'
    # Europe
    EUR = 'EUR'
    GBP = 'GBP'
    CHF = 'CHF'
    NOK = 'NOK'
    SEK = 'SEK'
    # Japan
    JPY = 'JPY'
    # Commodity proxy
    CAD = 'CAD'
    AUD = 'AUD'
    NZD = 'NZD'
    # North East Asia
    CNY = 'CNY'
    CNH = 'CNH'
    HKD = 'HKD'
    TWD = 'TWD'
    KRW = 'KRW'
    INR = 'INR'
    # South East Asia
    SGD = 'SGD'
    MYR = 'MYR'
    THB = 'THB'
    IDR = 'IDR'
    PHP = 'PHP'
    # Middle East & Africa
    TRY = 'TRY'
    ZAR = 'ZAR'
    # Latam
    MXN = 'MXN'
    BRL = 'BRL'
    CLP = 'CLP'
    COP = 'COP'
