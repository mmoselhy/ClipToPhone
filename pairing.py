import qrcode
from PIL import Image, ImageTk
import tkinter as tk

def show_clipboard_qr(content):
    text_preview = content[:50] + "..." if len(content) > 50 else content

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(content)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    root = tk.Tk()
    root.title("Clipboard QR Code")

    img_resized = img.resize((300, 300))
    photo = ImageTk.PhotoImage(img_resized)

    label_qr = tk.Label(root, image=photo)
    label_qr.pack(pady=10)

    label_text = tk.Label(root, text=f"Content: {text_preview}", font=("Arial", 10), wraplength=300)
    label_text.pack(pady=5)

    root.mainloop()
