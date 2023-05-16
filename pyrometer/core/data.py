from dataclasses import dataclass, field

import numpy as np
import matplotlib.pyplot as plt

from pyspectrum import Spectrum

from spectrumlab.alias import Array, kelvin, nano, TemperatureUnits
from spectrumlab.utils import find

C1 = 37417  # in W * mkm**4 / cm**2
C2 = 14388  # in mkm * K


@dataclass
class Wien:
    x: Array
    y: Array
    exposure: float

    @classmethod
    def from_spectrum(cls, spectrum: Spectrum) -> 'Wien':
        w = spectrum.wavelength / 1000

        return cls(
            x=C2/w,
            y=4*np.log(w) + np.log(spectrum.intensity),
            exposure=spectrum.exposure,
        )

    def __sub__(self, other):
        cls = self.__class__

        if isinstance(other, Wien):
            return cls(
                x=self.x,
                y=self.y - other.y,
                exposure=self.exposure,
            )

        return cls(
            x=self.x,
            y=self.y - other,
            exposure=self.exposure,
        )

    def __getitem__(self, index: slice | Array) -> 'Wien':
        cls = self.__class__

        if isinstance(index, int | slice):
            number = index

            return cls(
                x=self.x[number],
                y=self.y[:, number],
                exposure=self.exposure,
            )

        raise TypeError


    # --------        handlers        --------
    def show(self):
        raise NotImplementedError  # TODO:


class Calibration:

    def __init__(self, spectrum: Spectrum, T: kelvin) -> None:
        if spectrum.n_times > 1:
            spectrum = spectrum.mean()

        self._wien = Wien.from_spectrum(spectrum)
        self._T = T
        self._values = self._get()

    def _get(self) -> Array:
        T = self._T
        x = self._wien.x
        y = self._wien.y

        p = [-1/T, np.mean(y) - np.mean(-x/T)]
        
        return y - np.polyval(p, x)

    @classmethod
    def load(cls, path: str, T: kelvin) -> 'Calibration':
        return cls(
            spectrum=Spectrum.load(path),
            T=T,
        )

    def get(self, bounds: tuple[int, int] | None = None) -> Array:
        if bounds is None:
            return self._values

        lb, ub = bounds
        return self._values[lb:ub]


@dataclass
class Temperature:
    spectrum: Spectrum
    calibration: Calibration

    units: TemperatureUnits = field(default=TemperatureUnits.celsius)
    _wien: Array | None = field(default=None, init=False)

    @property
    def n_times(self) -> Array:
        return self.spectrum.n_times

    @property
    def time(self) -> Array:
        return self.spectrum.time

    def __post_init__(self):
        self._wien = Wien.from_spectrum(self.spectrum)

    def _get_bounds(self, wavelength_range) -> tuple[int, int]:
        wavelength = self.spectrum.wavelength
        lr, ur = wavelength_range
        cond = (lr <= wavelength) & (wavelength <= ur)

        return min(find(cond)), max(find(cond))

    def calcualte(self, wavelength_range: tuple[nano, nano], show: bool = False) -> 'TemperatureData':
        lb, ub = bounds = self._get_bounds(wavelength_range)

        #
        data = self._wien[lb:ub] - self.calibration.get(bounds=(lb, ub))

        p = np.array([
            np.polyfit(data.x, data.y[t,:], deg=1).tolist()
            for t in self.time
        ])
        values = -1/p[:,0]
        dvalues = np.full((self.n_times,), np.nan)

        #
        return TemperatureData(
            temperature=self,
            bounds=bounds,
            p=p,
            values=values,
            dvalues=dvalues,
        )


@dataclass
class TemperatureData:
    temperature: Temperature

    bounds: tuple[int, int]
    p: Array
    values: Array[kelvin]
    dvalues: Array[kelvin]

    _wien: Array | None = field(default=None)

    @property
    def time(self) -> float:
        return self.temperature.time

    @property
    def exposure(self) -> float:
        return self.temperature.spectrum.exposure

    @property
    def units(self) -> float:
        return self.temperature.units

    @property
    def spectrum(self) -> Array:
        return self.temperature.spectrum

    @property
    def wien(self) -> Array:
        if self._wien is None:
            self._wien = self.temperature._wien - self.temperature.calibration.get()

        return self._wien

    def show(self):

        values = self.values
        if self.units == TemperatureUnits.celsius:
            values -= 273.15

        #
        fig, (ax_left, ax_right) = plt.subplots(nrows=1, ncols=2, figsize=(12, 4), tight_layout=True)

        x, y = self.time, self.values
        ax_left.plot(
            x, y,
            color='black', linestyle='-',
        )
        ax_left.set_xlabel(r'$\it{count}$')
        ax_left.set_ylabel(fr'$t, ^{{\circ}}{self.units.value}$')

        plt.show()

    def show_frame(self, t: int):
        spectrum = self.spectrum
        wien = self.wien

        lb, ub = self.bounds

        #
        fig, (ax_left, ax_right) = plt.subplots(nrows=1, ncols=2, figsize=(12, 4), tight_layout=True)

        x, y = spectrum.wavelength, spectrum.intensity[t,:]
        ax_left.plot(
            x, y,
            color='black', linestyle='-', linewidth=.5,
        )
        ax_left.axvspan(
            spectrum.wavelength[lb], spectrum.wavelength[ub],
            alpha=.1,
        )
        ax_left.set_xlabel(r'$\lambda, nm$')
        ax_left.set_ylabel(r'$I, e^{-}$')

        plt.show()
        fig, (ax_left, ax_right) = plt.subplots(nrows=1, ncols=2, figsize=(12, 4), tight_layout=True)

        x, y = wien.x, wien.y[t,:]
        ax_left.plot(
            x, y,
            color='black', linestyle='-', linewidth=.5,
        )
        x, y = wien.x, np.polyval(self.p[t], wien.x)
        ax_left.plot(
            x, y,
            color='red', linestyle='-', linewidth=.5,
        )
        ax_left.axvspan(
            wien.x[lb], wien.x[ub],
            alpha=.1,
        )
        content = [
            fr'T: {self.values[t]:.2f}, $^{{\circ}}{self.units.value}$',
        ]
        ax_left.text(
            1-0.05/2, 0.95,
            '\n'.join(content),
            transform=ax_left.transAxes,
            ha='right', va='top',
        )
        ax_left.set_xlabel(r'$C_{2}/\lambda_{i}, ^{\circ}K$')
        ax_left.set_ylabel(r'$\ln(\lambda_{i}^{4} \cdot N_{i})$')

        error = wien.y[t,:] - np.polyval(self.p[t, :], wien.x)
        x, y = wien.x, error
        ax_right.plot(
            x, y,
            color='red', linestyle='none', marker='.', markersize=2,
        )
        ax_right.axvspan(
            wien.x[lb], wien.x[ub],
            alpha=.1,
        )
        # ax_right.set_xlim([wien.x[lb], wien.x[ub]])
        r_error = max(error[lb:ub]) - min(error[lb:ub])
        ax_right.set_ylim([min(error[lb:ub]) - r_error, max(error[lb:ub]) + r_error])
        ax_right.set_xlabel(r'$C_{2}/\lambda_{i}, ^{\circ}K$')
        ax_right.set_ylabel(r'$\ln(\lambda_{i}^{4} \cdot N_{i})$')

        plt.show()

