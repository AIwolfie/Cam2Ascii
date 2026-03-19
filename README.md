# Cam2Ascii 🎥➡️🔠

Transform your live webcam feed into real-time ASCII art! This project features two fully functional versions: a **high-performance Web UI** with a modern startup aesthetic and a **Python Terminal version** for classic terminal output.

## Features ✨

### 🌐 Web Version (`index.html`)
- **Real-Time ASCII Rendering**: Processes your live webcam feed completely in the browser.
- **Dynamic Rescaling**: Generates incredibly crisp ASCII text that perfectly scales to fit your full browser window continuously.
- **Picture-in-Picture (PiP) Window**: Keep an eye on the original camera feed in a clean, draggable floating window.
- **Toggle Features**: Easily toggle between Color Mode, Edge Detection, Face Tracking, and CRT Scanlines.
- **Modern Startup UI**: Stunning glassmorphic panels, beautiful typography (Inter & JetBrains Mono), and sleek dark mode aesthetic.

### 🐍 Python Terminal Version (`ascii_webcam.py`)
- **Direct Terminal Output**: See yourself formatted in classic Matrix-grid or simple text right precisely directly in your terminal/command prompt.

---

## Getting Started 🚀

### 1. Web Version (Browser UI)
The easiest to interact with. It requires zero installations and runs natively using modern web technologies!

1. Open this project directory in **VS Code**.
2. Install the **Live Server** extension (if you haven't already).
3. Open `index.html`.
4. Click the **"Go Live"** button in the bottom right corner of VS Code.
5. Grant camera permissions in your browser and enjoy!

### 2. Python Version (Terminal UI)
If you want that true hacker aesthetic running inside your command prompt, use the Python version.

1. Make sure you have **Python 3.x** installed.
2. Open your terminal/command prompt in the project's root directory.
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the webcam script:
   ```bash
   python ascii_webcam.py
   ```
   *(Alternatively, use `ascii_cam.py` for standard processing).*

---

## Tech Stack 🛠️
- **Web**: Vanilla HTML, CSS (`style.css`), JavaScript (`script.js`), WebRTC (Camera API), and Canvas API for image processing.
- **Python**: OpenCV (`cv2`) or relevant dependencies listed in `requirements.txt` for processing video stream into terminal characters.

## License
MIT License