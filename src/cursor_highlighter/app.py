"""Entry point instalable (`cursor-highlighter`): proceso de control.

Lanza el overlay (layer-shell) como subproceso aparte y muestra tray +
preferencias en este proceso (xdg-shell normal, con decoraciones). Ver el
comentario en kwin_bridge/dbus_service.py sobre por que van separados.
"""

import subprocess
import sys
import time

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMessageBox, QSystemTrayIcon

from cursor_highlighter.config.i18n import tr
from cursor_highlighter.config.settings_window import SettingsWindow
from cursor_highlighter.config.store import SettingsStore
from cursor_highlighter.config.theme import DARK_STYLESHEET
from cursor_highlighter.input.device_discovery import discover_devices
from cursor_highlighter.kwin_bridge.client import OverlayClient, overlay_running
from cursor_highlighter.kwin_bridge.loader import reload_bridge_script
from cursor_highlighter.tray.icon import ICON_FALLBACK, ICON_NAME, TrayIcon

OVERLAY_START_TIMEOUT_S = 5.0
OVERLAY_POLL_INTERVAL_S = 0.1
DESKTOP_FILE_NAME = "cursor-highlighter"


def _start_overlay_process(language: str) -> subprocess.Popen | None:
    """Lanza el proceso overlay si todavia no hay uno corriendo. None si ya habia uno."""
    if overlay_running():
        return None
    process = subprocess.Popen([sys.executable, "-m", "cursor_highlighter.overlay.engine"])

    deadline = time.monotonic() + OVERLAY_START_TIMEOUT_S
    while time.monotonic() < deadline:
        if overlay_running():
            return process
        time.sleep(OVERLAY_POLL_INTERVAL_S)

    raise RuntimeError(tr("error.overlay_timeout", language))


def _warn_if_devices_unavailable(tray: TrayIcon, language: str) -> None:
    """Avisa por notificacion del sistema si falta permiso de /dev/input.

    El chequeo real que importa para el highlight corre en el proceso overlay
    (otro EvdevReader), pero ese proceso es una QGuiApplication con
    layer-shell forzado y no puede mostrar UI. Repetimos el escaneo, barato
    (solo abre/cierra descriptores), en este proceso para poder avisarle al
    usuario con el tray, que si tiene QSystemTrayIcon.showMessage.
    """
    devices = discover_devices()
    for mouse in devices.mice:
        mouse.close()
    if not devices.permission_errors:
        return
    tray.showMessage(
        tr("app.name", language),
        tr("warn.devices_unavailable", language),
        QSystemTrayIcon.MessageIcon.Warning,
        10000,
    )


def main() -> int:
    app = QApplication(sys.argv)
    # Sin esto, KWin no puede vincular las ventanas con el .desktop instalado
    # y cae a un icono generico (el logo de Wayland) en vez de Icon=input-mouse.
    app.setDesktopFileName(DESKTOP_FILE_NAME)
    icon = QIcon.fromTheme(ICON_NAME)
    if icon.isNull():
        icon = QIcon.fromTheme(ICON_FALLBACK)
    app.setWindowIcon(icon)
    app.setStyleSheet(DARK_STYLESHEET)
    # El overlay y las preferencias se pueden cerrar/ocultar sin que eso cierre
    # la app: solo el tray decide cuando salir.
    app.setQuitOnLastWindowClosed(False)

    store = SettingsStore()
    language = store.language()

    try:
        overlay_process = _start_overlay_process(language)
        # Se carga (o recarga) recien ahora, con el bridge DBus del overlay ya
        # registrado y escuchando: si el script de KWin empezara a mandar
        # CursorMoved antes de que exista un listener, esos eventos se
        # pierden en el aire.
        reload_bridge_script()
    except RuntimeError as error:
        QMessageBox.critical(None, tr("app.name", language), str(error))
        return 1

    overlay = OverlayClient()
    settings_window = SettingsWindow(store, overlay)

    def show_preferences() -> None:
        settings_window.refresh()
        settings_window.show()
        settings_window.raise_()
        settings_window.activateWindow()

    def quit_app() -> None:
        if overlay_process is not None:
            overlay_process.terminate()
        app.quit()

    tray = TrayIcon(
        on_toggle=overlay.toggle_highlight, on_preferences=show_preferences, on_quit=quit_app, language=language
    )
    tray.show()
    _warn_if_devices_unavailable(tray, language)

    show_preferences()  # pedido: al iniciar la app, mostrar la interfaz de preferencias

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
