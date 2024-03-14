
from pydantic.dataclasses import dataclass
from dataclasses import InitVar
from typing import ClassVar
import numpy as np
from scipy import interpolate
import bisect


@dataclass
class Interpolator():
    _xy_init: InitVar[list[tuple[float, float]]]
    _xs: ClassVar[list[float]]
    _ys: ClassVar[list[float]]

    def __post_init__(self, xy_init):
        self._xs, self._ys = zip(*xy_init)

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
        elif type == 'LogCubicSplineFree':
            return LogCubicSplineFree
        else:
            raise Exception(f"{type} not supported yet")

    def _get_value(self, x: float):
        assert x >= self._xs[0], f"Cannot interpolate {x} before start {self._xs[0]}"

    def get_value(self, _: float):
        raise Exception("Abstract function")


@dataclass
class Step(Interpolator):

    def __post_init__(self, xy_init):
        super().__post_init__(xy_init)
    
    def get_value(self, x: float) -> float:
        super()._get_value(x)

        if x in self._xs:
            return self._ys[self._xs.index(x)]
        ih = bisect.bisect_left(self._xs, x)
        return self._ys[ih-1]


@dataclass
class LogLinear(Interpolator):
    log_ys: ClassVar[list[float]] = None

    def __post_init__(self, xy_init):
        self.update(xy_init)

    def update(self, xy_init):
        super().__post_init__(xy_init)
        self.log_ys = [np.log(y) for y in self._ys]
    
    def get_value(self, x: float) -> float:
        super()._get_value(x)

        if x in self._xs:
            return self._ys[self._xs.index(x)]
        elif x > self._xs[-1]:
            slope = (self.log_ys[-1] - self.log_ys[-2]) / (self._xs[-1] - self._xs[-2])
            return self._ys[-1] * np.exp((x-self._xs[-1]) * slope)
        ih = bisect.bisect_left(self._xs, x)
        slope = (self.log_ys[ih] - self.log_ys[ih-1]) / (self._xs[ih] - self._xs[ih-1])
        return self._ys[ih-1] * np.exp((x - self._xs[ih-1]) * slope)


# Cubic spline with free ends
@dataclass
class LogCubicSplineFree(Interpolator):
    log_ys: ClassVar[list[float]] = None

    def __post_init__(self, xy_init):
        super().__post_init__(xy_init)
        self.log_ys = [np.log(y) for y in self._ys]
        self.spline_tck = interpolate.splrep(self._xs, self.log_ys)

    def get_value(self, x: float) -> float:
        super()._get_value(x)
        return np.exp(interpolate.splev(x, self.spline_tck))


# Natural Cubic spline with f''(x) = 0 at both ends
@dataclass
class CubicSplineNatural(Interpolator):

    def __post_init__(self, xy_init):
        super().__post_init__(xy_init)
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

