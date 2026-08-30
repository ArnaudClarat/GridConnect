from datetime import datetime
from enum import Enum
from dataclasses import dataclass
from typing import Optional


class RegisterType(str, Enum):
    CONSUMPTION_PEAK = "CONSUMPTION_PEAK"        # Heures pleines (+A)
    CONSUMPTION_OFFPEAK = "CONSUMPTION_OFFPEAK"  # Heures creuses (+A)
    PRODUCTION_PEAK = "PRODUCTION_PEAK"          # Injection heures pleines (-A)
    PRODUCTION_OFFPEAK = "PRODUCTION_OFFPEAK"    # Injection heures creuses (-A)
    TOTAL_CONSUMPTION = "TOTAL_CONSUMPTION"      # Registre unique consommation
    TOTAL_PRODUCTION = "TOTAL_PRODUCTION"        # Registre unique production


@dataclass(frozen=True)
class Measure:
    ean: str
    timestamp: datetime
    register: RegisterType
    value_kwh: float
    is_anomaly: bool = False
    anomaly_reason: Optional[str] = None

    @property
    def power_kw(self) -> float:
        """Calcule la puissance moyenne équivalente sur l'intervalle 15-min."""
        return self.value_kwh * 4.0

    def mark_as_anomaly(self, reason: str) -> "Measure":
        """Retourne une nouvelle instance de Measure marquée comme anomalie."""
        return Measure(
            ean=self.ean,
            timestamp=self.timestamp,
            register=self.register,
            value_kwh=self.value_kwh,
            is_anomaly=True,
            anomaly_reason=reason
        )