"""Right-side inspector panel for selection and property placeholders."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.collapsible_section import CollapsibleSection

_SECTIONS: tuple[tuple[str, str], ...] = (
    ("Selection", "No selection"),
    ("Room Information", "No room selected"),
    ("Surface Information", "No surface selected"),
    ("Finish Information", "No finish assigned"),
    ("Estimating Information", "No estimate data"),
)


class InspectorPanel(QWidget):
    """Property inspector with collapsible placeholder groups.

    Layout-only shell. Groups reserve space for future selection details.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        header = QLabel("Inspector", self)
        header.setStyleSheet("font-weight: 600; font-size: 12px; padding: 2px 0;")

        body = QWidget(self)
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(4)

        for index, (title, placeholder) in enumerate(_SECTIONS):
            section = CollapsibleSection(
                title,
                body,
                expanded=index == 0,
            )
            section.add_placeholder(placeholder)
            body_layout.addWidget(section)

            if index < len(_SECTIONS) - 1:
                divider = QFrame(body)
                divider.setFrameShape(QFrame.Shape.HLine)
                divider.setFrameShadow(QFrame.Shadow.Sunken)
                divider.setStyleSheet("color: #d1d5db;")
                body_layout.addWidget(divider)

        body_layout.addStretch(1)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setWidget(body)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        layout.addWidget(header)
        layout.addWidget(scroll)

        self.setMinimumWidth(260)
        self.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Expanding,
        )
