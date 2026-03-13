from pydantic.dataclasses import dataclass
from dataclasses import field, KW_ONLY
import datetime as dtm

from lib_common.base_class import NameClass
from lib_common.currency import Currency
from lib_common.chrono.calendar import CalendarID
from lib_common.models.data_series import DataSeries

# No validators for non-default classes like SortedDict, pandas.DataFrame
# https://docs.pydantic.dev/latest/usage/model_config/#arbitrary-types-allowed
@dataclass(config=dict(arbitrary_types_allowed = True))
class BaseInstrument(NameClass):
    _: KW_ONLY
    data_id: str | None = None
    currency: Currency = Currency.USD
    calendar: CalendarID = CalendarID.USEX
    _data_series: DataSeries[dtm.date, float] = field(init=False, default_factory=DataSeries)
    
    @property
    def data(self):
        return self._data_series
