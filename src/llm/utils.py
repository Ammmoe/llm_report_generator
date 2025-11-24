"""
Spinner module: Implements a simple console spinner for indicating progress
during long-running tasks.
"""

import threading
import time
import sys


class Spinner:
    """A simple console spinner for long-running tasks."""

    def __init__(self, message="Working..."):
        """Initialize spinner with an optional message."""
        self.message = message
        self.stop_running = False
        self.spinner_cycle = ["|", "/", "-", "\\"]

    def start(self):
        """Start the spinner animation in a background thread."""
        self.stop_running = False
        threading.Thread(target=self._spin, daemon=True).start()

    def _spin(self):
        """Internal method to update spinner animation until stopped."""
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
        """Stop the spinner animation and print completion message."""
        self.stop_running = True
