
from pydantic.dataclasses import dataclass
import datetime as dtm

from common.models.base_instrument import BaseInstrumentP

@dataclass
class Future(BaseInstrumentP):
    _underlying: BaseInstrumentP
    _expiry: dtm.date
    _settle: dtm.date
    
    @property
    def underlying(self) -> str:
        return self._underlying
    
    @property
    def expiry(self):
        return self._expiry
    
    @property
    def settle_date(self):
        return self._settle
    
    def set_market(self, date: dtm.date, price: float) -> None:
        assert date <= self.expiry, "Value date cannot be after expiry"
        super().set_market(date, price)
