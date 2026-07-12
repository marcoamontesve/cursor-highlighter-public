# Cursor Highlighter

Resalta el cursor y anima los clicks en **KDE Plasma Wayland**. Pensado para
tutoriales, streams, presentaciones o clases grabadas, donde es fácil perder
de vista el mouse en pantalla.

## Features

- Overlay siempre encima de todas las ventanas (layer-shell), sin robar foco
- Animación de aro al hacer click izquierdo/derecho, con color propio para cada uno
- **Perfiles**: 4 temas de fábrica (Clásico, Neón, Minimal, Alto contraste) +
  perfiles propios que guardás/renombrás/borrás desde Preferencias
- Atajos globales: **F8** muestra/oculta el highlight, **F9** cicla al
  siguiente perfil
- Ícono de bandeja para togglear, abrir preferencias o salir

## Requisitos

- KDE Plasma en sesión **Wayland** (no funciona en X11 ni en otros escritorios)
- Python 3.10+
- Estar en el grupo `input` del sistema para que se detecten los clicks:
  ```bash
  sudo usermod -aG input $USER
  ```
  (cerrá sesión y volvé a entrar para que tome efecto)

## Instalación

```bash
git clone https://github.com/marcoamontesve/cursor-highlighter.git
cd cursor-highlighter
bash scripts/install.sh
```

Después buscá "Cursor Highlighter" en el lanzador de aplicaciones, o corré
`.venv/bin/cursor-highlighter` directo.

## Nota

La interfaz está en español. Si te sirve y querés traducirla, un PR es
bienvenido.

## Licencia

[MIT](LICENSE)
