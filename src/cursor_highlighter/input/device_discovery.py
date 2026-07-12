"""Enumera /dev/input y detecta los mouses por capacidades (no por nombre).

No alcanza con abrir "el" mouse por nombre fijo: hay dispositivos secundarios
(ej. botones extra de un mouse gaming registrados como sub-dispositivo aparte)
que tambien hay que escuchar. Se filtra por capacidades EV_KEY.

Deliberadamente no abrimos teclados: la app no usa sus eventos (el atajo
global se maneja via KWin, no evdev), y leer el stream crudo de un teclado sin
necesitarlo es una superficie de permisos innecesaria para una utilidad que
solo resalta el cursor.
"""

from __future__ import annotations

import glob
import logging
import os
from dataclasses import dataclass, field

import evdev
from evdev import ecodes

logger = logging.getLogger(__name__)

MOUSE_BUTTON_CODES = {ecodes.BTN_LEFT, ecodes.BTN_RIGHT, ecodes.BTN_MIDDLE}


@dataclass
class DiscoveredDevices:
    mice: list[evdev.InputDevice] = field(default_factory=list)
    permission_errors: list[str] = field(default_factory=list)


def discover_devices() -> DiscoveredDevices:
    result = DiscoveredDevices()

    # No usamos evdev.list_devices(): filtra en silencio los dispositivos sin
    # permiso de lectura (via is_device -> os.access(R_OK|W_OK)), por lo que
    # PermissionError nunca llegaria a dispararse mas abajo. Enumeramos los
    # nodos nosotros mismos para poder detectar y avisar cuales fallan.
    for path in sorted(glob.glob("/dev/input/event*")):
        try:
            dev = evdev.InputDevice(path)
        except PermissionError:
            result.permission_errors.append(path)
            continue

        key_caps = set(dev.capabilities().get(ecodes.EV_KEY, []))

        if key_caps & MOUSE_BUTTON_CODES:
            result.mice.append(dev)
            logger.info("Mouse detectado: %s (%s)", dev.name, dev.path)
        else:
            dev.close()

    if result.permission_errors:
        user = os.environ.get("USER", "tu_usuario")
        logger.warning(
            "Sin permiso para leer %d dispositivo(s) de /dev/input "
            "(detección de clicks deshabilitada). "
            "Corré: sudo usermod -aG input %s ; luego cerrá sesión y volvé a entrar.",
            len(result.permission_errors),
            user,
        )

    return result
