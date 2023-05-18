
from pyspectrum import Spectrum

from spectrumlab.alias import nano, TemperatureUnits
from spectrumlab.utils import find

from .calibration import Calibration
from .exceptions import NotFittedError
from .temperature import Temperature
from .wien import Wien


class Model:

    def __init__(self, units: TemperatureUnits = TemperatureUnits.celsius) -> None:
        self.units = units

        self.calibration = None
        self.wavelength_range = None

    def _get_bounds(self, spectrum:Spectrum, wavelength_range: tuple[nano, nano]) -> tuple[int, int]:
        lr, ur = wavelength_range
        index = find((lr <= spectrum.wavelength) & (spectrum.wavelength <= ur))

        return min(index), max(index)

    def _get_wien(self, spectrum: Spectrum) -> Wien:

        wien = Wien.from_spectrum(spectrum)
        wien -= self.calibration.values  # calibrate wien to device's response 

        return wien

    # --------        handlers        --------
    def fit(self, calibration: Calibration, wavelength_range: tuple[nano, nano]) -> 'Model':
        self.calibration = calibration
        self.wavelength_range = wavelength_range

        return self

    def predict(self, spectrum: Spectrum) -> Temperature:
        assert self.calibration is not None, NotFittedError.__doc__
        assert self.wavelength_range is not None, NotFittedError.__doc__

        # wien
        wien = self._get_wien(
            spectrum=spectrum,
        )

        # bounds
        bounds = self._get_bounds(
            spectrum=spectrum,
            wavelength_range=self.wavelength_range,
        )

        # temperature
        return Temperature(
            spectrum=spectrum,
            wien=wien,
            bounds=bounds,
            units=self.units,
        )
