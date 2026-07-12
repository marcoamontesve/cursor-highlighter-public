# Cursor Highlighter

Highlights your cursor and animates clicks on **KDE Plasma Wayland**. Built
for tutorials, streams, presentations, or recorded lessons, where it's easy
to lose track of the mouse on screen.

It's free and open source. If it's useful to you and you'd like to support
the project, there's a tip jar here: [ko-fi.com/marcoamontesve](https://ko-fi.com/marcoamontesve) ☕

## Features

- Overlay always on top of every window (layer-shell), without stealing focus
- Ring animation on left/right click, with its own color for each
- **Profiles**: 4 built-in themes (Classic, Neon, Minimal, High contrast) +
  your own profiles you can save/rename/delete from Preferences
- Global shortcuts: **F8** shows/hides the highlight, **F9** cycles to the
  next profile
- Tray icon to toggle, open preferences, or quit
- **English and Spanish** interface, switchable from Preferences

## Requirements

- KDE Plasma in a **Wayland** session (doesn't work on X11 or other desktops)
- Python 3.10+
- Being in the system's `input` group so clicks get detected:
  ```bash
  sudo usermod -aG input $USER
  ```
  (log out and back in for it to take effect)

## Installation

```bash
git clone https://github.com/marcoamontesve/cursor-highlighter-public.git
cd cursor-highlighter-public
bash scripts/install.sh
```

Then look for "Cursor Highlighter" in your application launcher, or run
`.venv/bin/cursor-highlighter` directly.

## License

[MIT](LICENSE)
