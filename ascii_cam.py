#!/usr/bin/env python3
# Instructions: Run this script softly from a terminal using: python ascii_cam.py
# Use "python ascii_cam.py -i video.mp4" for video file
# Press 'q' to exit.

import cv2
import numpy as np
import colorama
from colorama import Fore, Style
import argparse
import sys
import shutil

if sys.platform == "win32":
    import msvcrt
else:
    import select

colorama.init()

ASCII_CHARS_STR = r" .'`^\",:;Il!i~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
ASCII_CHARS = np.array(list(ASCII_CHARS_STR))
NUM_CHARS = len(ASCII_CHARS)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", default="0")
    parser.add_argument("-w", "--width", type=int, default=120)
    parser.add_argument("--no-faces", action="store_true")
    parser.add_argument("--no-edges", action="store_true")
    return parser.parse_args()

def is_quit_pressed():
    if sys.platform == "win32":
        return msvcrt.kbhit() and msvcrt.getch().lower() == b'q'
    dr, _, _ = select.select([sys.stdin], [], [], 0.0)
    if dr: return sys.stdin.read(1).lower() == 'q'
    return False

def map_pixels_to_ascii(gray_frame, color_mask, edges_mask=None):
    normalized = (gray_frame / 255.0) * (NUM_CHARS - 1)
    indices = normalized.astype(np.uint8)
    ascii_frame = ASCII_CHARS[indices]
    
    if edges_mask is not None:
        ascii_frame[edges_mask > 0] = '#'
        
    lines = []
    green_col = Fore.GREEN
    red_col = Fore.RED + Style.BRIGHT
    
    for y in range(ascii_frame.shape[0]):
        row_chars = ascii_frame[y]
        row_colors = color_mask[y]
        changes = np.where(np.diff(row_colors) != 0)[0] + 1
        
        if len(changes) == 0:
            lines.append((red_col if row_colors[0] == 1 else green_col) + "".join(row_chars))
        else:
            line_str = green_col if row_colors[0] == 0 else red_col
            start = 0
            for idx in changes:
                line_str += "".join(row_chars[start:idx])
                line_str += red_col if row_colors[idx] == 1 else green_col
                start = idx
            line_str += "".join(row_chars[start:])
            lines.append(line_str)
            
    return "\n".join(lines)

def main():
    args = parse_arguments()
    src = int(args.input) if args.input.isdigit() else args.input
    cap = cv2.VideoCapture(src)
    
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    use_faces = not args.no_faces and not face_cascade.empty()
    use_edges = not args.no_edges

    sys.stdout.write("\033[2J")
    
    try:
        out_height = 0
        while True:
            if is_quit_pressed(): break
            ret, frame = cap.read()
            if not ret: break

            t_cols, t_lines = shutil.get_terminal_size((80, 20))
            out_width = min(args.width, t_cols - 1)
            
            h, w = frame.shape[:2]
            aspect = h / w
            out_height = int(out_width * aspect * 0.5)
            
            max_h = t_lines - 2
            if out_height > max_h:
                out_height = max_h
                out_width = int(out_height / (aspect * 0.5))

            if out_width <= 0 or out_height <= 0: continue

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            color_mask = np.zeros((out_height, out_width), dtype=np.uint8)
            
            if use_faces:
                small = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
                faces = face_cascade.detectMultiScale(small, 1.1, 5, minSize=(30, 30))
                sx, sy = out_width / (w * 0.5), out_height / (h * 0.5)
                for (fx, fy, fw, fh) in faces:
                    color_mask[max(0, int(fy*sy)):min(out_height, int((fy+fh)*sy)),
                               max(0, int(fx*sx)):min(out_width, int((fx+fw)*sx))] = 1
                    
            gray_res = cv2.resize(gray, (out_width, out_height))
            edges = cv2.Canny(gray_res, 60, 120) if use_edges else None
            
            ascii_output = map_pixels_to_ascii(gray_res, color_mask, edges)
            sys.stdout.write("\033[H" + ascii_output)
            sys.stdout.flush()

    finally:
        cap.release()
        sys.stdout.write(f"\033[{out_height + 1};1H\n{Style.RESET_ALL}")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
