# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**ClipToPhone** — A Windows system tray app that converts clipboard content to a QR code for phone scanning.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py

# Package to standalone .exe
pip install pyinstaller
pyinstaller --onefile --noconsole --collect-data customtkinter main.py
# Output: dist/main.exe
```

No test suite exists currently.

## Architecture

Three Python modules with a simple dependency chain:

```
main.py → tray.py → qr_popup.py
               ↓
          [clipboard/hotkey/tray via pyperclip, keyboard, pystray]
```

- **main.py**: Bootstrap with logging setup — calls `run_tray()`. Logs errors to `cliptophone.log`.
- **tray.py**: System tray icon (QR-pattern icon), Ctrl+Alt+P hotkey, tray menu. On trigger, reads clipboard via `pyperclip` and launches `show_qr_popup()` in a daemon thread. Uses `icon.notify()` for error feedback.
- **qr_popup.py**: `QRPopup` class using CustomTkinter. Frameless, draggable, dark/light mode, DPI-aware. Generates QR code (error correction M, auto-version), shows text preview and byte count. Dismissal via Escape, click-outside, close button, or 60s auto-close. Truncates content >2000 bytes with warning.

## Stack

- UI: `pystray` (tray), `customtkinter` (popup), `Pillow` (image)
- Input: `keyboard` (hotkey), `pyperclip` (clipboard)
- QR: `qrcode[pil]`
