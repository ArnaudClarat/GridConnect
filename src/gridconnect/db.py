import os, psycopg2
from psycopg2.extras import execute_values
from typing import List, Optional
from gridconnect.models import Measure

class DBStore:
    _instance: Optional["DBStore"] = None

    def __new__(cls, db_config: Optional[dict] = None):
        if cls._instance is None:
            if db_config is None:
                db_config = {
                    "host": os.getenv("DB_HOST", "localhost"),
                    "port": os.getenv("DB_PORT", "5432"),
                    "database": os.getenv("DB_NAME", "gridconnect"),
                    "user": os.getenv("DB_USER", "postgres"),
                    "password": os.getenv("DB_PASSWORD", "")
                }
            cls._instance = super(DBStore, cls).__new__(cls)
            cls._instance.db_config = db_config
        return cls._instance

    def _get_connection(self):
        return psycopg2.connect(**self.db_config)

    def save_measures(self, measures: List[Measure]) -> int:
        """
        Insère une liste de mesures de manière idempotente (ON CONFLICT DO NOTHING).
        Retourne le nombre de lignes réellement insérées.
        """
        if not measures:
            return 0

        query = """
            INSERT INTO measures (read_at, register, volume_kwh, is_valid)
            VALUES %s
            ON CONFLICT (read_at, register) DO NOTHING;
        """

        records = [
            (
                m.timestamp,
                m.register.value,
                m.volume_kwh,
                m.is_valid
            )
            for m in measures
        ]

        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                execute_values(cursor, query, records, page_size=len(records))
                inserted_count = cursor.rowcount
            conn.commit()
        return inserted_count