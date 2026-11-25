import sqlite3
from contextlib import closing
import uuid
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


class VehicleEventLogger:
    """Antrean lokal persisten untuk event kendaraan."""

    def __init__(self, camera_code, queue_dir="data/event_queue"):
        self.camera_code = camera_code
        self.session_id = uuid.uuid4().hex
        self.sequence = 0

        queue_path = Path(queue_dir)
        if not queue_path.is_absolute():
            queue_path = Path(__file__).resolve().parent.parent / queue_path
        queue_path.mkdir(parents=True, exist_ok=True)

        self.db_path = queue_path / f"{camera_code}.sqlite3"

        with closing(self._connect()) as conn, conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_events (
                    event_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    vehicle_type TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    counted_at TEXT NOT NULL
                )
            """)

    def _connect(self):
        conn = sqlite3.connect(
            str(self.db_path),
            timeout=5
        )
        conn.execute("PRAGMA busy_timeout = 5000")
        return conn

    def record(self, vehicle_type, direction):
        self.sequence += 1

        event_id = uuid.uuid4().hex
        counted_at = datetime.now(
            ZoneInfo("Asia/Jakarta")
        ).strftime("%Y-%m-%d %H:%M:%S.%f")

        with closing(self._connect()) as conn, conn:
            conn.execute(
                """
                INSERT INTO pending_events (
                    event_id,
                    session_id,
                    vehicle_type,
                    direction,
                    counted_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    self.session_id,
                    vehicle_type,
                    direction,
                    counted_at
                )
            )

        return event_id

    def pending_count(self):
        with closing(self._connect()) as conn, conn:
            row = conn.execute(
                "SELECT COUNT(*) FROM pending_events"
            ).fetchone()

        return row[0]

    def flush_to_mysql(self, database_config, batch_size=100):
        """
        Kirim event tertunda ke MySQL.

        Mengembalikan jumlah event yang berhasil dikonfirmasi.
        Jika gagal, antrean lokal tetap dipertahankan.
        """
        import mysql.connector

        with closing(self._connect()) as local, local:
            rows = local.execute(
                """
                SELECT event_id, session_id, vehicle_type,
                       direction, counted_at
                FROM pending_events
                ORDER BY rowid
                LIMIT ?
                """,
                (batch_size,)
            ).fetchall()

        if not rows:
            return 0

        connection = None
        cursor = None

        try:
            connection = mysql.connector.connect(
                **database_config,
                connection_timeout=5
            )
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT id FROM cameras
                WHERE code = %s AND is_active = 1
                LIMIT 1
                """,
                (self.camera_code,)
            )

            camera_row = cursor.fetchone()

            if camera_row is None:
                raise RuntimeError(
                    f"Kamera tidak ditemukan: {self.camera_code}"
                )

            camera_id = camera_row[0]

            for (
                event_id,
                session_id,
                vehicle_type,
                direction,
                counted_at
            ) in rows:
                try:
                    cursor.execute(
                        """
                        INSERT INTO vehicle_count_events (
                            camera_id, session_id, event_id,
                            vehicle_type, direction, counted_at
                        ) VALUES (%s, %s, %s, %s, %s, %s)
                        """,
                        (
                            camera_id,
                            session_id,
                            event_id,
                            vehicle_type,
                            direction,
                            counted_at
                        )
                    )
                except mysql.connector.IntegrityError as error:
                    if error.errno != 1062:
                        raise

            connection.commit()

            event_ids = [row[0] for row in rows]

            with closing(self._connect()) as local, local:
                local.executemany(
                    "DELETE FROM pending_events WHERE event_id = ?",
                    [(event_id,) for event_id in event_ids]
                )

            return len(rows)

        except Exception:
            if connection is not None:
                try:
                    connection.rollback()
                except Exception:
                    pass
            raise

        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None:
                connection.close()