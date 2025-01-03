from pydantic.dataclasses import dataclass
from dataclasses import field, KW_ONLY
import datetime as dtm

from common.base_class import NameClass
from common.currency import Currency
from common.chrono import CalendarID
from common.models.data_series import DataSeries

# No validators for non-default classes like SortedDict, pandas.DataFrame
# https://docs.pydantic.dev/latest/usage/model_config/#arbitrary-types-allowed
@dataclass(config=dict(arbitrary_types_allowed = True))
class BaseInstrument(NameClass):
    _: KW_ONLY
    data_id: str | None = None
    _currency: Currency = Currency.USD
    _calendar: CalendarID = CalendarID.USEX
    _data_series: DataSeries[dtm.date, float] = field(init=False, default_factory=DataSeries)

    @property
    def currency(self):
        return self._currency
    
    @property
    def calendar(self):
        return self._calendar
    
    @property
    def data(self):
        return self._data_series
