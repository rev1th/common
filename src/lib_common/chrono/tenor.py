from pydantic.dataclasses import dataclass
import datetime as dtm
from pandas.tseries.offsets import DateOffset, MonthEnd, QuarterEnd, YearEnd, MonthBegin, CustomBusinessDay as CBDay

from .calendar import CalendarContext, CalendarID
from .badjust import BDayAdjust
from .roll import RollConvention


def parse_code(str_int: str) -> tuple[int, str]:
    """Separates alphabet characters at the end of the string from the integer prefix."""
    assert len(str_int) >= 2, ValueError(f'Invalid input {str_int}')
    ci = len(str_int) - 1
    while ci >= 0 and str_int[ci].isalpha():
        ci -= 1
    return int(str_int[:ci+1]), str_int[ci+1:]

def is_eom(date: dtm.date, calendar: CalendarID | str | None):
    next_day = Tenor.bday(1, calendar).get_date_simple(date)
    return next_day.month != date.month

def load_tenor(arg: str | tuple[str, str]):
    if isinstance(arg, tuple):
        assert len(arg) == 2, ValueError(f'Expect tuple of size 2 {arg}')
        full_code = arg[0]
        bdc = CalendarContext().get_bdc(arg[1])
    else:
        full_code, bdc = arg, None
    num, code = parse_code(full_code)
    match code.lower():
        case 'b':
            return CBDay(n=num, calendar=bdc)
        case 'y':
            return DateOffset(years=num)
        case 'm':
            # rolls back to month end e.g. 31-Jan-2024 + 1m = 29-Feb-2024
            return DateOffset(months=num)
        case 'w':
            return DateOffset(weeks=num)
        case 'd':
            return DateOffset(days=num)
        case 'mb':
            return MonthBegin(n=num)
        case 'me':
            return MonthEnd(n=num)
        case 'qe':
            return QuarterEnd(n=num)
        case 'ye':
            return YearEnd(n=num)
        case _:
            raise RuntimeError(f'Cannot parse tenor {code}')


@dataclass(config=dict(arbitrary_types_allowed = True))
class Tenor:
    code: str | tuple[str, str]
    _offsets: list[DateOffset | CBDay] = None
    
    def __post_init__(self):
        if not self._offsets:
            self._offsets = [load_tenor(self.code)]
    
    def __add__(self, new):
        return Tenor(f"{self.code}+{new.code}", self._offsets + new._offsets)
    
    @classmethod
    def bday(cls, n: int = 0, calendar: CalendarID | str = None):
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
        if roll_convention.is_eom() and not (self.is_monthly() and is_eom(date, bd_adjust.calendar)):
            return RollConvention()
        return roll_convention
    
    def get_date_rolled(self, date: dtm.date, roll_convention_v: RollConvention, bd_adjust = BDayAdjust()):
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

