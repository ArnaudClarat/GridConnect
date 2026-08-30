import json
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OresSession:
    auth_cookie: str
    created_at: datetime
    site_id: Optional[str] = None
    source_id: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "auth_cookie": self.auth_cookie,
            "created_at": self.created_at.isoformat(),
            "site_id": self.site_id,
            "source_id": self.source_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "OresSession":
        return cls(
            auth_cookie=data["auth_cookie"],
            created_at=datetime.fromisoformat(data["created_at"]),
            site_id=data.get("site_id"),
            source_id=data.get("source_id"),
        )


class SessionManager:
    def __init__(self, session_filepath: Path | str = "config/session.json"):
        self.session_filepath = Path(session_filepath)

    def save_session(self, session: OresSession) -> None:
        """Sauvegarde la session dans un fichier JSON sécurisé."""
        self.session_filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(self.session_filepath, "w", encoding="utf-8") as f:
            json.dump(session.to_dict(), f, indent=2)

    def load_session(self) -> Optional[OresSession]:
        """Charge la session courante si le fichier existe."""
        if not self.session_filepath.exists():
            return None
        try:
            with open(self.session_filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return OresSession.from_dict(data)
        except (json.JSONDecodeError, KeyError):
            return None