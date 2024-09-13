
from pydantic.dataclasses import dataclass
from typing import Union
from enum import StrEnum, IntEnum


class DataField(StrEnum):
    NAME = 'name'
    RIC = 'ric'
    CONTRACT = 'contract'
    CCY = 'ccy'

    LOT_SIZE = 'lotsize'
    TICK_SIZE = 'ticksize'

class DataPointType(StrEnum):
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
class DataModel(dict):
    # data_map: dict[Union[DataField, DataPointType], any]

    def __getitem__(self, data_type: Union[DataField, DataPointType]):
        if data_type == DataPointType.MID:
            if self[DataPointType.BID] and self[DataPointType.ASK]:
                return (self[DataPointType.BID] + self[DataPointType.ASK])/2
            else:
                return None
        elif data_type == DataPointType.SPREAD:
            if self[DataPointType.BID] and self[DataPointType.ASK]:
                return self[DataPointType.ASK] - self[DataPointType.BID]
            else:
                return None
        else:
            return super().__getitem__(data_type)

