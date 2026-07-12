"""Bridge DBus: expone org.cursorhighlighter.App, llamado por kwin/cursor_bridge.js.

Bridge (QObject) emite senales Qt (cursorMoved, hotkeyTriggered) que el resto de
la app conecta a lo que corresponda (CursorState, toggles de overlays, etc).
BridgeAdaptor es el QDBusAbstractAdaptor que traduce las llamadas DBus entrantes
a esas senales.
"""

import sys

from PyQt6.QtCore import QObject, pyqtClassInfo, pyqtSignal, pyqtSlot
from PyQt6.QtDBus import QDBusAbstractAdaptor, QDBusConnection

SERVICE_NAME = "org.cursorhighlighter.App"
OBJECT_PATH = "/org/cursorhighlighter/Bridge"
INTERFACE_NAME = "org.cursorhighlighter.Bridge1"

HOTKEY_TOGGLE_HIGHLIGHT = "toggle_highlight"
HOTKEY_NEXT_PROFILE = "next_profile"


class Bridge(QObject):
    cursorMoved = pyqtSignal(int, int)
    hotkeyTriggered = pyqtSignal(str)

    # Emitidos cuando el proceso de preferencias (otro proceso, ver
    # kwin_bridge/client.py) pide cambiar la apariencia del overlay en vivo.
    # Van por DBus y no por memoria compartida porque el overlay necesita
    # QT_WAYLAND_SHELL_INTEGRATION=layer-shell, que Qt aplica a TODAS las
    # ventanas del proceso: si tray/preferencias vivieran en el mismo
    # proceso, tambien saldrian como layer-shell (sin decoraciones, sin
    # tamano propio). Por eso corren en procesos separados.
    shapeChangeRequested = pyqtSignal(str)
    sizeChangeRequested = pyqtSignal(int)
    opacityChangeRequested = pyqtSignal(float)
    colorChangeRequested = pyqtSignal(str)
    ringThicknessChangeRequested = pyqtSignal(int)
    leftClickColorChangeRequested = pyqtSignal(str)
    rightClickColorChangeRequested = pyqtSignal(str)


@pyqtClassInfo("D-Bus Interface", INTERFACE_NAME)
class BridgeAdaptor(QDBusAbstractAdaptor):
    def __init__(self, bridge: Bridge):
        super().__init__(bridge)
        self.setAutoRelaySignals(True)
        self._bridge = bridge

    @pyqtSlot(int, int)
    def CursorMoved(self, x: int, y: int) -> None:
        self._bridge.cursorMoved.emit(x, y)

    @pyqtSlot(str)
    def HotkeyTriggered(self, name: str) -> None:
        self._bridge.hotkeyTriggered.emit(name)

    @pyqtSlot(str)
    def SetShape(self, shape: str) -> None:
        self._bridge.shapeChangeRequested.emit(shape)

    @pyqtSlot(int)
    def SetSize(self, size: int) -> None:
        self._bridge.sizeChangeRequested.emit(size)

    @pyqtSlot(float)
    def SetOpacity(self, opacity: float) -> None:
        self._bridge.opacityChangeRequested.emit(opacity)

    @pyqtSlot(str)
    def SetColor(self, color: str) -> None:
        self._bridge.colorChangeRequested.emit(color)

    @pyqtSlot(int)
    def SetRingThickness(self, thickness: int) -> None:
        self._bridge.ringThicknessChangeRequested.emit(thickness)

    @pyqtSlot(str)
    def SetLeftClickColor(self, color: str) -> None:
        self._bridge.leftClickColorChangeRequested.emit(color)

    @pyqtSlot(str)
    def SetRightClickColor(self, color: str) -> None:
        self._bridge.rightClickColorChangeRequested.emit(color)


def register_bridge(bridge: Bridge) -> bool:
    """Registra bridge en org.cursorhighlighter.App. False si ya hay otra instancia."""
    BridgeAdaptor(bridge)
    bus = QDBusConnection.sessionBus()
    if not bus.registerObject(OBJECT_PATH, bridge):
        return False
    if not bus.registerService(SERVICE_NAME):
        return False
    return True


def main() -> None:
    """Standalone: registra el bridge e imprime todo lo que llega (debug manual)."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    bridge = Bridge()
    bridge.cursorMoved.connect(lambda x, y: print(f"cursor: {x}, {y}", flush=True))
    bridge.hotkeyTriggered.connect(lambda name: print(f"hotkey: {name}", flush=True))

    if not register_bridge(bridge):
        print(f"ERROR: {SERVICE_NAME} ya esta en uso (¿otra instancia corriendo?)", file=sys.stderr)
        sys.exit(1)

    print(f"Escuchando en {SERVICE_NAME}{OBJECT_PATH} ...", flush=True)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
