
from pydantic.dataclasses import dataclass
from typing import Optional
from enum import StrEnum
import datetime as dtm
from pandas.tseries.offsets import MonthEnd

class RollConventionType(StrEnum):
    DayOfMonth = 'D'
    EndOfMonth = 'EOM'
    IMM = 'IMM'

def get_rolled_date(roll_type: RollConventionType, date: dtm.date) -> dtm.date:
    match roll_type:
        case RollConventionType.DayOfMonth:
            return date
        case RollConventionType.EndOfMonth:
            return (date + MonthEnd(0)).date()
        case RollConventionType.IMM:
            raise Exception('IMM roll not implemented')

@dataclass
class RollConvention:
    _type: Optional[RollConventionType] = None

    def is_eom(self):
        return self._type == RollConventionType.EndOfMonth

    def get_date(self, date: dtm.date) -> dtm.date:
        if self._type:
            return get_rolled_date(self._type, date)
        else:
            return date
