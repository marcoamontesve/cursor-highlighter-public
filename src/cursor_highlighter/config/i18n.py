"""Textos de la interfaz en espanol/ingles.

El idioma elegido se persiste en SettingsStore, pero no se re-traduce en
vivo: cambiar el idioma pide reiniciar la app para que se refleje en todos
lados (bandeja, ventana de preferencias). Es una simplificacion deliberada
frente a reescribir cada widget ya construido.
"""

LANGUAGE_ES = "es"
LANGUAGE_EN = "en"
DEFAULT_LANGUAGE = LANGUAGE_EN

_STRINGS = {
    LANGUAGE_ES: {
        "app.name": "Cursor Highlighter",
        "window.title": "Preferencias — Cursor Highlighter",
        "group.language": "Idioma",
        "group.profile": "Perfil",
        "group.appearance": "Aspecto del cursor",
        "group.clicks": "Colores de click",
        "group.shortcut": "Atajo de teclado",
        "profile.save": "Guardar como nuevo...",
        "profile.rename": "Renombrar...",
        "profile.delete": "Eliminar",
        "profile.classic": "Clásico",
        "profile.neon": "Neón",
        "profile.minimal": "Minimal",
        "profile.high_contrast": "Alto contraste",
        "field.shape": "Forma:",
        "field.size": "Tamaño:",
        "field.opacity": "Opacidad:",
        "field.color": "Color:",
        "field.ring_thickness": "Grosor del anillo:",
        "field.left_click": "Click izquierdo:",
        "field.right_click": "Click derecho:",
        "shape.circle": "Círculo relleno",
        "shape.ring": "Anillo",
        "shortcut.info": (
            "El highlight se muestra/oculta con <b>F8</b>, y <b>F9</b> cicla al "
            "siguiente perfil — ambos son atajos globales registrados en KWin."
        ),
        "button.restore": "Restaurar valores por defecto",
        "button.donate": "Donar",
        "button.close": "Cerrar",
        "dialog.save_profile.title": "Guardar perfil",
        "dialog.save_profile.label": "Nombre del perfil:",
        "dialog.rename_profile.title": "Renombrar perfil",
        "dialog.rename_profile.label": "Nuevo nombre:",
        "dialog.builtin_name_taken": '"{name}" es un perfil de fábrica, elegí otro nombre.',
        "dialog.overwrite_profile": 'Ya existe un perfil "{name}". ¿Sobreescribirlo?',
        "dialog.name_taken": 'Ya existe un perfil llamado "{name}".',
        "dialog.delete_profile": '¿Eliminar el perfil "{name}"?',
        "dialog.color_picker": "Elegir color",
        "tray.toggle": "Mostrar/Ocultar highlight (F8)",
        "tray.preferences": "Preferencias...",
        "tray.quit": "Salir",
        "warn.devices_unavailable": (
            "No se detectan clicks: falta permiso para leer el mouse en /dev/input.\n"
            "Corré 'sudo usermod -aG input $USER' y volvé a iniciar sesión."
        ),
        "error.overlay_timeout": "El proceso overlay no respondió a tiempo por DBus.",
        "language.restart_notice": (
            "El idioma se aplica del todo al reiniciar la app (bandeja incluida). "
            "Volvé a abrirla cuando quieras."
        ),
    },
    LANGUAGE_EN: {
        "app.name": "Cursor Highlighter",
        "window.title": "Preferences — Cursor Highlighter",
        "group.language": "Language",
        "group.profile": "Profile",
        "group.appearance": "Cursor appearance",
        "group.clicks": "Click colors",
        "group.shortcut": "Keyboard shortcut",
        "profile.save": "Save as new...",
        "profile.rename": "Rename...",
        "profile.delete": "Delete",
        "profile.classic": "Classic",
        "profile.neon": "Neon",
        "profile.minimal": "Minimal",
        "profile.high_contrast": "High contrast",
        "field.shape": "Shape:",
        "field.size": "Size:",
        "field.opacity": "Opacity:",
        "field.color": "Color:",
        "field.ring_thickness": "Ring thickness:",
        "field.left_click": "Left click:",
        "field.right_click": "Right click:",
        "shape.circle": "Filled circle",
        "shape.ring": "Ring",
        "shortcut.info": (
            "The highlight shows/hides with <b>F8</b>, and <b>F9</b> cycles to the "
            "next profile — both are global shortcuts registered in KWin."
        ),
        "button.restore": "Restore defaults",
        "button.donate": "Donate",
        "button.close": "Close",
        "dialog.save_profile.title": "Save profile",
        "dialog.save_profile.label": "Profile name:",
        "dialog.rename_profile.title": "Rename profile",
        "dialog.rename_profile.label": "New name:",
        "dialog.builtin_name_taken": '"{name}" is a built-in profile, pick another name.',
        "dialog.overwrite_profile": 'A profile named "{name}" already exists. Overwrite it?',
        "dialog.name_taken": 'A profile named "{name}" already exists.',
        "dialog.delete_profile": 'Delete the profile "{name}"?',
        "dialog.color_picker": "Pick a color",
        "tray.toggle": "Show/Hide highlight (F8)",
        "tray.preferences": "Preferences...",
        "tray.quit": "Quit",
        "warn.devices_unavailable": (
            "Clicks aren't being detected: missing permission to read the mouse in /dev/input.\n"
            "Run 'sudo usermod -aG input $USER' and log back in."
        ),
        "error.overlay_timeout": "The overlay process didn't respond in time over DBus.",
        "language.restart_notice": (
            "The language fully applies after restarting the app (tray included). "
            "Reopen it whenever you're ready."
        ),
    },
}


def tr(key: str, language: str) -> str:
    strings = _STRINGS.get(language, _STRINGS[DEFAULT_LANGUAGE])
    return strings.get(key, _STRINGS[DEFAULT_LANGUAGE].get(key, key))
