import threading
import copy
import time
import uvicorn
import urllib.error
import urllib.request
from fastapi import FastAPI


class FrontendApi:

    def __init__(self, HOST, PORT):
        self.host = HOST
        self.port = PORT

        self.app = FastAPI()

        self.app.add_api_route(
            "/api/health",
            self._get_health,
            methods=["GET"],
        )

        self.app.add_api_route(
            "/api/live",
            self._get_live_data,
            methods=["GET"],
        )

        self.current_live_data = {}
        self.data_lock = threading.Lock()

        self.thread = None

        self.server = None
        self.server_online = False

    def _get_health(self):
        """Status des API-Servers prüfen"""
        return {
            "status": "ok",
            "service": "hortivault-api",
        }

    def _get_live_data(self):
        """Live-Daten ausgeben"""
        with self.data_lock:
            return copy.deepcopy(self.current_live_data)

    def _check_server_health(self):
        health_url = f"http://{self.host}:{self.port}/api/health"

        try:
            with urllib.request.urlopen(health_url, timeout=1.0) as response:
                return response.status == 200

        except (
            urllib.error.URLError,
            TimeoutError,
            OSError,
            ValueError,
        ):
            return False

    def _run_api(self):
        """UVICORN- / API- Server starten"""
        try:
            config = uvicorn.Config(self.app, host=self.host, port=self.port)
            self.server = uvicorn.Server(config)
            self.server.run()  # Funktion blockiert und wird deswegen im Thread ausgeführt

        except Exception as e:
            print(f"[ERROR]: Fehler im API-Server: {e}")

        # sobald der Uvicorn Server heruntergefahren wird oder die Exception greift wird der finally Block ausgeführt
        finally:
            self.server = None
            self.server_online = False

    def _restart_api_thread(self):
        if not self.stop_api_thread():
            return

        self.start_api_thread()

    def update_live_data(self, live_data):
        """Live-Daten aktualisieren und als Kopie im Objekt speichern"""
        with self.data_lock:
            self.current_live_data = copy.deepcopy(live_data)

    def start_api_thread(self):
        """API-Thread und _run_api() ausführen (Server starten)"""
        if self.thread is not None and self.thread.is_alive():
            return

        try:
            self.thread = threading.Thread(
                target=self._run_api,
                name="hortivault-api",
                daemon=True,
            )

            self.thread.start()

        except Exception as e:
            print(f"[ERROR]: API-Thread konnte nicht gestartet werden: {e}")

            self.thread = None

    def stop_api_thread(self):
        """Beendet den laufenden API-Thread"""
        if self.server is not None:
            self.server.should_exit = True

        if self.thread is not None and self.thread.is_alive():
            self.thread.join(timeout=5)

        if self.thread is not None and self.thread.is_alive():
            print("[ERROR]: API-Thread konnte nicht sauber beendet werden.")
            return False

        self.thread = None

        return True

    def start_monitoring_thread(self):
        """API Monitoring Thread mir _api_checker() starten"""
        monitoring_thread = threading.Thread(
            target=self._api_checker, name="monitoring-thread", daemon=True
        )
        monitoring_thread.start()

    def _api_checker(self):
        """Prüft ob der API Server online ist und startet diesen ggf. neu."""
        while True:
            time.sleep(15)

            self.server_online = self._check_server_health()

            thread_alive = self.thread is not None and self.thread.is_alive()

            # API-Server und Thread online
            if not self.server_online and thread_alive:
                self._restart_api_thread()
