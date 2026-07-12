"""Persiste perfiles de apariencia del highlight entre sesiones (QSettings, ~/.config).

Un perfil es un dict con los campos de apariencia (shape/size/opacity/color/
ring_thickness/left_click_color/right_click_color). Hay perfiles built-in
("temas" de fabrica, fijos en código, no editables) y perfiles custom que el
usuario crea a partir del estado actual. Los custom se guardan serializados
como JSON en una sola key de QSettings, ya que el formato INI no maneja bien
estructuras anidadas. Ademas se persiste cual es el perfil activo, para que
el proceso overlay (que via hotkey puede ciclar de perfil sin pasar por la
ventana de Preferencias) y el proceso principal vean siempre el mismo estado.
"""

import json

from PyQt6.QtCore import QSettings

ORG = "cursor-highlighter"
APP = "cursor-highlighter"

SHAPE_CIRCLE = "circle"
SHAPE_RING = "ring"

FIELDS = (
    "shape",
    "size",
    "opacity",
    "color",
    "ring_thickness",
    "left_click_color",
    "right_click_color",
)

BUILTIN_PROFILES = {
    "Clásico": {
        "shape": SHAPE_CIRCLE,
        "size": 60,
        "opacity": 0.6,
        "color": "#ff5555",
        "ring_thickness": 4,
        "left_click_color": "#4a9eff",
        "right_click_color": "#4aff8f",
    },
    "Neón": {
        "shape": SHAPE_RING,
        "size": 70,
        "opacity": 0.9,
        "color": "#ff00e6",
        "ring_thickness": 6,
        "left_click_color": "#00fff2",
        "right_click_color": "#eaff00",
    },
    "Minimal": {
        "shape": SHAPE_RING,
        "size": 36,
        "opacity": 0.5,
        "color": "#ffffff",
        "ring_thickness": 2,
        "left_click_color": "#ffffff",
        "right_click_color": "#ffffff",
    },
    "Alto contraste": {
        "shape": SHAPE_CIRCLE,
        "size": 90,
        "opacity": 1.0,
        "color": "#ffff00",
        "ring_thickness": 6,
        "left_click_color": "#ff0000",
        "right_click_color": "#00ff00",
    },
}

DEFAULT_PROFILE_NAME = "Clásico"
DEFAULTS = BUILTIN_PROFILES[DEFAULT_PROFILE_NAME]

_ACTIVE_PROFILE_KEY = "active_profile"
_CUSTOM_PROFILES_KEY = "custom_profiles_json"


class SettingsStore:
    def __init__(self):
        self._settings = QSettings(QSettings.Format.IniFormat, QSettings.Scope.UserScope, ORG, APP)

    # --- estado actual (valores del perfil activo) --------------------------

    def get(self, key: str):
        default = DEFAULTS[key]
        value = self._settings.value(key, default)
        if isinstance(default, float):
            return float(value)
        if isinstance(default, int):
            return int(value)
        return str(value)

    def set(self, key: str, value) -> None:
        self._settings.setValue(key, value)

    def all(self) -> dict:
        return {key: self.get(key) for key in FIELDS}

    # --- perfiles -------------------------------------------------------------

    def custom_profiles(self) -> dict[str, dict]:
        raw = self._settings.value(_CUSTOM_PROFILES_KEY, "")
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return {}

    def profile_names(self) -> list[str]:
        return list(BUILTIN_PROFILES) + list(self.custom_profiles())

    def is_builtin(self, name: str) -> bool:
        return name in BUILTIN_PROFILES

    def active_profile_name(self) -> str:
        return str(self._settings.value(_ACTIVE_PROFILE_KEY, DEFAULT_PROFILE_NAME))

    def profile_values(self, name: str) -> dict | None:
        if name in BUILTIN_PROFILES:
            return dict(BUILTIN_PROFILES[name])
        return self.custom_profiles().get(name)

    def apply_profile(self, name: str) -> dict | None:
        """Marca `name` como perfil activo y persiste sus valores como estado
        actual. Devuelve esos valores, o None si `name` no existe."""
        values = self.profile_values(name)
        if values is None:
            return None
        for key, value in values.items():
            self.set(key, value)
        self._settings.setValue(_ACTIVE_PROFILE_KEY, name)
        return values

    def save_custom_profile(self, name: str) -> None:
        """Guarda el estado actual (self.all()) como perfil custom `name`."""
        profiles = self.custom_profiles()
        profiles[name] = self.all()
        self._settings.setValue(_CUSTOM_PROFILES_KEY, json.dumps(profiles))
        self._settings.setValue(_ACTIVE_PROFILE_KEY, name)

    def rename_custom_profile(self, old_name: str, new_name: str) -> None:
        profiles = self.custom_profiles()
        if old_name not in profiles or new_name in profiles or new_name in BUILTIN_PROFILES:
            return
        profiles[new_name] = profiles.pop(old_name)
        self._settings.setValue(_CUSTOM_PROFILES_KEY, json.dumps(profiles))
        if self.active_profile_name() == old_name:
            self._settings.setValue(_ACTIVE_PROFILE_KEY, new_name)

    def delete_custom_profile(self, name: str) -> None:
        profiles = self.custom_profiles()
        if name not in profiles:
            return
        del profiles[name]
        self._settings.setValue(_CUSTOM_PROFILES_KEY, json.dumps(profiles))
        if self.active_profile_name() == name:
            self._settings.setValue(_ACTIVE_PROFILE_KEY, DEFAULT_PROFILE_NAME)
