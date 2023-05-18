
import numpy as np

from pyspectrum import Spectrum
from spectrumlab.alias import Array, kelvin

from .wien import Wien


class Calibration:

    def __init__(self, spectrum: Spectrum, T: kelvin) -> None:
        self.T = T
        self.values = self._get_values(spectrum)

    def _get_values(self, spectrum: Spectrum) -> Array:
        T = self.T

        # wien
        if spectrum.n_times > 1:
            spectrum = spectrum.mean()

        wien = Wien.from_spectrum(spectrum)

        # values
        p = [-1/T, np.mean(wien.y) - np.mean(-(wien.x/T))]
        values = (wien.y - np.polyval(p, wien.x)).reshape(-1,)

        return values

    # --------        classmethod        --------
    @classmethod
    def load(cls, path: str, T: kelvin) -> 'Calibration':
        return cls(
            spectrum=Spectrum.load(path),
            T=T,
        )
