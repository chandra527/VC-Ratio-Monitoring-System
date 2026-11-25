import logging
import threading


logger = logging.getLogger(__name__)


class VehicleEventSender:
    """Pengirim antrean event kendaraan ke MySQL."""

    def __init__(
        self,
        event_logger,
        database_config,
        interval=1.0,
        retry_interval=5.0,
        batch_size=100
    ):
        self.event_logger = event_logger
        self.database_config = database_config
        self.interval = interval
        self.retry_interval = retry_interval
        self.batch_size = batch_size

        self._stop_event = threading.Event()
        self._thread = None

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return

        self._stop_event.clear()

        self._thread = threading.Thread(
            target=self._run,
            name=f"vehicle-sender-{self.event_logger.camera_code}",
            daemon=True
        )

        self._thread.start()

    def _run(self):
        while not self._stop_event.is_set():
            try:
                sent = self.event_logger.flush_to_mysql(
                    self.database_config,
                    batch_size=self.batch_size
                )

                if sent > 0:
                    logger.info(
                        "Event kamera %s: %s event dikonfirmasi",
                        self.event_logger.camera_code,
                        sent
                    )

                # Jika batch penuh, segera proses batch berikutnya.
                delay = 0 if sent == self.batch_size else self.interval

            except Exception:
                logger.exception(
                    "Gagal mengirim event kamera %s",
                    self.event_logger.camera_code
                )
                delay = self.retry_interval

            self._stop_event.wait(delay)

    def stop(self, timeout=10):
        self._stop_event.set()

        if self._thread is not None:
            self._thread.join(timeout=timeout)

        return self._thread is None or not self._thread.is_alive()
