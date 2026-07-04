"""Format-agnostic document engine.

All document open, viewing, navigation, and page-render requests flow through
this engine. Callers must never import Qt PDF or other format backends
directly so future formats (DWG, IFC, images) can be added without changing
UI or viewer code.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from PySide6.QtWidgets import QWidget


@dataclass(frozen=True)
class RenderedPage:
    """Raw RGB888 page pixels produced by a document backend."""

    samples: bytes
    width: int
    height: int
    stride: int


class DocumentBackend(Protocol):
    """Backend contract for a single drawing format."""

    def viewer_widget(self) -> QWidget:
        """Return the embeddable viewer widget for this backend."""

    def open(self, path: str | Path) -> None:
        """Open a document from disk."""

    def close(self) -> None:
        """Release backend resources for the open document."""

    def is_open(self) -> bool:
        """Return whether a document is open."""

    def page_count(self) -> int:
        """Return the page count, or ``0`` if none is open."""

    def page_size(self, page_index: int) -> tuple[float, float]:
        """Return ``(width, height)`` in PDF points for a zero-based page."""

    def render_page(self, page_index: int, scale: float) -> RenderedPage:
        """Render a page at ``scale`` to an RGB888 buffer."""

    def current_page(self) -> int:
        """Return the current 1-based page number, or ``0`` if none is open."""

    def go_to_page(self, page_number: int) -> None:
        """Navigate to a 1-based page number."""

    def next_page(self) -> None:
        """Advance to the next page."""

    def previous_page(self) -> None:
        """Move to the previous page."""

    def zoom_in(self) -> None:
        """Increase zoom by one step."""

    def zoom_out(self) -> None:
        """Decrease zoom by one step."""

    def fit_width(self) -> None:
        """Fit page width to the viewport."""

    def fit_page(self) -> None:
        """Fit the whole page in the viewport."""

    def log_runtime_diagnostics(self, phase: str) -> str:
        """Print runtime viewer diagnostics and return a short summary."""


class DocumentEngine:
    """Owns the active document backend and exposes format-neutral operations.

    Backend selection is based on file extension. Only PDF (via Qt PDF) is
    supported today; additional backends can register without changing callers.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        # PDF is the default interactive format; the backend owns QPdfView.
        from app.document.qtpdf_backend import QtPdfBackend

        self._backend: DocumentBackend = QtPdfBackend(parent)

    def viewer_widget(self) -> QWidget:
        """Return the embeddable viewer widget for the active backend."""
        return self._backend.viewer_widget()

    def open(self, path: str | Path) -> None:
        """Open a document, validating that a backend supports the type.

        Args:
            path: Absolute or relative path to a supported drawing file.

        Raises:
            ValueError: If the file type is not supported.
            RuntimeError: If the backend fails to open the file.
        """
        path = Path(path)
        self._ensure_backend_for_path(path)
        self._backend.close()
        self._backend.open(path)
        self.fit_page()
        self._schedule_runtime_diagnostics()

    def log_runtime_diagnostics(self, phase: str) -> str:
        """Print runtime viewer diagnostics and return a short summary."""
        return self._backend.log_runtime_diagnostics(phase)

    def _schedule_runtime_diagnostics(self) -> None:
        """Capture QPdfView state immediately and after layout settles."""
        from PySide6.QtCore import QTimer

        self._backend.log_runtime_diagnostics("post-open")
        QTimer.singleShot(
            0,
            lambda: self._backend.log_runtime_diagnostics("post-layout-0ms"),
        )
        QTimer.singleShot(
            100,
            lambda: self._backend.log_runtime_diagnostics("post-layout-100ms"),
        )

    def close(self) -> None:
        """Close the active document."""
        self._backend.close()

    def is_open(self) -> bool:
        """Return whether a document is currently open."""
        return self._backend.is_open()

    def page_count(self) -> int:
        """Return the page count, or ``0`` if none is open."""
        return self._backend.page_count()

    def page_size(self, page_index: int) -> tuple[float, float]:
        """Return ``(width, height)`` in PDF points for a zero-based page.

        Args:
            page_index: Zero-based page index.

        Raises:
            RuntimeError: If no document is open.
        """
        return self._backend.page_size(page_index)

    def render_page(self, page_index: int, scale: float) -> RenderedPage:
        """Render a page at the given scale for non-UI pipelines.

        Args:
            page_index: Zero-based page index.
            scale: Uniform scale factor (1.0 = 72 DPI for PDF).

        Returns:
            RGB888 pixel data.

        Raises:
            RuntimeError: If no document is open.
        """
        return self._backend.render_page(page_index, scale)

    def current_page(self) -> int:
        """Return the current 1-based page number, or ``0`` if none is open."""
        return self._backend.current_page()

    def go_to_page(self, page_number: int) -> None:
        """Navigate to a 1-based page number."""
        self._backend.go_to_page(page_number)

    def next_page(self) -> None:
        """Advance to the next page."""
        self._backend.next_page()

    def previous_page(self) -> None:
        """Move to the previous page."""
        self._backend.previous_page()

    def zoom_in(self) -> None:
        """Increase zoom by one step."""
        self._backend.zoom_in()

    def zoom_out(self) -> None:
        """Decrease zoom by one step."""
        self._backend.zoom_out()

    def fit_width(self) -> None:
        """Fit page width to the viewport."""
        self._backend.fit_width()

    def fit_page(self) -> None:
        """Fit the whole page in the viewport."""
        self._backend.fit_page()

    def _ensure_backend_for_path(self, path: Path) -> None:
        """Validate that the active backend supports ``path``.

        Args:
            path: Path used for extension-based selection.

        Raises:
            ValueError: If no backend supports the extension.
        """
        suffix = path.suffix.lower()
        if suffix == ".pdf":
            return

        raise ValueError(f"Unsupported document type: {suffix or '(none)'}")
