"""Carga/recarga kwin/cursor_bridge.js en KWin via org.kde.kwin.Scripting (DBus).

No requiere kpackagetool6 ni reiniciar KWin: el script se (re)carga en cada arranque
de la app, asi que un `dnf update` o una edicion del .js se reflejan con solo
reiniciar la app Python.
"""

from pathlib import Path

from PyQt6.QtDBus import QDBusConnection, QDBusInterface, QDBusReply

KWIN_SERVICE = "org.kde.KWin"
SCRIPTING_PATH = "/Scripting"
SCRIPTING_INTERFACE = "org.kde.kwin.Scripting"
PLUGIN_NAME = "cursor-highlighter-bridge"

SCRIPT_PATH = Path(__file__).resolve().parents[3] / "kwin" / "cursor_bridge.js"


class KWinBridgeError(RuntimeError):
    pass


def _scripting_interface() -> QDBusInterface:
    bus = QDBusConnection.sessionBus()
    if not bus.isConnected():
        raise KWinBridgeError("No hay conexion al bus de sesion DBus.")
    iface = QDBusInterface(KWIN_SERVICE, SCRIPTING_PATH, SCRIPTING_INTERFACE, bus)
    if not iface.isValid():
        raise KWinBridgeError(
            "No se pudo hablar con org.kde.KWin. ¿Estás en una sesión Wayland de "
            "KDE Plasma? (KWin no responde en el bus de sesión)"
        )
    return iface


def reload_bridge_script() -> None:
    """Descarga (si estaba) y vuelve a cargar cursor_bridge.js en KWin."""
    if not SCRIPT_PATH.is_file():
        raise KWinBridgeError(f"No existe el script de KWin: {SCRIPT_PATH}")

    iface = _scripting_interface()

    loaded = QDBusReply(iface.call("isScriptLoaded", PLUGIN_NAME))
    if loaded.isValid() and loaded.value():
        unload = QDBusReply(iface.call("unloadScript", PLUGIN_NAME))
        if not unload.isValid():
            raise KWinBridgeError(f"unloadScript fallo: {unload.error().message()}")

    load = QDBusReply(iface.call("loadScript", str(SCRIPT_PATH), PLUGIN_NAME))
    if not load.isValid():
        raise KWinBridgeError(f"loadScript fallo: {load.error().message()}")
    script_id = load.value()
    if script_id < 0:
        raise KWinBridgeError(f"loadScript devolvio id invalido: {script_id}")

    start = QDBusReply(iface.call("start"))
    if not start.isValid():
        raise KWinBridgeError(f"start fallo: {start.error().message()}")


if __name__ == "__main__":
    reload_bridge_script()
    print(f"Script cargado: {SCRIPT_PATH}")
