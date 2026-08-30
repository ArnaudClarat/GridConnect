from datetime import datetime
from dataclasses import dataclass

@dataclass(frozen=True)
class Measure:
    ean: str
    timestamp: datetime
    register: str
    value_kwh: float

    @property
    def power_kw(self) -> float:
        """Calcule la puissance moyenne équivalente sur l'intervalle 15-min."""
        return self.value_kwh * 4.0.