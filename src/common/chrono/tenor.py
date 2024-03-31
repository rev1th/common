
from pydantic.dataclasses import dataclass
from dataclasses import InitVar
from typing import Union, Iterable, Optional
from enum import StrEnum
import datetime as dtm
from zoneinfo import ZoneInfo
from pandas.tseries.offsets import DateOffset, MonthEnd, QuarterEnd, YearEnd, MonthBegin, CustomBusinessDay as CBDay

from .calendar import get_bdc, Calendar


def str_to_int(str_int: str) -> int:
    if str_int.isdigit() or (str_int[0] == '-' and str_int[1:].isdigit()):
        return int(str_int)
    return None


class BDayAdjustType(StrEnum):
    Following = 'F'
    Previous = 'P'
    ModifiedFollowing = 'MF'

def get_adjusted_date(adjust_type: Optional[BDayAdjustType], date: dtm.date, calendar: Optional[Calendar]) -> dtm.date:
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
        case _:
            return date

@dataclass()
class BDayAdjust:
    _adjust_type: Optional[BDayAdjustType] = None
    _calendar: Optional[Calendar] = None

    def get_date(self, date: dtm.date) -> dtm.date:
        return get_adjusted_date(self._adjust_type, date, self._calendar)


def parseTenor(offsets: Union[str, tuple[str, str]]):
    if isinstance(offsets, str):
        offset, bdc = offsets, None
    else:
        offset = offsets[0]
        bdc = get_bdc(offsets[1]) if offsets[1] else None
    if len(offset) < 2:
        raise Exception(f'Invalid input {offset}')
    if len(offset) > 3:
        offset_int = str_to_int(offset[:-3])
        match offset[-3:].upper():
            case 'BOM'|'SOM':
                return MonthBegin(n=offset_int)
            case 'EOM':
                return MonthEnd(n=offset_int)
            case 'EOQ':
                return QuarterEnd(n=offset_int)
            case 'EOY':
                return YearEnd(n=offset_int)
    offset_int = str_to_int(offset[:-1])
    match offset[-1]:
        case 'B' | 'b':
            return CBDay(n=offset_int, calendar=bdc)
        case 'Y' | 'y':
            return DateOffset(years=offset_int)
        case 'M' | 'm':
            return DateOffset(months=offset_int)
        case 'W' | 'w':
            return DateOffset(weeks=offset_int)
        case 'D' | 'd':
            return DateOffset(days=offset_int)
        case _:
            raise RuntimeError(f'Cannot parse tenor {offset}')


@dataclass(config=dict(arbitrary_types_allowed = True))
class Tenor:
    offset_init: InitVar[Union[str, tuple[str, str], DateOffset, Iterable[DateOffset], dtm.date]]
    
    def __post_init__(self, offset_init):
        if isinstance(offset_init, str) or isinstance(offset_init, tuple):
            self._offset = parseTenor(offset_init)
        else:
            self._offset = offset_init
    
    def __add__(self, new):
        offsets = self._offset if isinstance(self._offset, Iterable) else [self._offset]
        if isinstance(new._offset, Iterable):
            offsets.extend(new._offset)
        else:
            offsets.append(new._offset)
        return Tenor(offsets)
    
    @classmethod
    def bday(cls, n: int = 0, calendar: Union[Calendar, str] = None):
        return cls(CBDay(n=n, calendar=get_bdc(calendar)))
    
    @property
    def is_backward(self) -> dtm.date:
        offset = self._offset
        if isinstance(offset, DateOffset):
            return offset.n < 0
        elif isinstance(offset, Iterable):
            return offset[0].n < 0
        return False
    
    def _get_date(self, date: dtm.date = None) -> dtm.date:
        offset = self._offset
        if isinstance(offset, dtm.date):
            return offset
        elif isinstance(offset, DateOffset):
            return (date + offset).date()
        elif isinstance(offset, Iterable):
            res = date
            for off_i in offset:
                res = res + off_i
            return res.date()
        return date + offset
    
    def get_date(self, date: dtm.date = None, bd_adjust = BDayAdjust()) -> dtm.date:
        return bd_adjust.get_date(self._get_date(date))
    
    # Generates schedule with Tenor for [from_date, to_date]
    def generate_series(self, from_date: dtm.date, to_date: dtm.date,
                        roll_backward: bool = False,
                        bd_adjust = BDayAdjust(),
                        extended: bool = False, inclusive: bool = False,
                        ) -> list[dtm.date]:
        schedule = []
        if roll_backward:
            date_i = to_date
            while date_i > from_date:
                date_i_adj = bd_adjust.get_date(date_i)
                schedule.insert(0, date_i_adj)
                date_i = self.get_date(date_i)
            if (inclusive and date_i == from_date) or extended:
                date_i_adj = bd_adjust.get_date(date_i)
                schedule.insert(0, date_i_adj)
        else:
            date_i = from_date
            while date_i < to_date:
                date_i_adj = bd_adjust.get_date(date_i)
                schedule.append(date_i_adj)
                date_i = self.get_date(date_i)
            if (inclusive and date_i == to_date) or extended:
                date_i_adj = bd_adjust.get_date(date_i)
                schedule.append(date_i_adj)
        return schedule


# Return all business dates over a period
def get_bdate_series(from_date: dtm.date, to_date: dtm.date, calendar: Union[Calendar, str] = None) -> list[dtm.date]:
    return Tenor.bday(1, calendar=calendar).generate_series(from_date, to_date, inclusive=True)

# Returns last valuation date
def get_last_valuation_date(timezone: str = None, calendar: str = None,
                            roll_hour: int = 18, roll_minute: int = 0) -> dtm.date:
    sys_dtm = dtm.datetime.now()
    val_dtm = sys_dtm.astimezone(ZoneInfo(timezone) if timezone else None)
    val_dt = get_adjusted_date(BDayAdjustType.Previous, val_dtm.date(), calendar=calendar)
    if val_dt < val_dtm.date():
        return val_dt
    if val_dtm.hour < roll_hour or (val_dtm.hour == roll_hour and val_dtm.minute < roll_minute):
        return Tenor(('-1B', calendar)).get_date(val_dt)
    return val_dtm.date()

# Returns current valuation date, roll forward on holiday
def get_current_valuation_date(timezone: str = None, calendar: str = None,
                               roll_hour: int = 18, roll_minute: int = 0) -> dtm.date:
    sys_dtm = dtm.datetime.now()
    val_dtm = sys_dtm.astimezone(ZoneInfo(timezone) if timezone else None)
    val_dt = get_adjusted_date(BDayAdjustType.Following, val_dtm.date(), calendar=calendar)
    if val_dt > val_dtm.date():
        return val_dt
    if val_dtm.hour > roll_hour or (val_dtm.hour == roll_hour and val_dtm.minute >= roll_minute):
        return Tenor(('1B', calendar)).get_date(val_dt)
    return val_dtm.date()

