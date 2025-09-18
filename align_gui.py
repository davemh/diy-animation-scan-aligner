import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
from align_pages import detect_three_holes, build_reference, align_page, draw_overlay
import cv2

stop_flag = False  # Global flag to cancel alignment

def browse_source():
    folder = filedialog.askdirectory(initialdir=source_var.get())
    if folder:
        source_var.set(folder)

def browse_destination():
    folder = filedialog.askdirectory(initialdir=dest_var.get())
    if folder:
        dest_var.set(folder)

def run_alignment_thread():
    global stop_flag
    stop_flag = False
    thread = threading.Thread(target=run_alignment, daemon=True)
    thread.start()

def cancel_alignment():
    global stop_flag
    stop_flag = True

def run_alignment():
    global stop_flag
    peg_pos = peg_var.get()
    src = source_var.get()
    dest = dest_var.get()
    debug = debug_var.get()
    preview = preview_var.get()
    try:
        delay = int(delay_var.get())
    except ValueError:
        messagebox.showerror("Error", "Preview delay must be an integer")
        return

    # List all images
    files = sorted([f for f in os.listdir(src) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))])
    if not files:
        messagebox.showerror("Error", "No images found in source folder")
        return

    os.makedirs(dest, exist_ok=True)
    reference = None

    progress_bar["maximum"] = len(files)
    progress_bar["value"] = 0

    for i, fname in enumerate(files, start=1):
        if stop_flag:
            messagebox.showinfo("Cancelled", "Alignment was cancelled by the user.")
            break

        in_path = os.path.join(src, fname)
        img = cv2.imread(in_path)
        if img is None:
            continue
        try:
            holes = detect_three_holes(img)
        except RuntimeError:
            continue
        if reference is None:
            reference = build_reference(holes, img.shape, peg_pos.lower())
        try:
            aligned, transformed = align_page(img, holes, reference)
        except RuntimeError:
            continue
        out_img = aligned
        if debug or preview:
            overlay = draw_overlay(aligned, holes, reference, transformed)
            out_img = overlay
        out_name = os.path.splitext(fname)[0] + ".png"
        cv2.imwrite(os.path.join(dest, out_name), out_img)

        progress_bar["value"] = i
        root.update_idletasks()  # refresh GUI

        if preview:
            disp = out_img.copy()
            cv2.putText(disp, fname, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 4)
            cv2.putText(disp, fname, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
            cv2.imshow("Preview", disp)
            key = cv2.waitKey(delay) & 0xFF
            if key == 27:  # ESC
                break

    if preview:
        cv2.destroyAllWindows()
    if not stop_flag:
        messagebox.showinfo("Done", "Alignment complete!")

# --- GUI setup ---
root = tk.Tk()
root.title("DIY Animation Scan Aligner")

peg_var = tk.StringVar(value="Top")
source_var = tk.StringVar(value="scans/")
dest_var = tk.StringVar(value="aligned/")
debug_var = tk.BooleanVar(value=False)
preview_var = tk.BooleanVar(value=False)
delay_var = tk.StringVar(value="500")

# Pegbar position
tk.Label(root, text="Pegbar position:").grid(row=0, column=0, sticky="w")
tk.Radiobutton(root, text="Top", variable=peg_var, value="Top").grid(row=0, column=1)
tk.Radiobutton(root, text="Bottom", variable=peg_var, value="Bottom").grid(row=0, column=2)

# Source directory
tk.Label(root, text="Source folder:").grid(row=1, column=0, sticky="w")
tk.Entry(root, textvariable=source_var, width=40).grid(row=1, column=1, columnspan=2)
tk.Button(root, text="Browse...", command=browse_source).grid(row=1, column=3)

# Destination directory
tk.Label(root, text="Destination folder:").grid(row=2, column=0, sticky="w")
tk.Entry(root, textvariable=dest_var, width=40).grid(row=2, column=1, columnspan=2)
tk.Button(root, text="Browse...", command=browse_destination).grid(row=2, column=3)

# Debug and Preview checkboxes
tk.Checkbutton(root, text="Debug overlay", variable=debug_var).grid(row=3, column=0, sticky="w")
tk.Checkbutton(root, text="Preview", variable=preview_var).grid(row=3, column=1, sticky="w")

# Preview delay
tk.Label(root, text="Preview delay (ms):").grid(row=4, column=0, sticky="w")
tk.Entry(root, textvariable=delay_var, width=10).grid(row=4, column=1, sticky="w")

# Progress bar
progress_bar = ttk.Progressbar(root, length=400)
progress_bar.grid(row=5, column=0, columnspan=4, pady=10)

# Run and Cancel buttons
tk.Button(root, text="Run Alignment", command=run_alignment_thread, bg="green", fg="white").grid(row=6, column=0, columnspan=2, pady=10)
tk.Button(root, text="Cancel", command=cancel_alignment, bg="red", fg="white").grid(row=6, column=2, columnspan=2, pady=10)

root.mainloop()
