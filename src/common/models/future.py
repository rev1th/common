from pydantic.dataclasses import dataclass
from dataclasses import field
import datetime as dtm
from typing import Self

from common.models.base_instrument import BaseInstrument

@dataclass
class Future(BaseInstrument):
    _underlying: BaseInstrument
    _expiry: dtm.date
    _lot_size: int = field(kw_only=True, default=1)
    
    @property
    def underlying(self):
        return self._underlying
    
    @property
    def expiry(self):
        return self._expiry
    
    @property
    def lot_size(self):
        return self._lot_size
    
    def __lt__(self, other: Self) -> bool:
        return self._expiry < other._expiry
