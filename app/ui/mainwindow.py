"""Primary application window and workspace shell."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QDockWidget,
    QFileDialog,
    QLabel,
    QMainWindow,
    QWidget,
)

from app.ui.inspector_panel import InspectorPanel
from app.ui.project_panel import ProjectPanel
from app.viewer.pdfviewer import PDFViewer


class MainWindow(QMainWindow):
    """Paintable AI commercial estimating workspace.

    Assembles the menu bar, project panel, document viewer, inspector panel,
    and status bar. Contains no estimating, AI, or measurement logic.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Paintable AI")
        self.resize(1600, 960)
        self.setMinimumSize(1100, 700)
        self.setDockNestingEnabled(True)

        self._pdf_viewer = PDFViewer(self)
        self.setCentralWidget(self._pdf_viewer)

        self._project_dock = self._create_project_dock()
        self._inspector_dock = self._create_inspector_dock()

        self._create_menus()
        self._create_status_bar()
        self._apply_workspace_style()

    def _create_project_dock(self) -> QDockWidget:
        """Create the left Project Panel dock."""
        dock = QDockWidget("Project Panel", self)
        dock.setObjectName("ProjectPanelDock")
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        panel = ProjectPanel(dock)
        panel.setMinimumWidth(240)
        dock.setWidget(panel)
        dock.setMinimumWidth(240)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock)
        return dock

    def _create_inspector_dock(self) -> QDockWidget:
        """Create the right Inspector Panel dock."""
        dock = QDockWidget("Inspector", self)
        dock.setObjectName("InspectorPanelDock")
        dock.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea
            | Qt.DockWidgetArea.RightDockWidgetArea
        )
        dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable
            | QDockWidget.DockWidgetFeature.DockWidgetClosable
            | QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )
        dock.setWidget(InspectorPanel(dock))
        dock.setMinimumWidth(280)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock)
        return dock

    def _create_menus(self) -> None:
        """Build the professional menu bar."""
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")
        open_pdf_action = QAction("Open PDF…", self)
        open_pdf_action.setShortcut(QKeySequence.StandardKey.Open)
        open_pdf_action.triggered.connect(self._on_open_pdf)
        file_menu.addAction(open_pdf_action)
        file_menu.addSeparator()
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        edit_menu = menu_bar.addMenu("&Edit")
        for label in ("Undo", "Redo", "Cut", "Copy", "Paste"):
            action = QAction(label, self)
            action.setEnabled(False)
            edit_menu.addAction(action)

        view_menu = menu_bar.addMenu("&View")
        view_menu.addAction(self._project_dock.toggleViewAction())
        view_menu.addAction(self._inspector_dock.toggleViewAction())
        view_menu.addSeparator()
        fit_page_action = QAction("Fit Page", self)
        fit_page_action.triggered.connect(self._pdf_viewer.fit_page)
        view_menu.addAction(fit_page_action)
        fit_width_action = QAction("Fit Width", self)
        fit_width_action.triggered.connect(self._pdf_viewer.fit_width)
        view_menu.addAction(fit_width_action)
        view_menu.addSeparator()
        zoom_in_action = QAction("Zoom In", self)
        zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        zoom_in_action.triggered.connect(self._pdf_viewer.zoom_in)
        view_menu.addAction(zoom_in_action)
        zoom_out_action = QAction("Zoom Out", self)
        zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        zoom_out_action.triggered.connect(self._pdf_viewer.zoom_out)
        view_menu.addAction(zoom_out_action)

        tools_menu = menu_bar.addMenu("&Tools")
        for label in ("Measure", "Scale Calibration", "Takeoff Tools"):
            action = QAction(label, self)
            action.setEnabled(False)
            tools_menu.addAction(action)

        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction("About Paintable AI", self)
        about_action.setEnabled(False)
        help_menu.addAction(about_action)

    def _create_status_bar(self) -> None:
        """Create the bottom status bar with workspace placeholders."""
        status = self.statusBar()
        status.setSizeGripEnabled(True)
        status.showMessage("Ready")

        self._sheet_label = QLabel("Sheet: —")
        self._page_label = QLabel("Page: —")
        self._zoom_label = QLabel("Zoom: —")
        for label in (self._sheet_label, self._page_label, self._zoom_label):
            label.setMinimumWidth(90)
            label.setStyleSheet("padding: 0 8px; color: #4b5563;")
            status.addPermanentWidget(label)

    def _apply_workspace_style(self) -> None:
        """Apply light professional styling to the workspace chrome."""
        self.setStyleSheet(
            """
            QMainWindow {
                background: #f3f4f6;
            }
            QMenuBar {
                background: #ffffff;
                border-bottom: 1px solid #e5e7eb;
                padding: 2px 4px;
            }
            QMenuBar::item {
                padding: 4px 10px;
                background: transparent;
            }
            QMenuBar::item:selected {
                background: #e5e7eb;
                border-radius: 3px;
            }
            QDockWidget {
                titlebar-close-icon: none;
                font-weight: 600;
            }
            QDockWidget::title {
                background: #e5e7eb;
                padding: 8px 10px;
                border-bottom: 1px solid #d1d5db;
            }
            QStatusBar {
                background: #ffffff;
                border-top: 1px solid #e5e7eb;
            }
            QTreeWidget {
                border: 1px solid #e5e7eb;
                background: #ffffff;
                outline: none;
            }
            QTreeWidget::item {
                padding: 4px 2px;
            }
            QTreeWidget::item:selected {
                background: #dbeafe;
                color: #111827;
            }
            """
        )

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
        name = Path(file_path).name
        diagnostics = self._pdf_viewer.log_runtime_diagnostics("status-bar")
        self.statusBar().showMessage(f"Loaded: {name} | {diagnostics}")
        self._sheet_label.setText(f"Sheet: {name}")
        page_count = self._pdf_viewer.page_count()
        current = self._pdf_viewer.current_page()
        self._page_label.setText(f"Page: {current} / {page_count}")
        self._zoom_label.setText("Zoom: Fit")
