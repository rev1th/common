from enum import StrEnum
from typing import Optional
import holidays
import numpy as np

class CalendarID(StrEnum):
    USD = 'US'
    USEX = 'XNYS'
    USNY = 'US:NY'
    CNY = 'CN'
    HKD = 'HK'

class CalendarContext(object):
    _years = range(2022, 2030)
    _bdc_map: dict[str, np.busdaycalendar] = {}

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(CalendarContext, cls).__new__(cls)
        return cls.instance
        
    def set_bdc(self, calendar: str):
        calendar_list = calendar.split('+')
        if len(calendar_list) > 1:
            hols = np.concatenate([self.get_bdc(c).holidays for c in calendar_list])
        else:
            subcals = calendar.split(':')
            if len(subcals) > 1:
                assert len(subcals) == 2, f'Unrecognized {calendar}'
                hols = list(holidays.country_holidays(subcals[0], subdiv=subcals[1], years = self._years).keys())
            else:
                hols = list(holidays.country_holidays(subcals[0], years = self._years).keys())
        self._bdc_map[calendar] = np.busdaycalendar(holidays=hols)
    
    def get_bdc(self, calendar: Optional[CalendarID | str]) -> Optional[np.busdaycalendar]:
        if not calendar:
            return None
        elif isinstance(calendar, CalendarID):
            return self.get_bdc(calendar.value)
        elif calendar not in self._bdc_map:
            self.set_bdc(calendar)
        return self._bdc_map[calendar]
    
    def get_holidays(self, calendar: str) -> list:
        return self.get_bdc(calendar).holidays
