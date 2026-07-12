"""Tema oscuro de la app (tray, preferencias, dialogos). Un solo lugar para la
paleta, asi el look es consistente sin depender del esquema de color/acento
del sistema (que puede variar de una maquina a otra).
"""

BG = "#1e1f22"
PANEL_BG = "#252629"
BORDER = "#35373b"
TEXT = "#e6e6e6"
TEXT_MUTED = "#9aa0a6"
ACCENT = "#5b8cff"
ACCENT_HOVER = "#7aa2ff"
DISABLED = "#4a4d52"

DARK_STYLESHEET = f"""
QWidget {{
    background-color: {BG};
    color: {TEXT};
    font-size: 13px;
}}

QDialog {{
    background-color: {BG};
}}

QGroupBox {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 8px;
    margin-top: 14px;
    padding: 12px 10px 10px 10px;
    font-weight: 600;
    color: {TEXT_MUTED};
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    top: -2px;
    padding: 0 6px;
}}

QLabel {{
    background: transparent;
    color: {TEXT};
}}

QComboBox, QPushButton {{
    background-color: {PANEL_BG};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 5px 10px;
    color: {TEXT};
}}

QComboBox:hover, QPushButton:hover {{
    border-color: {ACCENT};
}}

QPushButton:pressed {{
    background-color: {BORDER};
}}

QComboBox::drop-down {{
    border: none;
}}

QComboBox QAbstractItemView {{
    background-color: {PANEL_BG};
    color: {TEXT};
    selection-background-color: {ACCENT};
    border: 1px solid {BORDER};
}}

QSlider::groove:horizontal {{
    height: 4px;
    background: {BORDER};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal {{
    background: {ACCENT};
    border-radius: 2px;
}}

QSlider::sub-page:horizontal:disabled {{
    background: {DISABLED};
}}

QSlider::handle:horizontal {{
    width: 14px;
    margin: -6px 0;
    background: {ACCENT};
    border-radius: 7px;
}}

QSlider::handle:horizontal:hover {{
    background: {ACCENT_HOVER};
}}

QSlider::handle:horizontal:disabled {{
    background: {DISABLED};
}}

QMenu {{
    background-color: {PANEL_BG};
    color: {TEXT};
    border: 1px solid {BORDER};
}}

QMenu::item:selected {{
    background-color: {ACCENT};
}}
"""
