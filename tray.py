import pystray
from PIL import Image, ImageDraw
import keyboard
import pyperclip
from tkinter import messagebox
from pairing import show_clipboard_qr

def create_icon():
    img = Image.new('RGB', (64, 64), color='blue')
    draw = ImageDraw.Draw(img)
    draw.text((20, 20), 'C', fill='white')
    return img

def on_send_clipboard(icon, item):
    content = pyperclip.paste()
    if not content or not content.strip():
        messagebox.showinfo("No Text", "No text in clipboard")
        return
    show_clipboard_qr(content)

def on_exit(icon, item):
    icon.stop()

def setup_tray():
    icon = pystray.Icon("ClipToPhone", create_icon(), "Clip to Phone")
    icon.menu = pystray.Menu(
        pystray.MenuItem("Send Clipboard to Phone", on_send_clipboard),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", on_exit)
    )

    # Register hotkey
    keyboard.add_hotkey('ctrl+alt+p', lambda: on_send_clipboard(icon, None))

    return icon

def run_tray():
    icon = setup_tray()
    icon.run()