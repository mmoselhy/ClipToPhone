import threading
import logging

import pystray
from PIL import Image, ImageDraw
import keyboard
import pyperclip

from qr_popup import show_qr_popup

logger = logging.getLogger(__name__)

HOTKEY = "ctrl+alt+p"


def create_icon_image():
    """Create a 64x64 tray icon with a mini QR-code pattern."""
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Dark gray rounded background
    draw.rounded_rectangle([4, 4, 60, 60], radius=10, fill=(50, 50, 50, 255))

    # Mini QR pattern: 3x3 checkerboard of white squares
    cell = 12
    ox, oy = 14, 14
    pattern = [[1, 0, 1], [0, 1, 0], [1, 0, 1]]
    for r, row in enumerate(pattern):
        for c, filled in enumerate(row):
            if filled:
                x = ox + c * (cell + 2)
                y = oy + r * (cell + 2)
                draw.rectangle([x, y, x + cell, y + cell], fill=(255, 255, 255, 255))

    return img


def on_send_clipboard(icon, item):
    """Read clipboard and show QR popup in a separate thread."""
    try:
        content = pyperclip.paste()
    except Exception as e:
        logger.error("Failed to read clipboard: %s", e)
        _notify(icon, "Could not read clipboard")
        return

    if not content or not content.strip():
        _notify(icon, "Clipboard is empty")
        return

    t = threading.Thread(target=show_qr_popup, args=(content.strip(),), daemon=True)
    t.start()


def _notify(icon, message):
    """Show a brief tray notification."""
    try:
        icon.notify(message, "ClipToPhone")
    except Exception:
        logger.warning("Notification failed: %s", message)


def on_exit(icon, item):
    keyboard.unhook_all()
    icon.stop()


def setup_tray():
    icon = pystray.Icon("ClipToPhone", create_icon_image(), "ClipToPhone")
    icon.menu = pystray.Menu(
        pystray.MenuItem(
            "Send to Phone  (Ctrl+Alt+P)", on_send_clipboard, default=True
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit),
    )

    keyboard.add_hotkey(HOTKEY, lambda: on_send_clipboard(icon, None))
    return icon


def run_tray():
    icon = setup_tray()
    icon.run()
