"""Application bootstrap and lifecycle management."""

from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.ui.mainwindow import MainWindow


class Application:
    """Owns the Qt application lifecycle and main window.

    Responsibilities are limited to creating the QApplication,
    constructing the main window, and running the event loop.
    """

    def __init__(self) -> None:
        self._qt_app = QApplication(sys.argv)
        self._window = MainWindow()

    def run(self) -> int:
        """Show the main window and start the Qt event loop.

        Returns:
            The application exit code from ``QApplication.exec()``.
        """
        self._window.show()
        return self._qt_app.exec()
