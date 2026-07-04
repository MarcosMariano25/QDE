"""Qt PDF document backend.

This is the only module that may import ``PySide6.QtPdf`` or
``PySide6.QtPdfWidgets``. All other code must access documents through
``DocumentEngine``.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QSize, QSizeF
from PySide6.QtGui import QImage
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QApplication, QWidget

from app.document.document_engine import RenderedPage


class QtPdfBackend:
    """Document backend powered by Qt PDF (``QPdfDocument`` + ``QPdfView``)."""

    ZOOM_STEP: float = 1.25
    MIN_ZOOM: float = 0.1
    MAX_ZOOM: float = 10.0

    def __init__(self, parent: QWidget | None = None) -> None:
        self._document = QPdfDocument(parent)
        self._view = QPdfView(parent)
        self._view.setDocument(self._document)
        self._view.setPageMode(QPdfView.PageMode.MultiPage)
        self._view.setZoomMode(QPdfView.ZoomMode.FitInView)

    def viewer_widget(self) -> QWidget:
        """Return the embeddable viewer widget (typed as ``QWidget``)."""
        return self._view

    def open(self, path: str | Path) -> None:
        """Open a PDF file.

        Args:
            path: Absolute or relative path to a PDF.

        Raises:
            RuntimeError: If Qt PDF fails to load the file.
        """
        error = self._document.load(str(path))
        if error != QPdfDocument.Error.None_:
            self._document.close()
            raise RuntimeError(f"Failed to open PDF ({error.name}): {path}")

    def log_runtime_diagnostics(self, phase: str) -> str:
        """Print QPdfView runtime state for debugging and return a short summary.

        Args:
            phase: Label identifying when the snapshot was taken.

        Returns:
            One-line summary suitable for the status bar.
        """
        QApplication.processEvents()

        page_mode = self._view.pageMode()
        zoom_mode = self._view.zoomMode()
        zoom_factor = self._view.zoomFactor()
        v_bar = self._view.verticalScrollBar()
        h_bar = self._view.horizontalScrollBar()
        page_count = self.page_count()
        current_page = self.current_page()
        view_size = self._view.size()
        viewport_size = self._view.viewport().size()

        page_width = page_height = None
        if page_count > 0:
            page_width, page_height = self.page_size(0)

        lines = [
            f"[QPdfView diagnostics:{phase}]",
            f"  PageMode={page_mode.name} (value={page_mode.value})",
            f"  ZoomMode={zoom_mode.name} (value={zoom_mode.value})",
            f"  ZoomFactor={zoom_factor}",
            (
                f"  VerticalScrollbar visible={v_bar.isVisible()} "
                f"min={v_bar.minimum()} max={v_bar.maximum()} "
                f"pageStep={v_bar.pageStep()} value={v_bar.value()}"
            ),
            (
                f"  HorizontalScrollbar visible={h_bar.isVisible()} "
                f"min={h_bar.minimum()} max={h_bar.maximum()} "
                f"pageStep={h_bar.pageStep()} value={h_bar.value()}"
            ),
            f"  DocumentPageCount={page_count}",
            f"  CurrentPageNumber={current_page}",
            (
                f"  ViewerWidgetSize="
                f"{view_size.width()}x{view_size.height()}"
            ),
            (
                f"  ViewportSize="
                f"{viewport_size.width()}x{viewport_size.height()}"
            ),
            f"  DocumentPageSize(page0)={page_width}x{page_height}",
        ]
        report = "\n".join(lines)
        print(report, flush=True)

        return (
            f"{phase}: {page_mode.name}/{zoom_mode.name} "
            f"z={zoom_factor:.3f} pages={page_count} "
            f"vscroll={v_bar.isVisible()}({v_bar.maximum()}) "
            f"view={view_size.width()}x{view_size.height()}"
        )

    def close(self) -> None:
        """Release the open document, if any."""
        if self.is_open():
            self._document.close()

    def is_open(self) -> bool:
        """Return whether a document is ready for viewing."""
        return self._document.status() == QPdfDocument.Status.Ready

    def page_count(self) -> int:
        """Return the number of pages, or ``0`` if none is open."""
        if not self.is_open():
            return 0
        return self._document.pageCount()

    def page_size(self, page_index: int) -> tuple[float, float]:
        """Return ``(width, height)`` in PDF points for a zero-based page.

        Args:
            page_index: Zero-based page index.

        Raises:
            RuntimeError: If no document is open.
            IndexError: If ``page_index`` is out of range.
        """
        self._require_open()
        if page_index < 0 or page_index >= self._document.pageCount():
            raise IndexError(f"Page index out of range: {page_index}")

        size: QSizeF = self._document.pagePointSize(page_index)
        return (size.width(), size.height())

    def render_page(self, page_index: int, scale: float) -> RenderedPage:
        """Render a page to an RGB888 pixel buffer.

        Args:
            page_index: Zero-based page index.
            scale: Uniform scale factor (1.0 = 72 DPI).

        Returns:
            A ``RenderedPage`` suitable for image pipelines.

        Raises:
            RuntimeError: If no document is open.
            IndexError: If ``page_index`` is out of range.
        """
        width_pt, height_pt = self.page_size(page_index)
        width_px = max(1, int(width_pt * scale))
        height_px = max(1, int(height_pt * scale))

        image = self._document.render(page_index, QSize(width_px, height_px))
        if image.isNull():
            raise RuntimeError(f"Failed to render page {page_index}")

        rgb = image.convertToFormat(QImage.Format.Format_RGB888)
        bits = rgb.constBits()
        samples = bytes(bits[: rgb.sizeInBytes()])
        return RenderedPage(
            samples=samples,
            width=rgb.width(),
            height=rgb.height(),
            stride=rgb.bytesPerLine(),
        )

    def current_page(self) -> int:
        """Return the current 1-based page number, or ``0`` if none is open."""
        if not self.is_open():
            return 0
        return self._view.pageNavigator().currentPage() + 1

    def go_to_page(self, page_number: int) -> None:
        """Navigate to a 1-based page number.

        Args:
            page_number: Target page in the range ``1 .. page_count()``.
                Out-of-range values are ignored.
        """
        if not self.is_open():
            return
        if page_number < 1 or page_number > self.page_count():
            return

        navigator = self._view.pageNavigator()
        navigator.jump(
            page_number - 1,
            QPointF(0.0, 0.0),
            navigator.currentZoom(),
        )

    def next_page(self) -> None:
        """Advance to the next page."""
        self.go_to_page(self.current_page() + 1)

    def previous_page(self) -> None:
        """Move to the previous page."""
        self.go_to_page(self.current_page() - 1)

    def zoom_in(self) -> None:
        """Increase zoom by one step and leave fit mode."""
        if not self.is_open():
            return
        factor = min(self._view.zoomFactor() * self.ZOOM_STEP, self.MAX_ZOOM)
        self._view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._view.setZoomFactor(factor)

    def zoom_out(self) -> None:
        """Decrease zoom by one step and leave fit mode."""
        if not self.is_open():
            return
        factor = max(self._view.zoomFactor() / self.ZOOM_STEP, self.MIN_ZOOM)
        self._view.setZoomMode(QPdfView.ZoomMode.Custom)
        self._view.setZoomFactor(factor)

    def fit_width(self) -> None:
        """Scale pages to the viewport width."""
        if not self.is_open():
            return
        self._view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

    def fit_page(self) -> None:
        """Scale pages to fit entirely within the viewport."""
        if not self.is_open():
            return
        self._view.setZoomMode(QPdfView.ZoomMode.FitInView)

    def _require_open(self) -> None:
        """Raise if no document is ready."""
        if not self.is_open():
            raise RuntimeError("No document is open.")
