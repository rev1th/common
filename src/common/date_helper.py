import datetime as dtm

from common.chrono.badjust import BDayAdjustType, get_adjusted_date
from common.chrono.calendar import CalendarID
from common.chrono.tenor import Tenor

# Return all business dates
def get_bdate_series(from_date: dtm.date, to_date: dtm.date, calendar: CalendarID | str = None) -> list[dtm.date]:
    from_date_adj = get_adjusted_date(BDayAdjustType.Following, from_date, calendar=calendar)
    return Tenor.bday(1, calendar=calendar).generate_series(from_date_adj, to_date, inclusive=True)

# Returns last business date
def get_last_business_date(calendar: CalendarID | str = None, roll_time: dtm.time = None) -> dtm.date:
    val_dtm = dtm.datetime.now(roll_time.tzinfo if roll_time else None)
    val_dt = get_adjusted_date(BDayAdjustType.Preceding, val_dtm.date(), calendar=calendar)
    if val_dt < val_dtm.date():
        return val_dt
    if roll_time and val_dtm.time() < roll_time:
        return Tenor.bday(-1, calendar).get_date_simple(val_dt)
    return val_dtm.date()

# Returns current business date rolling forward on holiday
def get_current_business_date(calendar: CalendarID | str = None, roll_time: dtm.time = None) -> dtm.date:
    val_dtm = dtm.datetime.now(roll_time.tzinfo if roll_time else None)
    val_dt = get_adjusted_date(BDayAdjustType.Following, val_dtm.date(), calendar=calendar)
    if val_dt > val_dtm.date():
        return val_dt
    if roll_time and val_dtm.time() >= roll_time:
        return Tenor.bday(1, calendar).get_date_simple(val_dt)
    return val_dtm.date()
