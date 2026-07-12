"""Arma bridge + evdev + overlay QML. Este modulo es el entry point del
*proceso overlay* (`python -m cursor_highlighter.overlay.engine`), que
cursor_highlighter.app lanza como subproceso aparte del tray/preferencias.

Importante: QT_WAYLAND_SHELL_INTEGRATION debe estar seteado ANTES de crear la
QGuiApplication. Como el valor se fija a nivel de modulo (import time),
alcanza con importar este modulo antes de instanciar la app. No se puede
compartir proceso con tray/preferencias: ese env var hace que TODAS las
ventanas del proceso usen layer-shell (sin decoraciones ni tamano propio),
lo cual rompe un QDialog normal.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_WAYLAND_SHELL_INTEGRATION", "layer-shell")

from PyQt6.QtGui import QGuiApplication  # noqa: E402
from PyQt6.QtQml import QQmlApplicationEngine  # noqa: E402

from cursor_highlighter.config.store import SettingsStore  # noqa: E402
from cursor_highlighter.kwin_bridge.dbus_service import (  # noqa: E402
    HOTKEY_NEXT_PROFILE,
    HOTKEY_TOGGLE_HIGHLIGHT,
    SERVICE_NAME,
    Bridge,
    register_bridge,
)
from cursor_highlighter.input.evdev_reader import EvdevReader  # noqa: E402
from cursor_highlighter.overlay.cursor_state import CursorState  # noqa: E402

QML_DIR = Path(__file__).resolve().parent / "qml"


class HighlighterApp:
    """Agrupa el store de preferencias, bridge DBus, evdev, CursorState y el motor QML."""

    def __init__(self):
        self.store = SettingsStore()
        self.bridge = Bridge()
        self.cursor_state = CursorState()
        self._apply_stored_settings()
        self.bridge.cursorMoved.connect(self.cursor_state.updatePosition)
        self.bridge.shapeChangeRequested.connect(self.cursor_state.setShape)
        self.bridge.sizeChangeRequested.connect(self.cursor_state.setSize)
        self.bridge.opacityChangeRequested.connect(self.cursor_state.setOpacity)
        self.bridge.colorChangeRequested.connect(self.cursor_state.setColor)
        self.bridge.ringThicknessChangeRequested.connect(self.cursor_state.setRingThickness)
        self.bridge.leftClickColorChangeRequested.connect(self.cursor_state.setLeftClickColor)
        self.bridge.rightClickColorChangeRequested.connect(self.cursor_state.setRightClickColor)

        self.evdev_reader = EvdevReader()
        self.evdev_reader.leftClicked.connect(self.cursor_state.triggerLeftClick)
        self.evdev_reader.rightClicked.connect(self.cursor_state.triggerRightClick)
        self.evdev_reader.devicesUnavailable.connect(self._warn_devices_unavailable)

        self.qml_engine: QQmlApplicationEngine | None = None

    def _apply_stored_settings(self) -> None:
        self._apply_values_to_cursor_state(self.store.all())

    def _apply_values_to_cursor_state(self, values: dict) -> None:
        self.cursor_state.shape = values["shape"]
        self.cursor_state.size = values["size"]
        self.cursor_state.opacity = values["opacity"]
        self.cursor_state.color = values["color"]
        self.cursor_state.ringThickness = values["ring_thickness"]
        self.cursor_state.leftClickColor = values["left_click_color"]
        self.cursor_state.rightClickColor = values["right_click_color"]

    def next_profile(self) -> None:
        """Ciclado de perfiles vía atajo global (F9), sin pasar por Preferencias."""
        names = self.store.profile_names()
        if not names:
            return
        current = self.store.active_profile_name()
        index = names.index(current) if current in names else -1
        next_name = names[(index + 1) % len(names)]
        values = self.store.apply_profile(next_name)
        if values is not None:
            self._apply_values_to_cursor_state(values)

    @staticmethod
    def _warn_devices_unavailable(paths) -> None:
        print(
            f"AVISO: sin permiso para {len(paths)} dispositivo(s) de /dev/input. "
            "Corré: sudo usermod -aG input $USER ; luego cerrá sesión y volvé a entrar.",
            file=sys.stderr,
        )

    def start(self) -> bool:
        """Arranca evdev, registra el bridge DBus y carga el overlay QML. False si algo fallo."""
        self.evdev_reader.start()

        if not register_bridge(self.bridge):
            print(
                f"ERROR: {SERVICE_NAME} ya esta en uso (¿otra instancia de la app corriendo?)",
                file=sys.stderr,
            )
            return False

        self.qml_engine = QQmlApplicationEngine()
        self.qml_engine.rootContext().setContextProperty("cursorState", self.cursor_state)
        self.qml_engine.load(str(QML_DIR / "CursorHighlight.qml"))
        if not self.qml_engine.rootObjects():
            print("ERROR: no se pudo cargar CursorHighlight.qml", file=sys.stderr)
            return False
        return True

    def is_visible(self) -> bool:
        return bool(self.qml_engine.rootObjects()[0].isVisible())

    def toggle_visible(self) -> None:
        root = self.qml_engine.rootObjects()[0]
        root.setVisible(not root.isVisible())


def run_cursor_highlight() -> int:
    """Entry point del proceso overlay: arranca todo y togglea visibilidad por hotkey."""
    app = QGuiApplication(sys.argv)
    highlighter = HighlighterApp()
    if not highlighter.start():
        return 1
    highlighter.qml_engine.quit.connect(app.quit)

    def _on_hotkey(name: str) -> None:
        if name == HOTKEY_TOGGLE_HIGHLIGHT:
            highlighter.toggle_visible()
        elif name == HOTKEY_NEXT_PROFILE:
            highlighter.next_profile()

    highlighter.bridge.hotkeyTriggered.connect(_on_hotkey)
    return app.exec()


if __name__ == "__main__":
    sys.exit(run_cursor_highlight())
