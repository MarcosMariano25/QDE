"""Collapsible section used by workspace panels."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)


class CollapsibleSection(QWidget):
    """A titled section that can expand and collapse its body content."""

    def __init__(
        self,
        title: str,
        parent: QWidget | None = None,
        *,
        expanded: bool = True,
    ) -> None:
        super().__init__(parent)

        self._toggle = QToolButton(self)
        self._toggle.setText(title)
        self._toggle.setCheckable(True)
        self._toggle.setChecked(expanded)
        self._toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
        self._toggle.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )
        self._toggle.setStyleSheet(
            "QToolButton {"
            "  font-weight: 600;"
            "  padding: 6px 4px;"
            "  border: none;"
            "  text-align: left;"
            "  background: transparent;"
            "}"
        )
        self._toggle.toggled.connect(self._on_toggled)

        self._body = QFrame(self)
        self._body.setFrameShape(QFrame.Shape.NoFrame)
        self._body.setVisible(expanded)
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(12, 4, 8, 10)
        self._body_layout.setSpacing(6)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._toggle)
        root.addWidget(self._body)

    def add_placeholder(self, text: str) -> None:
        """Add muted placeholder text inside the section body."""
        label = QLabel(text, self._body)
        label.setWordWrap(True)
        label.setStyleSheet("color: #6b7280;")
        self._body_layout.addWidget(label)

    def add_widget(self, widget: QWidget) -> None:
        """Add a custom widget to the section body."""
        self._body_layout.addWidget(widget)

    def _on_toggled(self, expanded: bool) -> None:
        """Show or hide the body and update the header arrow."""
        self._body.setVisible(expanded)
        self._toggle.setArrowType(
            Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow
        )
