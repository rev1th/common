
from pydantic.dataclasses import dataclass
from typing import Union
from enum import StrEnum, IntEnum


class InstrumentDataField(StrEnum):
    NAME = 'name'
    RIC = 'ric'
    CONTRACT = 'contract'
    CCY = 'ccy'

    LOT_SIZE = 'lotsize'
    TICK_SIZE = 'ticksize'

class MarketDataType(StrEnum):
    LAST = 'last'
    HIGH = 'high'
    LOW = 'low'
    ASK = 'ask'
    BID = 'bid'
    VOLUME = 'volume'
    MID = 'mid'
    SPREAD = 'spread'

    SETTLE = 'settle'
    CLOSE = 'close'
    OPEN = 'open'
    PREV_CLOSE = 'prev_close'
    PREV_OI = 'prev_oi'
    
    UPDATE_TIME = 'update_time'

class OptionDataFlag(StrEnum):
    CALL = 'c'
    PUT = 'p'

class SessionType(IntEnum):
    REGULAR = 0
    EXTENDED = 1

@dataclass
class InstrumentDataModel(dict):
    # data_map: dict[Union[DataField, DataPointType], any]

    def __getitem__(self, data_type: Union[InstrumentDataField, MarketDataType]):
        if data_type == MarketDataType.MID:
            if self[MarketDataType.BID] and self[MarketDataType.ASK]:
                return (self[MarketDataType.BID] + self[MarketDataType.ASK])/2
            else:
                return None
        elif data_type == MarketDataType.SPREAD:
            if self[MarketDataType.BID] and self[MarketDataType.ASK]:
                return self[MarketDataType.ASK] - self[MarketDataType.BID]
            else:
                return None
        else:
            return super().__getitem__(data_type)

