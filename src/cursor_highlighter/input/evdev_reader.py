"""Lee eventos crudos de mouse via evdev en un thread aparte.

Emite senales Qt (conexion automatica en cola hacia el hilo principal, ya que
el QObject vive ahi aunque _run() corra en otro thread). Si no hay dispositivos
accesibles (falta el grupo 'input' o no se relogueo todavia), no crashea: emite
devicesUnavailable y sigue con la app funcionando sin clicks/teclas.
"""

from __future__ import annotations

import logging
import selectors
import threading

from evdev import ecodes
from PyQt6.QtCore import QObject, pyqtSignal

from cursor_highlighter.input.device_discovery import discover_devices

logger = logging.getLogger(__name__)


class EvdevReader(QObject):
    leftClicked = pyqtSignal()  # solo el press (value == 1), no interesa el release
    rightClicked = pyqtSignal()
    devicesUnavailable = pyqtSignal(list)  # rutas sin permiso

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def start(self) -> None:
        devices = discover_devices()
        if devices.permission_errors:
            self.devicesUnavailable.emit(devices.permission_errors)

        mice = devices.mice
        if not mice:
            logger.warning("No hay mouses accesibles; clicks deshabilitados.")
            return

        self._thread = threading.Thread(target=self._run, args=(mice,), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _run(self, devices) -> None:
        selector = selectors.DefaultSelector()
        for dev in devices:
            selector.register(dev, selectors.EVENT_READ)

        while not self._stop.is_set():
            for key, _mask in selector.select(timeout=0.5):
                dev = key.fileobj
                try:
                    for event in dev.read():
                        self._handle_event(event)
                except OSError:
                    selector.unregister(dev)

    def _handle_event(self, event) -> None:
        if event.type != ecodes.EV_KEY or event.value != 1:
            return  # solo nos interesa el press (value 1), no el release (0) ni el repeat (2)
        if event.code == ecodes.BTN_LEFT:
            self.leftClicked.emit()
        elif event.code == ecodes.BTN_RIGHT:
            self.rightClicked.emit()
