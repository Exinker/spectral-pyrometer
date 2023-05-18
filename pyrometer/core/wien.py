
from dataclasses import dataclass

import numpy as np

from pyspectrum import Spectrum
from spectrumlab.alias import Array

from .config import C2


@dataclass
class Wien:
    x: Array
    y: Array
    exposure: float

    @property
    def shape(self) -> tuple[int, int]:
        return self.y.shape

    @property
    def n_times(self) -> int:
        return self.shape[0]

    @property
    def time(self) -> Array:
        return np.arange(self.n_times)

    @property
    def n_numbers(self) -> int:
        return self.shape[1]

    @property
    def number(self) -> Array:
        return np.arange(self.n_numbers)

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

    # --------        classmethod        --------
    @classmethod
    def from_spectrum(cls, spectrum: Spectrum) -> 'Wien':
        wavelength = spectrum.wavelength / 1000  # convert `nano` to `micro`  # FIXME: change C1, C2!

        x = C2/wavelength
        y = 4*np.log(wavelength) + np.log(spectrum.intensity)

        return cls(
            x=x,
            y=y,
            exposure=spectrum.exposure,
        )
