
from pydantic.dataclasses import dataclass
from dataclasses import field
import datetime as dtm


# Mixin/Traits
@dataclass()
class NameClass:
    name: str = field(kw_only=True, default=None)

    # @property
    # def name(self) -> str:
    #     return self._name

@dataclass()
class NameDateClass(NameClass):
    date: dtm.date

    # @property
    # def date(self) -> dtm.date:
    #     return self._date

