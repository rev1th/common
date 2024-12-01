
from pydantic.dataclasses import dataclass
from dataclasses import InitVar, field
from typing import ClassVar
import numpy as np
from scipy import interpolate
import bisect


@dataclass
class Interpolator:
    _xy_init: InitVar[list[tuple[float, float]]]
    _extrapolate_left: bool = field(kw_only=True, default=False)
    
    _xs: ClassVar[list[float]]
    _ys: ClassVar[list[float]]

    def __post_init__(self, xy_init):
        self._xs, self._ys = zip(*xy_init)

    def update(self, xy_init):
        self.__post_init__(xy_init)
    
    @property
    def size(self):
        return len(self._xs)
    
    @classmethod
    def fromString(cls, type: str):
        if type in ('LogCubic', 'LogCubicSplineNatural'):
            return LogCubicSplineNatural
        elif type == 'Step':
            return Step
        elif type == 'LogLinear':
            return LogLinear
        elif type == 'LogBSpline':
            return LogBSpline
        else:
            raise ValueError(f"{type} not supported yet")

    def _get_value(self, x: float):
        if not self._extrapolate_left:
            assert x >= self._xs[0], f"Cannot interpolate {x} before start {self._xs[0]}"

    def get_value(self, _: float):
        raise NotImplementedError("Abstract function")


@dataclass
class Step(Interpolator):

    def get_value(self, x: float) -> float:
        super()._get_value(x)
        ih = bisect.bisect(self._xs, x)
        return self._ys[ih-1]


@dataclass
class Linear(Interpolator):
    
    def get_value(self, x: float) -> float:
        super()._get_value(x)

        if x > self._xs[-1]:
            slope = (self._ys[-1] - self._ys[-2]) / (self._xs[-1] - self._xs[-2])
            return self._ys[-1] + slope * (x-self._xs[-1])
        ih = bisect.bisect_left(self._xs, x)
        if x == self._xs[ih]:
            return self._ys[ih]
        slope = (self._ys[ih] - self._ys[ih-1]) / (self._xs[ih] - self._xs[ih-1])
        return self._ys[ih-1] + slope * (x - self._xs[ih-1])


@dataclass
class LogLinear(Linear):

    def __post_init__(self, xy_init):
        xly_init = [(x, np.log(y)) for x, y in xy_init]
        super().__post_init__(xly_init)
    
    def get_value(self, x: float) -> float:
        return np.exp(super().get_value(x))


# Cubic spline with free ends
@dataclass
class BSpline(Interpolator):

    def __post_init__(self, xy_init):
        super().__post_init__(xy_init)
        assert len(self._ys) > 3, 'require more than 3 coordinates for B-spline'
        self.spline_tck = interpolate.splrep(self._xs, self._ys)

    def get_value(self, x: float) -> float:
        super()._get_value(x)
        return interpolate.splev(x, self.spline_tck)

@dataclass
class LogBSpline(Interpolator):

    def __post_init__(self, xy_init):
        xly_init = [(x, np.log(y)) for x, y in xy_init]
        super().__post_init__(xly_init)

    def get_value(self, x: float) -> float:
        return np.exp(super().get_value(x))

# Natural Cubic spline with f''(x) = 0 at both ends
@dataclass
class CubicSplineNatural(Interpolator):

    def __post_init__(self, xy_init):
        super().__post_init__(xy_init)
        assert len(xy_init) > 3, 'require more than 3 coordinates for spline'
        self.spline_tck = interpolate.make_interp_spline(
                            self._xs, self._ys,
                            bc_type=([(2, 0.0)], [(2, 0.0)]))

    def get_value(self, x: float) -> float:
        super()._get_value(x)
        return interpolate.splev(x, self.spline_tck)

# Standard for curve construction
@dataclass
class LogCubicSplineNatural(CubicSplineNatural):

    def __post_init__(self, xy_init):
        xly_init = [(x, np.log(y)) for x, y in xy_init]
        super().__post_init__(xly_init)

    def get_value(self, x: float) -> float:
        return np.exp(super().get_value(x))

