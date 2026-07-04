"""Reusable PDF viewer widget powered by PyMuPDF."""

from __future__ import annotations

from typing import Literal

import fitz
from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QImage, QPixmap, QResizeEvent
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

FitMode = Literal["page", "width"]


class PDFViewer(QWidget):
    """Single-page blueprint-style PDF viewer.

    Rendering, scrolling, zoom, and page navigation are isolated here.
    Pages are shown one at a time at a uniform zoom factor; the pixmap is
    never stretched. ``QScrollArea`` provides scrollbars and mouse-wheel
    scrolling when the page exceeds the viewport.
    """

    ZOOM_STEP: float = 1.25
    MIN_ZOOM: float = 0.1
    MAX_ZOOM: float = 10.0

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._document: fitz.Document | None = None
        self._page_index: int = 0
        self._zoom: float = 1.0
        self._fit_mode: FitMode | None = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Create the scrollable page display and placeholder."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._page_label = QLabel("Open a PDF to begin")
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setScaledContents(False)

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(False)
        self._scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self._scroll_area.setWidget(self._page_label)
        layout.addWidget(self._scroll_area)

    def load_pdf(self, path: str) -> None:
        """Open a PDF document and render the first page.

        Args:
            path: Absolute or relative path to a PDF file.
        """
        self._close_document()
        self._document = fitz.open(path)
        self._page_index = 0
        self.fit_page()
        self._reset_scroll_position()

    def render_current_page(self) -> None:
        """Render the current page at the active zoom level.

        The page is drawn at its natural aspect ratio. The label is sized
        exactly to the pixmap so ``QScrollArea`` can scroll without stretching.
        """
        if self._document is None:
            return

        page = self._document.load_page(self._page_index)
        matrix = fitz.Matrix(self._zoom, self._zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image = QImage(
            pixmap.samples,
            pixmap.width,
            pixmap.height,
            pixmap.stride,
            QImage.Format.Format_RGB888,
        ).copy()

        page_pixmap = QPixmap.fromImage(image)
        self._page_label.setText("")
        self._page_label.setPixmap(page_pixmap)
        self._page_label.resize(page_pixmap.size())

    def next_page(self) -> None:
        """Advance to the next page, preserving the current zoom level."""
        self.go_to_page(self.current_page() + 1)

    def previous_page(self) -> None:
        """Move to the previous page, preserving the current zoom level."""
        self.go_to_page(self.current_page() - 1)

    def go_to_page(self, page_number: int) -> None:
        """Navigate to a 1-based page number without changing zoom.

        Args:
            page_number: Target page in the range ``1 .. page_count()``.
                Out-of-range values are ignored.
        """
        if self._document is None:
            return
        if page_number < 1 or page_number > self._document.page_count:
            return

        new_index = page_number - 1
        if new_index == self._page_index:
            return

        self._page_index = new_index
        self.render_current_page()
        self._reset_scroll_position()

    def current_page(self) -> int:
        """Return the current 1-based page number, or ``0`` if none is open."""
        if self._document is None:
            return 0
        return self._page_index + 1

    def page_count(self) -> int:
        """Return the document page count, or ``0`` if none is open."""
        if self._document is None:
            return 0
        return self._document.page_count

    def zoom_in(self) -> None:
        """Increase zoom by one step and leave fit mode."""
        if self._document is None:
            return

        self._fit_mode = None
        self._zoom = min(self._zoom * self.ZOOM_STEP, self.MAX_ZOOM)
        self.render_current_page()

    def zoom_out(self) -> None:
        """Decrease zoom by one step and leave fit mode."""
        if self._document is None:
            return

        self._fit_mode = None
        self._zoom = max(self._zoom / self.ZOOM_STEP, self.MIN_ZOOM)
        self.render_current_page()

    def fit_width(self) -> None:
        """Scale the page to the viewport width, preserving aspect ratio."""
        if self._document is None:
            return

        self._fit_mode = "width"
        self._update_zoom_for_fit()
        self.render_current_page()

    def fit_page(self) -> None:
        """Scale the page to fit entirely within the viewport."""
        if self._document is None:
            return

        self._fit_mode = "page"
        self._update_zoom_for_fit()
        self.render_current_page()

    def resizeEvent(self, event: QResizeEvent) -> None:
        """Re-apply fit modes so the page scales smoothly with the window."""
        super().resizeEvent(event)
        if self._document is not None and self._fit_mode is not None:
            self._update_zoom_for_fit()
            self.render_current_page()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Release the open document when the widget is closed."""
        self._close_document()
        super().closeEvent(event)

    def _reset_scroll_position(self) -> None:
        """Move scrollbars to the top-left of the current page."""
        self._scroll_area.horizontalScrollBar().setValue(0)
        self._scroll_area.verticalScrollBar().setValue(0)

    def _update_zoom_for_fit(self) -> None:
        """Set ``_zoom`` from the current fit mode and viewport size."""
        if self._document is None or self._fit_mode is None:
            return

        page = self._document.load_page(self._page_index)
        page_rect = page.rect
        viewport = self._scroll_area.viewport().size()
        if viewport.width() <= 0 or viewport.height() <= 0:
            return
        if page_rect.width <= 0 or page_rect.height <= 0:
            return

        width_scale = viewport.width() / page_rect.width
        if self._fit_mode == "width":
            self._zoom = width_scale
        else:
            height_scale = viewport.height() / page_rect.height
            self._zoom = min(width_scale, height_scale)

    def _close_document(self) -> None:
        """Close any open document and restore the placeholder."""
        if self._document is not None:
            self._document.close()
            self._document = None

        self._page_index = 0
        self._zoom = 1.0
        self._fit_mode = None
        self._page_label.setPixmap(QPixmap())
        self._page_label.setText("Open a PDF to begin")
        self._page_label.adjustSize()
        self._reset_scroll_position()
