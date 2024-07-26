
from pydantic.dataclasses import dataclass
from typing import Union, Iterable, Optional
import datetime as dtm
from zoneinfo import ZoneInfo
from pandas.tseries.offsets import DateOffset, MonthEnd, QuarterEnd, YearEnd, MonthBegin, CustomBusinessDay as CBDay

from .calendar import get_bdc, Calendar
from .badjust import BDayAdjust, BDayAdjustType, get_adjusted_date
from .roll import RollConvention


def str_to_int(str_int: str) -> int:
    if str_int.isdigit() or (str_int[0] == '-' and str_int[1:].isdigit()):
        return int(str_int)
    return None

def is_eom(date: dtm.date):
    next_day = date + dtm.timedelta(days=1)
    return next_day.month != date.month

def parseTenor(offsets: Union[str, tuple[str, str]]) -> DateOffset:
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
    _code: Union[str, tuple[str, Optional[str]], DateOffset]
    
    def __post_init__(self):
        if isinstance(self._code, str) or isinstance(self._code, tuple):
            self._offset = parseTenor(self._code)
        else:
            self._offset = self._code
    
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
        if isinstance(offset, DateOffset):
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
                        step_backward: bool = False,
                        bd_adjust = BDayAdjust(),
                        roll_convention = RollConvention(),
                        extended: bool = False, inclusive: bool = False,
                        ) -> list[dtm.date]:
        schedule = []
        if step_backward:
            if roll_convention.is_eom():
                if not is_eom(to_date):
                    roll_convention = RollConvention()
            date_i = to_date
            while date_i > from_date:
                date_i_adj = bd_adjust.get_date(roll_convention.get_date(date_i))
                # ensure still within period after adjustment
                if date_i_adj > from_date:
                    schedule.append(date_i_adj)
                    date_i = self.get_date(date_i)
                    # move prior to adjusted
                    while date_i >= date_i_adj:
                        date_i = self.get_date(date_i)
                else:
                    break
            if (inclusive and date_i == from_date) or extended:
                date_i_adj = bd_adjust.get_date(roll_convention.get_date(date_i))
                schedule.append(date_i_adj)
            schedule.reverse()
        else:
            date_i = from_date
            while date_i < to_date:
                date_i_adj = bd_adjust.get_date(roll_convention.get_date(date_i))
                if date_i_adj < to_date:
                    schedule.append(date_i_adj)
                    date_i = self.get_date(date_i)
                    while date_i <= date_i_adj:
                        date_i = self.get_date(date_i)
                else:
                    break
            if (inclusive and date_i == to_date) or extended:
                date_i_adj = bd_adjust.get_date(roll_convention.get_date(date_i))
                schedule.append(date_i_adj)
        return schedule


# Return all business dates over a period
def get_bdate_series(from_date: dtm.date, to_date: dtm.date, calendar: Union[Calendar, str] = None) -> list[dtm.date]:
    from_date_adj = get_adjusted_date(BDayAdjustType.Following, from_date, calendar=calendar)
    return Tenor.bday(1, calendar=calendar).generate_series(from_date_adj, to_date, inclusive=True)

# Returns last business date
def get_last_valuation_date(timezone: str = None, calendar: Union[Calendar, str] = None,
                            roll_hour: int = 18, roll_minute: int = 0) -> dtm.date:
    sys_dtm = dtm.datetime.now()
    val_dtm = sys_dtm.astimezone(ZoneInfo(timezone) if timezone else None)
    val_dt = get_adjusted_date(BDayAdjustType.Previous, val_dtm.date(), calendar=calendar)
    if val_dt < val_dtm.date():
        return val_dt
    if val_dtm.hour < roll_hour or (val_dtm.hour == roll_hour and val_dtm.minute < roll_minute):
        return Tenor(('-1B', calendar)).get_date(val_dt)
    return val_dtm.date()

# Returns current business date rolling forward on holiday
def get_current_valuation_date(timezone: str = None, calendar: Union[Calendar, str] = None,
                               roll_hour: int = 18, roll_minute: int = 0) -> dtm.date:
    sys_dtm = dtm.datetime.now()
    val_dtm = sys_dtm.astimezone(ZoneInfo(timezone) if timezone else None)
    val_dt = get_adjusted_date(BDayAdjustType.Following, val_dtm.date(), calendar=calendar)
    if val_dt > val_dtm.date():
        return val_dt
    if val_dtm.hour > roll_hour or (val_dtm.hour == roll_hour and val_dtm.minute >= roll_minute):
        return Tenor(('1B', calendar)).get_date(val_dt)
    return val_dtm.date()

