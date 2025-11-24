import threading
import time
import sys


class Spinner:
    """A simple console spinner for long-running tasks."""

    def __init__(self, message="Working..."):
        self.message = message
        self.stop_running = False
        self.spinner_cycle = ["|", "/", "-", "\\"]

    def start(self):
        self.stop_running = False
        threading.Thread(target=self._spin, daemon=True).start()

    def _spin(self):
        i = 0
        while not self.stop_running:
            sys.stdout.write(
                f"\r{self.spinner_cycle[i % len(self.spinner_cycle)]} {self.message}"
            )
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write("\r✓ " + self.message + " — done.\n")
        sys.stdout.flush()

    def stop(self):
        self.stop_running = True
