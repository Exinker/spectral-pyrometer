
import numpy as np
import matplotlib.pyplot as plt

from pyspectrum import Spectrum
from spectrumlab.alias import Array, TemperatureUnits

from .wien import Wien


class Temperature:

    def __init__(self, spectrum: Spectrum, wien: Wien, bounds: tuple[int, int], units: TemperatureUnits) -> None:

        self.spectrum = spectrum
        self.wien = wien
        self.bounds = bounds
        self.units = units

        # temperature
        lb, ub = bounds
        data = wien[lb:ub]

        self._p = np.array([
            self._polyfit(data.x, data.y[t,:])
            for t in data.time
        ])

        self._values = -1/self._p[:,0]
        self._deviation = np.full((data.n_times,), np.nan)  # FIXME: !

    def _polyfit(self, x: Array, y: Array) -> tuple[float, float]:
        mask = np.isfinite(y)

        return tuple(np.polyfit(x[mask], y[mask], deg=1))

    @property
    def time(self) -> Array:
        return self.wien.time

    @property
    def values(self) -> Array:
        if self.units == TemperatureUnits.celsius:
            return self._values - 273.15

        return self._values

    # --------        handlers        --------
    def show(self, tail: int = 50, xlim: tuple[int, int] | None = None, ylim: tuple[int, int] | None = None):

        #
        fig, (ax_left, ax_right) = plt.subplots(nrows=1, ncols=2, figsize=(12, 4), tight_layout=True)

        x, y = self.time, self.values
        ax_left.plot(
            x, y,
            color='black', linestyle='-',
        )
        y = np.nanmean(self.values[-tail:])
        ax_left.axhline(
            y,
            color='red', linestyle='--', linewidth=1,
        )
        content = [
            fr'T: {y:.2f}, $^{{\circ}}{self.units.value}$',
        ]
        ax_left.text(
            1-0.05/2, 0.05,
            '\n'.join(content),
            transform=ax_left.transAxes,
            ha='right', va='bottom',
        )

        if xlim:
            ax_left.set_xlim(xlim)
        if ylim:
            ax_left.set_ylim(ylim)

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
        x, y = wien.x, np.polyval(self._p[t], wien.x)
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

        error = wien.y[t,:] - np.polyval(self._p[t, :], wien.x)
        x, y = wien.x, error
        ax_right.plot(
            x, y,
            color='red', linestyle='none', marker='.', markersize=2,
        )
        ax_right.axvspan(
            wien.x[lb], wien.x[ub],
            alpha=.1,
        )

        r_error = max(error[lb:ub]) - min(error[lb:ub])
        ylim = [min(error[lb:ub]) - r_error, max(error[lb:ub]) + r_error]
        if np.all(np.isfinite(ylim)):
            ax_right.set_ylim(ylim)

        ax_right.set_xlabel(r'$C_{2}/\lambda_{i}, ^{\circ}K$')
        ax_right.set_ylabel(r'$\ln(\lambda_{i}^{4} \cdot N_{i})$')

        plt.show()
