import customtkinter as ctk
from PIL import Image
import qrcode
import logging
import re

logger = logging.getLogger(__name__)

# --- Constants ---
QR_MAX_BYTES = 2000
QR_DISPLAY_SIZE = 300
AUTO_CLOSE_MS = 60_000
FADE_DURATION_MS = 250
FADE_STEPS = 10
PREVIEW_MAX_CHARS = 120

URL_PATTERN = re.compile(r"^https?://\S+$", re.IGNORECASE)


class QRPopup:
    """Frameless CustomTkinter popup that displays clipboard content as a QR code."""

    def __init__(self, content: str):
        self.content = content
        self.original_byte_len = len(content.encode("utf-8"))
        self.is_url = bool(URL_PATTERN.match(content.strip()))
        self.truncated = False

        if self.original_byte_len > QR_MAX_BYTES:
            self.content = self._truncate_to_bytes(content, QR_MAX_BYTES)
            self.truncated = True

        self.window = None
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._auto_close_id = None

    def show(self):
        """Build and display the popup. Blocks until closed."""
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.window = ctk.CTk()
        self.window.title("ClipToPhone")
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)
        self.window.attributes("-alpha", 0.0)

        self._build_title_bar()
        self._build_qr_display()
        self._build_text_preview()
        self._build_status_bar()

        self.window.update_idletasks()
        self._center_on_screen()

        self.window.bind("<Escape>", lambda e: self._close())
        self.window.bind("<FocusOut>", self._on_focus_out)

        self._auto_close_id = self.window.after(AUTO_CLOSE_MS, self._close)
        self._fade_in(step=0)
        self.window.focus_force()
        self.window.mainloop()

    def _build_title_bar(self):
        title_bar = ctk.CTkFrame(self.window, height=36, corner_radius=0)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)

        title_label = ctk.CTkLabel(
            title_bar,
            text="  ClipToPhone",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="w",
        )
        title_label.pack(side="left", padx=(8, 0))

        close_btn = ctk.CTkButton(
            title_bar,
            text="\u2715",
            width=36,
            height=36,
            corner_radius=0,
            fg_color="transparent",
            hover_color=("#e81123", "#e81123"),
            font=ctk.CTkFont(size=14),
            command=self._close,
        )
        close_btn.pack(side="right")

        for widget in (title_bar, title_label):
            widget.bind("<ButtonPress-1>", self._start_drag)
            widget.bind("<B1-Motion>", self._on_drag)

    def _build_qr_display(self):
        try:
            qr = qrcode.QRCode(
                version=None,
                error_correction=qrcode.constants.ERROR_CORRECT_M,
                box_size=10,
                border=4,
            )
            qr.add_data(self.content)
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white")
            qr_img = qr_img.resize(
                (QR_DISPLAY_SIZE, QR_DISPLAY_SIZE),
                Image.NEAREST,
            )
        except Exception as e:
            logger.error("QR generation failed: %s", e)
            error_label = ctk.CTkLabel(
                self.window,
                text="Failed to generate QR code.\nContent may be invalid.",
                font=ctk.CTkFont(size=14),
                text_color=("#cc0000", "#ff4444"),
            )
            error_label.pack(pady=40, padx=20)
            return

        self._ctk_image = ctk.CTkImage(
            light_image=qr_img,
            dark_image=qr_img,
            size=(QR_DISPLAY_SIZE, QR_DISPLAY_SIZE),
        )

        qr_frame = ctk.CTkFrame(self.window, fg_color="white", corner_radius=8)
        qr_frame.pack(padx=20, pady=(12, 8))

        qr_label = ctk.CTkLabel(qr_frame, image=self._ctk_image, text="")
        qr_label.pack(padx=8, pady=8)

    def _build_text_preview(self):
        preview = self.content
        if len(preview) > PREVIEW_MAX_CHARS:
            preview = preview[:PREVIEW_MAX_CHARS] + "..."

        prefix = "URL: " if self.is_url else ""

        preview_label = ctk.CTkLabel(
            self.window,
            text=f"{prefix}{preview}",
            font=ctk.CTkFont(size=12),
            wraplength=QR_DISPLAY_SIZE + 20,
            justify="center",
            text_color=("gray30", "gray70"),
        )
        preview_label.pack(padx=20, pady=(0, 4))

    def _build_status_bar(self):
        char_count = len(self.content)
        byte_count = len(self.content.encode("utf-8"))
        status_parts = [f"{char_count} chars ({byte_count} bytes)"]

        if self.truncated:
            status_parts.append(f"Truncated from {self.original_byte_len} bytes")

        status_text = "  |  ".join(status_parts)
        text_color = ("#cc6600", "#ffaa00") if self.truncated else ("gray50", "gray60")

        ctk.CTkLabel(
            self.window,
            text=status_text,
            font=ctk.CTkFont(size=11),
            text_color=text_color,
        ).pack(padx=20, pady=(0, 4))

        ctk.CTkLabel(
            self.window,
            text="Scan with your phone camera  |  Esc to close",
            font=ctk.CTkFont(size=10),
            text_color=("gray60", "gray50"),
        ).pack(padx=20, pady=(0, 12))

    # --- Positioning ---
    def _center_on_screen(self):
        self.window.update_idletasks()
        w = self.window.winfo_reqwidth()
        h = self.window.winfo_reqheight()
        x = (self.window.winfo_screenwidth() - w) // 2
        y = (self.window.winfo_screenheight() - h) // 2
        self.window.geometry(f"+{x}+{y}")

    # --- Drag ---
    def _start_drag(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def _on_drag(self, event):
        x = self.window.winfo_x() + event.x - self._drag_start_x
        y = self.window.winfo_y() + event.y - self._drag_start_y
        self.window.geometry(f"+{x}+{y}")

    # --- Fade ---
    def _fade_in(self, step):
        if step <= FADE_STEPS:
            alpha = step / FADE_STEPS * 0.98
            self.window.attributes("-alpha", alpha)
            self.window.after(FADE_DURATION_MS // FADE_STEPS, self._fade_in, step + 1)

    def _fade_out_and_close(self, step=None):
        if step is None:
            step = FADE_STEPS
        if step >= 0:
            alpha = step / FADE_STEPS * 0.98
            self.window.attributes("-alpha", alpha)
            self.window.after(
                FADE_DURATION_MS // FADE_STEPS // 2,
                self._fade_out_and_close,
                step - 1,
            )
        else:
            self.window.destroy()

    # --- Dismissal ---
    def _on_focus_out(self, event):
        self.window.after(100, self._check_focus)

    def _check_focus(self):
        try:
            if not self.window.focus_get():
                self._close()
        except Exception:
            pass

    def _close(self):
        if self._auto_close_id:
            self.window.after_cancel(self._auto_close_id)
            self._auto_close_id = None
        self._fade_out_and_close()

    # --- Truncation ---
    @staticmethod
    def _truncate_to_bytes(text: str, max_bytes: int) -> str:
        encoded = text.encode("utf-8")
        if len(encoded) <= max_bytes:
            return text
        truncated = encoded[:max_bytes]
        return truncated.decode("utf-8", errors="ignore")


def show_qr_popup(content: str):
    """Show a QR code popup for the given content. Blocks until closed."""
    try:
        popup = QRPopup(content)
        popup.show()
    except Exception:
        logger.exception("Failed to show QR popup")
