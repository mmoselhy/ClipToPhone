import sys
import logging

from tray import run_tray

logging.basicConfig(
    filename="cliptophone.log",
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(message)s",
)

if __name__ == "__main__":
    try:
        run_tray()
    except Exception:
        logging.exception("Fatal error in ClipToPhone")
        sys.exit(1)
