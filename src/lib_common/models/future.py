from pydantic.dataclasses import dataclass
from dataclasses import field
import datetime as dtm
from typing import Self

from lib_common.models.base_instrument import BaseInstrument

@dataclass
class Future(BaseInstrument):
    underlying: BaseInstrument
    expiry: dtm.date
    lot_size: int = field(kw_only=True, default=1)
    
    def __lt__(self, other: Self) -> bool:
        return self.expiry < other.expiry
