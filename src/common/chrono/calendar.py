
from enum import StrEnum
from typing import Union, Optional
import holidays
import numpy as np

_CACHED_BDC: dict[str, np.busdaycalendar] = {}
_YEARS = range(2022, 2030)


class Calendar(StrEnum):

    USD = 'US'
    USEX = 'XNYS'
    USNY = 'US:NY'
    CNY = 'CN'
    HKD = 'HK'


def get_bdc(calendar: Optional[Union[Calendar, str]]) -> Optional[np.busdaycalendar]:
    if not calendar:
        return None
    elif isinstance(calendar, Calendar):
        return get_bdc(calendar.value)
    if calendar not in _CACHED_BDC:
        subcals = calendar.split(':')
        if len(subcals) > 1:
            hols = list(holidays.country_holidays(subcals[0], subdiv=subcals[1], years = _YEARS).keys())
        else:
            hols = list(holidays.country_holidays(subcals[0], years = _YEARS).keys())
        _CACHED_BDC[calendar] = np.busdaycalendar(holidays=hols)
    return _CACHED_BDC[calendar]
