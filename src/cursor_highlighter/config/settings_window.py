"""Ventana de preferencias: forma, tamano, opacidad, color y colores de click.

Los cambios se aplican en vivo sobre CursorState (se ven en el overlay al
instante) y se persisten en SettingsStore en cada edicion, sin un boton
"Guardar" separado: lo que ves es lo que va a quedar la proxima vez que abras
la app.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMessageBox,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from cursor_highlighter.config.i18n import LANGUAGE_EN, LANGUAGE_ES, tr
from cursor_highlighter.config.store import (
    BUILTIN_PROFILES,
    DEFAULT_PROFILE_ID,
    SHAPE_CIRCLE,
    SHAPE_RING,
    SettingsStore,
)
from cursor_highlighter.config.theme import BORDER
from cursor_highlighter.kwin_bridge.client import OverlayClient
from cursor_highlighter.tray.icon import KOFI_ICON_PATH, open_donate_page

SIZE_RANGE = (10, 300)
OPACITY_RANGE = (10, 100)  # porcentaje
RING_THICKNESS_RANGE = (1, 30)


class _ColorButton(QPushButton):
    """Boton cuadrado que muestra el color actual y abre un QColorDialog al click."""

    def __init__(self, color: str, language: str, parent: QWidget | None = None):
        super().__init__(parent)
        # objectName unico: un QSS local sin selector ("background-color: X")
        # se comporta como "* { ... }" y cascadea a los widgets hijos. Como el
        # QColorDialog se abre parentado a self.window() (no a este boton),
        # ya no hereda nada de este widget, pero igual escopeamos por id para
        # no pisar el estilo de otros botones comunes (Cerrar, Restaurar, etc).
        self.setObjectName(f"colorSwatch_{id(self)}")
        self.setFixedSize(36, 24)
        self._color = color
        self._language = language
        self._paint()

    def _paint(self) -> None:
        self.setStyleSheet(
            f"QPushButton#{self.objectName()} {{ background-color: {self._color}; border: 1px solid {BORDER}; }}"
        )

    def set_color(self, color: str) -> None:
        self._color = color
        self._paint()

    def pick(self) -> str | None:
        # parent=self.window() (la ventana de Preferencias), no self: si el
        # dialogo quedara parentado al boton, heredaria el QSS de arriba y se
        # pintaria entero del color elegido en vez de mantener el tema oscuro.
        chosen = QColorDialog.getColor(QColor(self._color), self.window(), tr("dialog.color_picker", self._language))
        if not chosen.isValid():
            return None
        self.set_color(chosen.name())
        return self._color


class SettingsWindow(QDialog):
    def __init__(self, store: SettingsStore, overlay: OverlayClient, parent=None):
        super().__init__(parent)
        self._language = store.language()
        language = self._language
        self.setWindowTitle(tr("window.title", language))
        self.setMinimumWidth(440)
        self._overlay = overlay
        self._store = store
        settings = store.all()

        layout = QVBoxLayout(self)

        language_box = QGroupBox(tr("group.language", language))
        language_layout = QHBoxLayout(language_box)
        self._language_combo = QComboBox()
        self._language_combo.addItem("Español", LANGUAGE_ES)
        self._language_combo.addItem("English", LANGUAGE_EN)
        self._language_combo.setCurrentIndex(self._language_combo.findData(language))
        self._language_combo.currentIndexChanged.connect(self._on_language_changed)
        language_layout.addWidget(self._language_combo)
        layout.addWidget(language_box)

        profile_box = QGroupBox(tr("group.profile", language))
        profile_layout = QHBoxLayout(profile_box)

        self._profile_combo = QComboBox()
        self._profile_combo.currentIndexChanged.connect(self._on_profile_selected)
        profile_layout.addWidget(self._profile_combo, 1)

        save_profile_button = QPushButton(tr("profile.save", language))
        save_profile_button.clicked.connect(self._on_save_profile)
        profile_layout.addWidget(save_profile_button)

        self._rename_profile_button = QPushButton(tr("profile.rename", language))
        self._rename_profile_button.clicked.connect(self._on_rename_profile)
        profile_layout.addWidget(self._rename_profile_button)

        self._delete_profile_button = QPushButton(tr("profile.delete", language))
        self._delete_profile_button.clicked.connect(self._on_delete_profile)
        profile_layout.addWidget(self._delete_profile_button)

        layout.addWidget(profile_box)
        self._reload_profile_combo(select=store.active_profile_id())

        appearance = QGroupBox(tr("group.appearance", language))
        form = QFormLayout(appearance)

        self._shape_combo = QComboBox()
        self._shape_combo.addItem(tr("shape.circle", language), SHAPE_CIRCLE)
        self._shape_combo.addItem(tr("shape.ring", language), SHAPE_RING)
        self._shape_combo.setCurrentIndex(self._shape_combo.findData(settings["shape"]))
        self._shape_combo.currentIndexChanged.connect(self._on_shape_changed)
        form.addRow(tr("field.shape", language), self._shape_combo)

        self._size_slider = self._add_slider_row(
            form, tr("field.size", language), SIZE_RANGE, settings["size"], self._on_size_changed
        )
        self._opacity_slider = self._add_slider_row(
            form, tr("field.opacity", language), OPACITY_RANGE, round(settings["opacity"] * 100), self._on_opacity_changed
        )

        self._color_button = _ColorButton(settings["color"], language)
        self._color_button.clicked.connect(self._on_color_clicked)
        form.addRow(tr("field.color", language), self._color_button)

        self._ring_slider = self._add_slider_row(
            form,
            tr("field.ring_thickness", language),
            RING_THICKNESS_RANGE,
            settings["ring_thickness"],
            self._on_ring_thickness_changed,
        )
        self._sync_ring_slider_enabled(settings["shape"])

        layout.addWidget(appearance)

        clicks = QGroupBox(tr("group.clicks", language))
        clicks_form = QFormLayout(clicks)

        self._left_color_button = _ColorButton(settings["left_click_color"], language)
        self._left_color_button.clicked.connect(self._on_left_click_color_clicked)
        clicks_form.addRow(tr("field.left_click", language), self._left_color_button)

        self._right_color_button = _ColorButton(settings["right_click_color"], language)
        self._right_color_button.clicked.connect(self._on_right_click_color_clicked)
        clicks_form.addRow(tr("field.right_click", language), self._right_color_button)

        layout.addWidget(clicks)

        shortcut = QGroupBox(tr("group.shortcut", language))
        shortcut_layout = QVBoxLayout(shortcut)

        shortcut_info = QLabel(tr("shortcut.info", language))
        shortcut_info.setWordWrap(True)
        shortcut_layout.addWidget(shortcut_info)

        layout.addWidget(shortcut)

        buttons = QHBoxLayout()
        restore_button = QPushButton(tr("button.restore", language))
        restore_button.clicked.connect(self._on_restore_defaults)
        buttons.addWidget(restore_button)
        donate_button = QPushButton(QIcon(str(KOFI_ICON_PATH)), tr("button.donate", language))
        donate_button.clicked.connect(open_donate_page)
        buttons.addWidget(donate_button)
        close_button = QPushButton(tr("button.close", language))
        close_button.clicked.connect(self.close)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    @staticmethod
    def _add_slider_row(form: QFormLayout, label: str, value_range: tuple[int, int], value: int, on_change) -> QSlider:
        row = QWidget()
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(0, 0, 0, 0)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(*value_range)
        slider.setValue(value)

        value_label = QLabel(str(value))
        value_label.setFixedWidth(36)

        def _changed(new_value: int) -> None:
            value_label.setText(str(new_value))
            on_change(new_value)

        slider.valueChanged.connect(_changed)
        row_layout.addWidget(slider)
        row_layout.addWidget(value_label)
        form.addRow(label, row)
        return slider

    def _sync_ring_slider_enabled(self, shape: str) -> None:
        self._ring_slider.setEnabled(shape == SHAPE_RING)

    def _on_shape_changed(self, index: int) -> None:
        shape = self._shape_combo.itemData(index)
        self._overlay.set_shape(shape)
        self._store.set("shape", shape)
        self._sync_ring_slider_enabled(shape)

    def _on_size_changed(self, value: int) -> None:
        self._overlay.set_size(value)
        self._store.set("size", value)

    def _on_opacity_changed(self, value: int) -> None:
        opacity = value / 100
        self._overlay.set_opacity(opacity)
        self._store.set("opacity", opacity)

    def _on_ring_thickness_changed(self, value: int) -> None:
        self._overlay.set_ring_thickness(value)
        self._store.set("ring_thickness", value)

    def _on_color_clicked(self) -> None:
        color = self._color_button.pick()
        if color is None:
            return
        self._overlay.set_color(color)
        self._store.set("color", color)

    def _on_left_click_color_clicked(self) -> None:
        color = self._left_color_button.pick()
        if color is None:
            return
        self._overlay.set_left_click_color(color)
        self._store.set("left_click_color", color)

    def _on_right_click_color_clicked(self) -> None:
        color = self._right_color_button.pick()
        if color is None:
            return
        self._overlay.set_right_click_color(color)
        self._store.set("right_click_color", color)

    def _on_restore_defaults(self) -> None:
        # No alcanza con seleccionar DEFAULT_PROFILE_ID en el combo: si ya
        # estaba seleccionado (aunque los sliders se hayan tocado a mano
        # después, sin guardar como perfil nuevo) currentIndexChanged no se
        # dispara y no pasaría nada. Aplicamos el perfil directo, sin pasar
        # por el evento del combo.
        values = self._store.apply_profile(DEFAULT_PROFILE_ID)
        if values is None:
            return
        self._reload_profile_combo(select=DEFAULT_PROFILE_ID)
        self._apply_profile_to_ui(values)

    def _on_language_changed(self, index: int) -> None:
        new_language = self._language_combo.itemData(index)
        if new_language == self._language:
            return
        self._store.set_language(new_language)
        QMessageBox.information(
            self, tr("app.name", new_language), tr("language.restart_notice", new_language)
        )

    def refresh(self) -> None:
        """Releé perfil activo y valores del store. Se llama cada vez que se
        muestra la ventana: si el overlay cambió de perfil por atajo global
        mientras esto estaba cerrado (o abierto de una sesión anterior), acá
        se refleja en vez de mostrar valores viejos."""
        self._reload_profile_combo(select=self._store.active_profile_id())
        self._apply_profile_to_ui(self._store.all())

    def _reload_profile_combo(self, select: str) -> None:
        self._profile_combo.blockSignals(True)
        self._profile_combo.clear()
        for profile_id in BUILTIN_PROFILES:
            self._profile_combo.addItem(tr(f"profile.{profile_id}", self._language), profile_id)
        custom_names = list(self._store.custom_profiles())
        if custom_names:
            self._profile_combo.insertSeparator(self._profile_combo.count())
            for name in custom_names:
                self._profile_combo.addItem(name, name)
        index = self._profile_combo.findData(select)
        self._profile_combo.setCurrentIndex(index if index >= 0 else 0)
        self._profile_combo.blockSignals(False)
        self._sync_profile_buttons_enabled()

    def _sync_profile_buttons_enabled(self) -> None:
        is_custom = not self._store.is_builtin(self._profile_combo.currentData())
        self._rename_profile_button.setEnabled(is_custom)
        self._delete_profile_button.setEnabled(is_custom)

    def _apply_profile_to_ui(self, values: dict) -> None:
        self._shape_combo.setCurrentIndex(self._shape_combo.findData(values["shape"]))
        self._size_slider.setValue(values["size"])
        self._opacity_slider.setValue(round(values["opacity"] * 100))
        self._ring_slider.setValue(values["ring_thickness"])

        self._color_button.set_color(values["color"])
        self._overlay.set_color(values["color"])
        self._store.set("color", values["color"])

        self._left_color_button.set_color(values["left_click_color"])
        self._overlay.set_left_click_color(values["left_click_color"])
        self._store.set("left_click_color", values["left_click_color"])

        self._right_color_button.set_color(values["right_click_color"])
        self._overlay.set_right_click_color(values["right_click_color"])
        self._store.set("right_click_color", values["right_click_color"])

    def _on_profile_selected(self, _index: int) -> None:
        values = self._store.apply_profile(self._profile_combo.currentData())
        if values is None:
            return
        self._apply_profile_to_ui(values)
        self._sync_profile_buttons_enabled()

    def _on_save_profile(self) -> None:
        name, ok = QInputDialog.getText(
            self, tr("dialog.save_profile.title", self._language), tr("dialog.save_profile.label", self._language)
        )
        name = name.strip()
        if not ok or not name:
            return
        if name in BUILTIN_PROFILES:
            QMessageBox.warning(
                self, tr("app.name", self._language), tr("dialog.builtin_name_taken", self._language).format(name=name)
            )
            return
        if name in self._store.custom_profiles():
            confirm = QMessageBox.question(
                self, tr("app.name", self._language), tr("dialog.overwrite_profile", self._language).format(name=name)
            )
            if confirm != QMessageBox.StandardButton.Yes:
                return
        self._store.save_custom_profile(name)
        self._reload_profile_combo(select=name)

    def _on_rename_profile(self) -> None:
        old_name = self._profile_combo.currentData()
        new_name, ok = QInputDialog.getText(
            self,
            tr("dialog.rename_profile.title", self._language),
            tr("dialog.rename_profile.label", self._language),
            text=old_name,
        )
        new_name = new_name.strip()
        if not ok or not new_name or new_name == old_name:
            return
        if new_name in BUILTIN_PROFILES or new_name in self._store.custom_profiles():
            QMessageBox.warning(
                self, tr("app.name", self._language), tr("dialog.name_taken", self._language).format(name=new_name)
            )
            return
        self._store.rename_custom_profile(old_name, new_name)
        self._reload_profile_combo(select=new_name)

    def _on_delete_profile(self) -> None:
        profile_id = self._profile_combo.currentData()
        confirm = QMessageBox.question(
            self, tr("app.name", self._language), tr("dialog.delete_profile", self._language).format(name=profile_id)
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return
        was_active = profile_id == self._store.active_profile_id()
        self._store.delete_custom_profile(profile_id)
        if was_active:
            # delete_custom_profile ya movió el "perfil activo" a
            # DEFAULT_PROFILE_ID, pero los valores en vivo (sliders,
            # overlay) siguen siendo los del perfil borrado hasta que los
            # reaplicamos nosotros.
            values = self._store.apply_profile(DEFAULT_PROFILE_ID)
            self._reload_profile_combo(select=DEFAULT_PROFILE_ID)
            if values is not None:
                self._apply_profile_to_ui(values)
        else:
            self._reload_profile_combo(select=self._store.active_profile_id())
