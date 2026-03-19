qimport cv2
import numpy as np
import colorama
from colorama import Fore, Style
import argparse
import sys
import shutil

# Cross-platform handling for non-blocking 'q' key exit
if sys.platform == "win32":
    import msvcrt
else:
    import select

# Initialize colorama for cross-platform ANSI escape sequence support
colorama.init()

# 70-character ASCII gradient from dark to light
ASCII_CHARS_STR = r" .'`^\",:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_CHARS = np.array(list(ASCII_CHARS_STR))
NUM_CHARS = len(ASCII_CHARS)


def parse_arguments():
    """Parses command-line arguments for configuration."""
    parser = argparse.ArgumentParser(description="Real-time multi-featured ASCII webcam renderer")
    parser.add_argument("-i", "--input", default="0", 
                        help="Webcam device index (e.g., 0) or video file path")
    parser.add_argument("-w", "--width", type=int, default=None, 
                        help="Output width in characters. Defaults to terminal width")
    parser.add_argument("--no-faces", action="store_true", 
                        help="Disable face detection to improve performance")
    parser.add_argument("--no-edges", action="store_true", 
                        help="Disable edge detection to improve performance")
    return parser.parse_args()


def is_quit_pressed():
    """Checks if 'q' was pressed in the terminal using non-blocking I/O."""
    if sys.platform == "win32":
        if msvcrt.kbhit() and msvcrt.getch().lower() == b'q':
            return True
    else:
        # Fallback for Unix-like systems
        dr, _, _ = select.select([sys.stdin], [], [], 0.0)
        if dr:
            if sys.stdin.read(1).lower() == 'q':
                return True
    return False


def map_pixels_to_ascii(gray_frame, color_mask, edges_mask=None):
    """
    Vectorized mapping of pixel intensities to character symbols,
    with performance-optimized inline color application.
    """
    # Normalize grayscale image (0-255) to index range (0 to NUM_CHARS-1)
    normalized = (gray_frame / 255.0) * (NUM_CHARS - 1)
    indices = normalized.astype(np.uint8)
    
    # Map index layout to full ASCII frame map
    ascii_frame = ASCII_CHARS[indices]
    
    # Overlay detected Canny edges with a pronounced character
    if edges_mask is not None:
        ascii_frame[edges_mask > 0] = '#'
        
    lines = []
    green_color = Fore.GREEN
    red_color = Fore.RED + Style.BRIGHT
    
    # Iterate through rows and rapidly apply colors. 
    # Using np.diff allows us to instantly cluster segments of the same color,
    # preventing lag induced by applying ANSI sequences per-character.
    for y in range(ascii_frame.shape[0]):
        row_chars = ascii_frame[y]
        row_colors = color_mask[y]
        
        # Find index boundaries where color toggle occurs
        changes = np.where(np.diff(row_colors) != 0)[0] + 1
        
        if len(changes) == 0:
            # Entire row is unified
            col = red_color if row_colors[0] == 1 else green_color
            lines.append(col + "".join(row_chars))
        else:
            # Row has multiple color zones (Matrix green / Face red bounds)
            line_str = green_color if row_colors[0] == 0 else red_color
            start = 0
            for change_idx in changes:
                line_str += "".join(row_chars[start:change_idx])
                col = red_color if row_colors[change_idx] == 1 else green_color
                line_str += col
                start = change_idx
            
            # Flush the rest of the row
            line_str += "".join(row_chars[start:])
            lines.append(line_str)
            
    return "\n".join(lines)


def main():
    args = parse_arguments()
    
    # Resolve numeric device indexes vs. file paths
    video_source = int(args.input) if args.input.isdigit() else args.input
    cap = cv2.VideoCapture(video_source)
    if not cap.isOpened():
        print(f"Error: Unable to open video source '{video_source}'.")
        sys.exit(1)

    # Initialize Haar Cascade Face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    use_faces = not args.no_faces and not face_cascade.empty()
    use_edges = not args.no_edges

    # Prevent complete screen clearing on each frame to entirely eliminate visual flicker.
    # We clear it once initially, then jump cursor dynamically instead.
    sys.stdout.write("\033[2J")
    
    try:
        out_height = 0
        while True:
            if is_quit_pressed():
                break

            ret, frame = cap.read()
            if not ret:
                break

            # Fetch up-to-date terminal boundaries
            term_cols, term_lines = shutil.get_terminal_size((80, 20))
            out_width = (args.width if args.width else term_cols) - 1
            
            orig_height, orig_width = frame.shape[:2]
            aspect_ratio = orig_height / orig_width
            
            # Character grids have approx 2x1 height-to-width ratio, hence the factor of 0.5
            out_height = int(out_width * aspect_ratio * 0.5)
            
            # Dynamically restrict height so it perfectly fills the terminal frame 
            # without triggering terminal scrolling artifacts.
            max_height = term_lines - 2
            if out_height > max_height:
                out_height = max_height
                out_width = int(out_height / (aspect_ratio * 0.5))
                
            if out_width <= 0 or out_height <= 0:
                continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Run Face Detection with spatial bounding & color mapping
            color_mask = np.zeros((out_height, out_width), dtype=np.uint8)
            if use_faces:
                face_detect_scale = 0.5
                small_gray = cv2.resize(gray, (0, 0), fx=face_detect_scale, fy=face_detect_scale)
                faces = face_cascade.detectMultiScale(small_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
                
                scale_x = out_width / (orig_width * face_detect_scale)
                scale_y = out_height / (orig_height * face_detect_scale)
                
                for (x, y, w, h) in faces:
                    sx = int(x * scale_x)
                    sy = int(y * scale_y)
                    sw = int(w * scale_x)
                    sh = int(h * scale_y)
                    
                    # Fill color mask bounds specifically targeting the detected face structure
                    color_mask[max(0, sy):min(out_height, sy+sh), max(0, sx):min(out_width, sx+sw)] = 1
                    
            gray_resized = cv2.resize(gray, (out_width, out_height))
            
            if use_edges:
                edges = cv2.Canny(gray_resized, 60, 120)
            else:
                edges = None
                
            ascii_output = map_pixels_to_ascii(gray_resized, color_mask, edges)
            
            # Reset cursor sequence to effectively overlay rendering locally.
            sys.stdout.write("\033[H" + ascii_output)
            sys.stdout.flush()

    finally:
        cap.release()
        # Cleanly return cursor output sequence to bottom so CLI prompts rest normally
        sys.stdout.write(f"\033[{out_height + 1};1H\n")
        sys.stdout.write(Style.RESET_ALL)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
