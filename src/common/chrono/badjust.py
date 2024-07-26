
from pydantic.dataclasses import dataclass
from typing import Optional
from enum import StrEnum
import datetime as dtm
from pandas.tseries.offsets import CustomBusinessDay as CBDay

from .calendar import get_bdc, Calendar

class BDayAdjustType(StrEnum):
    Following = 'F'
    Previous = 'P'
    ModifiedFollowing = 'MF'

def get_adjusted_date(adjust_type: BDayAdjustType, date: dtm.date,
                        calendar: Optional[Calendar] = None) -> dtm.date:
    match adjust_type:
        case BDayAdjustType.Following:
            return (date + CBDay(0, calendar=get_bdc(calendar))).date()
        case BDayAdjustType.Previous:
            bdc = get_bdc(calendar)
            return (date + CBDay(1, calendar=bdc) + CBDay(-1, calendar=bdc)).date()
        case BDayAdjustType.ModifiedFollowing:
            date_f = get_adjusted_date(BDayAdjustType.Following, date, calendar)
            # if EOM then preceding else following
            if date_f.year > date.year or (date_f.year == date.year and date_f.month > date.month):
                return get_adjusted_date(BDayAdjustType.Previous, date, calendar)
            return date_f

@dataclass
class BDayAdjust:
    _type: Optional[BDayAdjustType] = None
    _calendar: Optional[Calendar] = None

    def get_date(self, date: dtm.date) -> dtm.date:
        if self._type:
            return get_adjusted_date(self._type, date, self._calendar)
        else:
            return date
