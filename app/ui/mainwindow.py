"""Primary application window."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QWidget,
)

from app.viewer.pdfviewer import PDFViewer


class MainWindow(QMainWindow):
    """Main window shell for Paintable AI.

    Hosts the menu bar, Project Explorer dock, PDF viewer area,
    and status bar. Does not contain PDF or estimating business logic.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paintable AI")
        self.resize(1400, 900)

        self._pdf_viewer = PDFViewer(self)
        self.setCentralWidget(self._pdf_viewer)

        self._create_menus()
        self._create_project_explorer()
        self.statusBar().showMessage("Ready")

    def _create_menus(self) -> None:
        """Build the professional menu bar."""
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("&File")

        open_pdf_action = QAction("Open PDF", self)
        open_pdf_action.setShortcut("Ctrl+O")
        open_pdf_action.triggered.connect(self._on_open_pdf)
        file_menu.addAction(open_pdf_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def _create_project_explorer(self) -> None:
        """Create the left-side Project Explorer dock widget."""
        dock = QDockWidget("Project Explorer", self)
        dock.setObjectName("ProjectExplorerDock")
        dock.setWidget(QWidget(dock))
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)

    def _on_open_pdf(self) -> None:
        """Open a PDF via file dialog and hand it to the viewer."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            "",
            "PDF Files (*.pdf)",
        )
        if not file_path:
            return

        self._pdf_viewer.load_pdf(file_path)
        self.statusBar().showMessage(f"Loaded: {Path(file_path).name}")
