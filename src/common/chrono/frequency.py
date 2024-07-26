
from enum import StrEnum
from typing import Union
import datetime as dtm
import numpy as np

from .tenor import Tenor, BDayAdjust
from .roll import RollConvention

_UNIT_DCF = {
    'A': 1.0,
    'S': .5,
    'Q': .25,
    'M': 1/12.0,
    '4W': 1/13.0,
    'W': 1/52.0,
}

class Frequency(StrEnum):

    Annual = 'A'
    SemiAnnual = 'S'
    Quarterly = 'Q'
    Monthly = 'M'
    Weekly = 'W'

    def to_tenor(self, backward: bool = True) -> Tenor:
        match self.value:
            case 'A':
                return Tenor('-1y' if backward else '1y')
            case 'S':
                return Tenor('-6m' if backward else '6m')
            case 'Q':
                return Tenor('-3m' if backward else '3m')
            case 'M':
                return Tenor('-1m' if backward else '1m')
            case 'W' | '7D':
                return Tenor('-1w' if backward else '1w')
            case '4W' | '28D':
                return Tenor('-4w' if backward else '4w')
            case 'D' | 'B':
                return Tenor('-1b' if backward else '1b')
            case _:
                raise RuntimeError(f'Cannot parse frequency {self.value}')
    
    def get_unit_dcf(self) -> float:
        try:
            return _UNIT_DCF[self.value]
        except KeyError:
            raise RuntimeError(f'Invalid coupon frequency {self.value}')
    
    def generate_schedule(self, start: Union[dtm.date, Tenor], end: Union[dtm.date, Tenor],
                          ref_date: dtm.date = None,
                          bd_adjust = BDayAdjust(),
                          roll_convention = RollConvention(),
                          step_backward = True,
                          extended = False) -> list[dtm.date]:
        start_date = start if isinstance(start, dtm.date) else start.get_date(ref_date)
        end_date = end if isinstance(end, dtm.date) else end.get_date(start_date)

        return self.to_tenor(backward=step_backward).generate_series(
            start_date, end_date, roll_convention=roll_convention,
            step_backward=step_backward, bd_adjust=bd_adjust, extended=extended)


class Compounding(StrEnum):

    Annual = 'A'
    SemiAnnual = 'S'
    Quarterly = 'Q'
    Monthly = 'M'
    Daily = 'D'
    Continous = 'CON'
    Simple = 'SIM'

    def get_rate(self, df: float, dcf: float, dcf_unit: float = 0) -> float:
        match self.value:
            case 'CON':
                return -np.log(df) / dcf
            case 'SIM':
                return (1 / df - 1) / dcf
            case 'D':
                return (df ** (-dcf_unit / dcf) - 1) / dcf_unit
            case 'A' | 'S' | 'Q' | 'M':
                dcf_compound = _UNIT_DCF[self.value]
                return (df ** (-dcf_compound / dcf) - 1) / dcf_compound
            case _:
                raise RuntimeError(f'Cannot parse compounding {self.value}')

    def get_df(self, rate: float, dcf: float) -> float:
        match self.value:
            case 'CON':
                return np.exp(-rate * dcf)
            case 'SIM':
                return 1 / (1 + rate * dcf)
            case 'A' | 'S' | 'Q' | 'M':
                dcf_compound = _UNIT_DCF[self.value]
                return (1 + rate * dcf_compound) ** (-dcf / dcf_compound)
            case _:
                raise RuntimeError(f'Cannot parse compounding {self.value}')

