"""Icono de bandeja: togglear el highlight, abrir preferencias y salir de la app."""

from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices, QIcon
from PyQt6.QtWidgets import QMenu, QSystemTrayIcon

ICON_NAME = "input-mouse"
ICON_FALLBACK = "preferences-desktop-mouse"
DONATE_URL = "https://ko-fi.com/marcoamontesve"
KOFI_ICON_PATH = Path(__file__).resolve().parent / "kofi_cup.png"


class TrayIcon(QSystemTrayIcon):
    def __init__(self, on_toggle, on_preferences, on_quit, parent=None):
        icon = QIcon.fromTheme(ICON_NAME)
        if icon.isNull():
            icon = QIcon.fromTheme(ICON_FALLBACK)
        super().__init__(icon, parent)
        self.setToolTip("Cursor Highlighter")

        menu = QMenu()
        menu.addAction("Mostrar/Ocultar highlight (F8)", on_toggle)
        menu.addAction("Preferencias...", on_preferences)
        menu.addSeparator()
        menu.addAction(QIcon(str(KOFI_ICON_PATH)), "Donar", open_donate_page)
        menu.addSeparator()
        menu.addAction("Salir", on_quit)
        self.setContextMenu(menu)


def open_donate_page() -> None:
    QDesktopServices.openUrl(QUrl(DONATE_URL))
