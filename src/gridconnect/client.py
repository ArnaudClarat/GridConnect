import requests
from datetime import datetime
from typing import List, Dict, Any
from gridconnect.models import Measure, RegisterType
from gridconnect.auth.session import OresSession


class OresApiClient:
    BASE_URL = "https://maconso.myores.be/app"

    def __init__(self, session: OresSession):
        if not session.site_id or not session.source_id:
            raise ValueError("La session ne contient pas les identifiants site_id et source_id.")
        
        self.session_data = session
        self.http_session = requests.Session()
        self.http_session.cookies.set("ores-prod-auth", session.auth_cookie)

    def fetch_measures(self, start_date: datetime, end_date: datetime) -> List[Measure]:
        url = f"{self.BASE_URL}/sites/{self.session_data.site_id}/sources/{self.session_data.source_id}/charts/render"
        
        payload = {
            "chartId": "CONSO_HILO",
            "granularityId": "HOUR",
            "from": start_date.strftime("%Y-%m-%dT%H:%M:%S.000Z"),
            "to": end_date.strftime("%Y-%m-%dT%H:%M:%S.999Z"),
        }

        response = self.http_session.post(url, json=payload, timeout=15)
        response.raise_for_status()

        return [m.check_validity() for m in self._parse_api_response(response.json())]

    def _parse_api_response(self, raw_json: Dict[str, Any]) -> List[Measure]:
        measures: List[Measure] = []

        for series in raw_json.get("series", []):
            data = series.get("data", [])
            if not data:
                continue

            interval_minutes = 15  # Fallback par défaut
            if len(data) >= 2:
                t1 = datetime.fromisoformat(data[0]["date"])
                t2 = datetime.fromisoformat(data[1]["date"])
                interval_minutes = int(abs((t2 - t1).total_seconds()) / 60.0)

            legend_text = series.get("legend", {}).get("text", "")
            is_injection = series.get("isInjectionSeries", False)
            register = self._map_series_to_register(legend_text, is_injection)

            for item in series.get("data", []):
                val = item.get("value")
                dt_str = item.get("date")
                if val is None or not dt_str:
                    continue

                dt = datetime.fromisoformat(dt_str)
                measures.append(
                    Measure(
                        timestamp=dt,
                        register=register,
                        volume_kwh=float(val),
                        interval_minutes=interval_minutes,
                    )
                )

        return measures

    @staticmethod
    def _map_series_to_register(legend_text: str, is_injection: bool) -> RegisterType:
        if "Consumption Peak" in legend_text:
            return RegisterType.CONSUMPTION_PEAK
        if "Consumption Off Peak" in legend_text:
            return RegisterType.CONSUMPTION_OFFPEAK
        if is_injection and "Peak" in legend_text:
            return RegisterType.PRODUCTION_PEAK
        if is_injection:
            return RegisterType.PRODUCTION_OFFPEAK
        return RegisterType.TOTAL_CONSUMPTION