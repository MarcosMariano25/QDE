"""Document viewer host widget.

Hosts the widget provided by ``DocumentEngine``. This module never imports
Qt PDF or other format backends; all document operations go through the
engine.
"""

from __future__ import annotations

from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QVBoxLayout, QWidget

from app.document import DocumentEngine


class PDFViewer(QWidget):
    """Thin host for the Document Engine viewer widget.

    Preserves a stable UI-facing API for ``MainWindow`` while delegating all
    document behavior to ``DocumentEngine``.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._engine = DocumentEngine(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._engine.viewer_widget())

    def load_pdf(self, path: str) -> None:
        """Open a document in the engine-owned viewer.

        Args:
            path: Absolute or relative path to a supported drawing file.
        """
        self._engine.open(path)

    def next_page(self) -> None:
        """Advance to the next page."""
        self._engine.next_page()

    def previous_page(self) -> None:
        """Move to the previous page."""
        self._engine.previous_page()

    def go_to_page(self, page_number: int) -> None:
        """Navigate to a 1-based page number."""
        self._engine.go_to_page(page_number)

    def current_page(self) -> int:
        """Return the current 1-based page number, or ``0`` if none is open."""
        return self._engine.current_page()

    def page_count(self) -> int:
        """Return the document page count, or ``0`` if none is open."""
        return self._engine.page_count()

    def zoom_in(self) -> None:
        """Increase zoom by one step."""
        self._engine.zoom_in()

    def zoom_out(self) -> None:
        """Decrease zoom by one step."""
        self._engine.zoom_out()

    def fit_width(self) -> None:
        """Fit page width to the viewport."""
        self._engine.fit_width()

    def fit_page(self) -> None:
        """Fit the whole page in the viewport."""
        self._engine.fit_page()

    def log_runtime_diagnostics(self, phase: str) -> str:
        """Print runtime viewer diagnostics and return a short summary."""
        return self._engine.log_runtime_diagnostics(phase)

    def closeEvent(self, event: QCloseEvent) -> None:
        """Release the open document when the widget is closed."""
        self._engine.close()
        super().closeEvent(event)
