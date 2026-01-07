# ClipToPhone - Clipboard to QR Code Tool

A simple Windows tray application that displays your clipboard content as a QR code for easy scanning with your phone.

## Features

- System tray icon with menu: Send Clipboard to Phone, Exit
- Global hotkey: Ctrl+Alt+P to show QR code
- Displays clipboard text as a scannable QR code
- Lightweight and simple

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the application:
   ```
   python main.py
   ```

3. Copy text to your clipboard and press Ctrl+Alt+P or use the tray menu to display the QR code.

4. Scan the QR code with your phone's camera to view the text.

## Usage

1. Copy any text to your Windows clipboard
2. Press Ctrl+Alt+P or right-click the tray icon and select "Send Clipboard to Phone"
3. A window will open showing a QR code containing your clipboard text
4. Scan the QR code with your phone's camera
5. Manually copy the text on your phone if needed

## Packaging

To create a standalone .exe:

```
pip install pyinstaller
pyinstaller --onefile --noconsole main.py
```

The .exe will be in the `dist/` folder.

## Note

iOS does not allow automatic clipboard writing from QR codes for security reasons, so you'll need to manually copy the text after scanning.