from datetime import datetime
from enum import Enum
from dataclasses import dataclass, replace


class RegisterType(str, Enum):
    CONSUMPTION_PEAK = "CONSUMPTION_PEAK"        # Heures pleines (+A)
    CONSUMPTION_OFFPEAK = "CONSUMPTION_OFFPEAK"  # Heures creuses (+A)
    PRODUCTION_PEAK = "PRODUCTION_PEAK"          # Injection heures pleines (-A)
    PRODUCTION_OFFPEAK = "PRODUCTION_OFFPEAK"    # Injection heures creuses (-A)
    TOTAL_CONSUMPTION = "TOTAL_CONSUMPTION"      # Registre unique consommation
    TOTAL_PRODUCTION = "TOTAL_PRODUCTION"        # Registre unique production


@dataclass(frozen=True)
class Measure:
    timestamp: datetime
    register: RegisterType
    volume_kwh: float
    interval_minutes: int = 15
    is_valid: bool = True

    @property
    def power_kw(self) -> float:
        """Calcule la puissance moyenne équivalente sur l'intervalle."""
        return round(self.volume_kwh / (self.interval_minutes / 60.0), 3) if self.interval_minutes > 0 else 0.0

    def check_validity(self) -> "Measure":
        """Invalide la mesure si négative ou physiquement impossible."""
        valid = 0.0 <= self.power_kw <= 30.0
        return self if self.is_valid == valid else replace(self, is_valid=valid)