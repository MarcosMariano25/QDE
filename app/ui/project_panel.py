"""Left-side project navigation panel."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

_SECTION_NAMES = (
    "Project",
    "Sheets",
    "Building",
    "Takeoffs",
    "AI Results",
    "Reports",
)


class ProjectPanel(QWidget):
    """Project navigation with collapsible workspace sections.

    Layout-only shell. Sections are placeholders for future project data.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        header = QLabel("Project", self)
        header.setStyleSheet("font-weight: 600; font-size: 12px; padding: 2px 0;")

        self._tree = QTreeWidget(self)
        self._tree.setObjectName("ProjectPanelTree")
        self._tree.setHeaderHidden(True)
        self._tree.setIndentation(14)
        self._tree.setAnimated(True)
        self._tree.setExpandsOnDoubleClick(True)
        self._tree.setRootIsDecorated(True)
        self._tree.setUniformRowHeights(True)
        self._tree.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        for index, name in enumerate(_SECTION_NAMES):
            section = QTreeWidgetItem([name])
            section.setFlags(
                Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
            )
            placeholder = QTreeWidgetItem(["No items"])
            placeholder.setDisabled(True)
            section.addChild(placeholder)
            self._tree.addTopLevelItem(section)
            section.setExpanded(index == 0)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.addWidget(header)
        layout.addWidget(self._tree)
