"""Cliente DBus liviano: le pide al proceso overlay que cambie su apariencia
en vivo o togglee su visibilidad. Ver comentario en dbus_service.py sobre por
que overlay y control corren en procesos separados.
"""

from PyQt6.QtDBus import QDBusConnection, QDBusInterface

from cursor_highlighter.kwin_bridge.dbus_service import (
    HOTKEY_TOGGLE_HIGHLIGHT,
    INTERFACE_NAME,
    OBJECT_PATH,
    SERVICE_NAME,
)


def overlay_running() -> bool:
    reply = QDBusConnection.sessionBus().interface().isServiceRegistered(SERVICE_NAME)
    return bool(reply.value())


class OverlayClient:
    def __init__(self):
        bus = QDBusConnection.sessionBus()
        self._iface = QDBusInterface(SERVICE_NAME, OBJECT_PATH, INTERFACE_NAME, bus)

    def toggle_highlight(self) -> None:
        self._iface.asyncCall("HotkeyTriggered", HOTKEY_TOGGLE_HIGHLIGHT)

    def set_shape(self, shape: str) -> None:
        self._iface.asyncCall("SetShape", shape)

    def set_size(self, size: int) -> None:
        self._iface.asyncCall("SetSize", size)

    def set_opacity(self, opacity: float) -> None:
        self._iface.asyncCall("SetOpacity", opacity)

    def set_color(self, color: str) -> None:
        self._iface.asyncCall("SetColor", color)

    def set_ring_thickness(self, thickness: int) -> None:
        self._iface.asyncCall("SetRingThickness", thickness)

    def set_left_click_color(self, color: str) -> None:
        self._iface.asyncCall("SetLeftClickColor", color)

    def set_right_click_color(self, color: str) -> None:
        self._iface.asyncCall("SetRightClickColor", color)
