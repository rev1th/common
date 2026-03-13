from enum import StrEnum
import datetime as dtm
import numpy as np

from .calendar import CalendarContext

def is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

class DayCount(StrEnum):
    
    ACT360 = 'ACT360'
    ACT365 = 'ACT365'
    ACTACT = 'ACTACT'
    ACTACTISDA = 'ACTACTISDA'
    _30360 = '30360'
    _30E360 = '30E360'
    # ACTACTISMA = 'ACTACTISMA'
    BD252 = 'BD252'

    def get_dcf(self, from_date: dtm.date, to_date: dtm.date, calendar: str = None) -> float:
        match self:
            case DayCount.ACT360:
                return (to_date-from_date).days/360.0
            case DayCount.ACT365:
                return (to_date-from_date).days/365.0
            case DayCount.BD252:
                return np.busday_count(from_date, to_date, busdaycal=CalendarContext().get_bdc(calendar)) / 252.0
            case DayCount.ACTACT:
                if (from_date.month > to_date.month) or (from_date.month == to_date.month and from_date.day > to_date.day):
                    from_date_to = dtm.date(from_date.year+1, to_date.month, to_date.day)
                    dcf = to_date.year-from_date.year-1
                else:
                    from_date_to = dtm.date(from_date.year, to_date.month, to_date.day)
                    dcf = to_date.year-from_date.year
                days_in_year = 365
                if is_leap(from_date.year):
                    if from_date < dtm.date(from_date.year, 2, 29) <= from_date_to:
                        days_in_year += 1
                dcf += (from_date_to-from_date).days / days_in_year
                return dcf
            case DayCount.ACTACTISDA:
                if to_date.year > from_date.year:
                    from_date_to = dtm.date(from_date.year+1, 1, 1)
                    dcf = (from_date_to-from_date).days / (365+is_leap(from_date.year))
                    dcf += to_date.year-from_date.year-1
                    to_date_from = dtm.date(to_date.year, 1, 1)
                    dcf += (to_date-to_date_from).days / (365+is_leap(to_date.year))
                    return dcf
                else:
                    return (to_date-from_date).days / (365+is_leap(to_date.year))
            case DayCount._30360:
                from_day = 30 if from_date.day == 31 else from_date.day
                to_day = 30 if to_date.day == 31 and from_date.day in (30, 31) else to_date.day
                return (to_date.year-from_date.year) + (to_date.month-from_date.month)/12 + (to_day-from_day)/360
            case DayCount._30E360:
                from_day = 30 if from_date.day == 31 else from_date.day
                to_day = 30 if to_date.day == 31 else to_date.day
                return (to_date.year-from_date.year) + (to_date.month-from_date.month)/12 + (to_day-from_day)/360
            case _:
                raise ValueError(f'{self.value} not recognized for day count fraction')
    
    def get_unit_dcf(self) -> float:
        match self:
            case DayCount.ACT360:
                return 1/360.0
            case DayCount.ACT365:
                return 1/365.0
            case DayCount.BD252:
                return 1/252
            case DayCount._30360 | DayCount._30E360:
                return 1/360.0
            case _:
                raise NotImplementedError(f'{self.value} not recognized for day count fraction unit')
