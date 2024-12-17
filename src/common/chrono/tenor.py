from pydantic.dataclasses import dataclass
from typing import Union, Iterable
import datetime as dtm
from pandas.tseries.offsets import DateOffset, MonthEnd, QuarterEnd, YearEnd, MonthBegin, CustomBusinessDay as CBDay

from .calendar import CalendarContext, CalendarID
from .badjust import BDayAdjust, BDayAdjustType, get_adjusted_date
from .roll import RollConvention


def str_to_int(str_int: str) -> int:
    if str_int.isdigit() or (str_int[0] == '-' and str_int[1:].isdigit()):
        return int(str_int)
    return None

def is_eom(date: dtm.date, calendar: CalendarID | str | None):
    next_day = Tenor.bday(1, calendar).get_date_simple(date)
    return next_day.month != date.month

def parseTenor(offset: Union[str, tuple[str, str]]) -> DateOffset:
    if isinstance(offset, tuple):
        assert len(offset) == 2, ValueError(f'Expect tuple of size 2 {offset}')
        code = offset[0]
        bdc = CalendarContext().get_bdc(offset[1])
    else:
        code, bdc = offset, None
    assert len(code) >= 2, ValueError(f'Invalid input {code}')
    if len(code) > 3:
        offset_int = str_to_int(code[:-3])
        match code[-3:].upper():
            case 'BOM'|'SOM':
                return MonthBegin(n=offset_int)
            case 'EOM':
                return MonthEnd(n=offset_int)
            case 'EOQ':
                return QuarterEnd(n=offset_int)
            case 'EOY':
                return YearEnd(n=offset_int)
    offset_int = str_to_int(code[:-1])
    match code[-1]:
        case 'B' | 'b':
            return CBDay(n=offset_int, calendar=bdc)
        case 'Y' | 'y':
            return DateOffset(years=offset_int)
        case 'M' | 'm':
            # rolls back to month end e.g. 31-Jan-2024 + 1m = 29-Feb-2024
            return DateOffset(months=offset_int)
        case 'W' | 'w':
            return DateOffset(weeks=offset_int)
        case 'D' | 'd':
            return DateOffset(days=offset_int)
        case _:
            raise RuntimeError(f'Cannot parse tenor {code}')


@dataclass(config=dict(arbitrary_types_allowed = True))
class Tenor:
    _code: Union[str, tuple[str, str]]
    _offsets: list[DateOffset] = None
    
    def __post_init__(self):
        if not self._offsets:
            self._offsets = [parseTenor(self._code)]
    
    def __add__(self, new):
        return Tenor(self._code, self._offsets + new._offsets)
    
    @classmethod
    def bday(cls, n: int = 0, calendar: Union[CalendarID, str] = None):
        return cls(f'{n}b', [CBDay(n=n, calendar=CalendarContext().get_bdc(calendar))])
    
    def is_monthly(self):
        for offset in self._offsets:
            if getattr(offset, 'months', 0) == 0 and getattr(offset, 'years', 0) == 0:
                return False
        return True
    
    def get_date_simple(self, date: dtm.date = None) -> dtm.date:
        res = date
        for offset in self._offsets:
            res = res + offset
        return res.date()
    
    def get_date(self, date: dtm.date = None, bd_adjust = BDayAdjust()) -> dtm.date:
        return bd_adjust.get_date(self.get_date_simple(date))
    
    def get_valid_roll(self, date: dtm.date, roll_convention: RollConvention, bd_adjust = BDayAdjust()):
        if roll_convention.is_eom() and not (self.is_monthly() and is_eom(date, bd_adjust._calendar)):
            return RollConvention()
        return roll_convention
    
    def get_rolled_date(self, date: dtm.date, roll_convention_v: RollConvention, bd_adjust = BDayAdjust()):
        roll_convention_v = self.get_valid_roll(date, roll_convention_v, bd_adjust)
        return bd_adjust.get_date(roll_convention_v.get_date(self.get_date_simple(date)))
    
    # Generates schedule with Tenor for [from_date, to_date]
    def generate_series(
            self, from_date: dtm.date, to_date: dtm.date,
            step_backward: bool = False, bd_adjust = BDayAdjust(),
            roll_convention = RollConvention(),
            extend_last: bool = False, inclusive: bool = False,
            ) -> list[dtm.date]:
        schedule = []
        if step_backward:
            roll_convention = self.get_valid_roll(to_date, roll_convention, bd_adjust)
            date_i = to_date
            while date_i > from_date:
                date_i_adj = bd_adjust.get_date(date_i)
                # ensure still within period after adjustment
                if date_i_adj > from_date:
                    schedule.append(date_i_adj)
                    date_i = roll_convention.get_date(self.get_date_simple(date_i))
                    # move prior to adjusted
                    while date_i >= date_i_adj:
                        date_i = self.get_date_simple(date_i)
                else:
                    break
            if extend_last or (inclusive and date_i >= from_date):
                # extend last step to at or below bound
                date_i_adj = bd_adjust.get_date(date_i)
                schedule.append(date_i_adj)
            schedule.reverse()
        else:
            roll_convention = self.get_valid_roll(from_date, roll_convention, bd_adjust)
            date_i = from_date
            while date_i < to_date:
                date_i_adj = bd_adjust.get_date(date_i)
                if date_i_adj < to_date:
                    schedule.append(date_i_adj)
                    date_i = roll_convention.get_date(self.get_date_simple(date_i))
                    while date_i <= date_i_adj:
                        date_i = self.get_date_simple(date_i)
                else:
                    break
            if extend_last or (inclusive and date_i <= to_date):
                date_i_adj = bd_adjust.get_date(date_i)
                schedule.append(date_i_adj)
        return schedule


# Return all business dates
def get_bdate_series(from_date: dtm.date, to_date: dtm.date, calendar: Union[CalendarID, str] = None) -> list[dtm.date]:
    from_date_adj = get_adjusted_date(BDayAdjustType.Following, from_date, calendar=calendar)
    return Tenor.bday(1, calendar=calendar).generate_series(from_date_adj, to_date, inclusive=True)

# Returns last business date
def get_last_business_date(calendar: Union[CalendarID, str] = None, roll_time: dtm.time = None) -> dtm.date:
    val_dtm = dtm.datetime.now(roll_time.tzinfo if roll_time else None)
    val_dt = get_adjusted_date(BDayAdjustType.Preceding, val_dtm.date(), calendar=calendar)
    if val_dt < val_dtm.date():
        return val_dt
    if roll_time and val_dtm.time() < roll_time:
        return Tenor.bday(-1, calendar).get_date_simple(val_dt)
    return val_dtm.date()

# Returns current business date rolling forward on holiday
def get_current_business_date(calendar: Union[CalendarID, str] = None, roll_time: dtm.time = None) -> dtm.date:
    val_dtm = dtm.datetime.now(roll_time.tzinfo if roll_time else None)
    val_dt = get_adjusted_date(BDayAdjustType.Following, val_dtm.date(), calendar=calendar)
    if val_dt > val_dtm.date():
        return val_dt
    if roll_time and val_dtm.time() >= roll_time:
        return Tenor.bday(1, calendar).get_date_simple(val_dt)
    return val_dtm.date()

