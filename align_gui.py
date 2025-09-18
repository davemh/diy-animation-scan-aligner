#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import align_pages  # make sure align_pages.py is in the same folder

# ---------------- GUI Setup ---------------- #
root = tk.Tk()
root.title("DIY Animation Scan Aligner")
root.geometry("500x400")

# ---------- Peg Hole Position ---------- #
peg_frame = tk.LabelFrame(root, text="Peg Hole Position")
peg_frame.pack(padx=10, pady=10, fill="x")

peg_pos_var = tk.StringVar(value="top")
tk.Radiobutton(peg_frame, text="Top", variable=peg_pos_var, value="top").pack(side="left", padx=10, pady=5)
tk.Radiobutton(peg_frame, text="Bottom", variable=peg_pos_var, value="bottom").pack(side="left", padx=10, pady=5)

# ---------- Source Directory ---------- #
src_frame = tk.LabelFrame(root, text="Source Directory")
src_frame.pack(padx=10, pady=10, fill="x")

src_var = tk.StringVar(value="scans/")

def browse_src():
    folder = filedialog.askdirectory(initialdir=".", title="Select Source Folder")
    if folder:
        src_var.set(folder)

src_entry = tk.Entry(src_frame, textvariable=src_var, width=40)
src_entry.pack(side="left", padx=5, pady=5)
tk.Button(src_frame, text="Browse", command=browse_src).pack(side="left", padx=5, pady=5)

# ---------- Destination Directory ---------- #
dst_frame = tk.LabelFrame(root, text="Destination Directory")
dst_frame.pack(padx=10, pady=10, fill="x")

dst_var = tk.StringVar(value="aligned/")

def browse_dst():
    folder = filedialog.askdirectory(initialdir=".", title="Select Destination Folder")
    if folder:
        dst_var.set(folder)

dst_entry = tk.Entry(dst_frame, textvariable=dst_var, width=40)
dst_entry.pack(side="left", padx=5, pady=5)
tk.Button(dst_frame, text="Browse", command=browse_dst).pack(side="left", padx=5, pady=5)

# ---------- Progress Bar ---------- #
progress_frame = tk.LabelFrame(root, text="Progress")
progress_frame.pack(padx=10, pady=10, fill="x")

progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=100)
progress_bar.pack(fill="x", padx=5, pady=5)

# ---------- Status Label ---------- #
status_var = tk.StringVar(value="Idle")
status_label = tk.Label(root, textvariable=status_var)
status_label.pack(pady=5)

# ---------- Alignment Thread ---------- #
def run_alignment_thread():
    src = src_var.get()
    dst = dst_var.get()
    peg_pos = peg_pos_var.get()

    if not os.path.exists(src):
        messagebox.showerror("Error", f"Source folder does not exist: {src}")
        return
    os.makedirs(dst, exist_ok=True)

    files = sorted([f for f in os.listdir(src)
                    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))])
    total = len(files)
    if total == 0:
        messagebox.showinfo("Info", "No image files found in source folder.")
        return

    def worker():
        for i, fname in enumerate(files, 1):
            status_var.set(f"Processing {fname} ({i}/{total})")
            root.update_idletasks()
            in_path = os.path.join(src, fname)
            out_path = os.path.join(dst, os.path.splitext(fname)[0] + ".png")
            try:
                align_pages.process_folder(src, dst, holes_position=peg_pos)
            except Exception as e:
                print(f"Failed to process {fname}: {e}")
            progress_var.set(i / total * 100)
        status_var.set("Done")
        messagebox.showinfo("Done", "Alignment complete!")

    threading.Thread(target=worker, daemon=True).start()

# ---------- Buttons ---------- #
run_button = tk.Button(
    root,
    text="Run Alignment",
    command=run_alignment_thread,
    fg="black",
    bg="#f0f0f0",
    activeforeground="white",
    activebackground="#007acc",
    width=20,
    height=2
)
run_button.pack(pady=10)

cancel_button = tk.Button(
    root,
    text="Cancel",
    command=root.destroy,
    fg="black",
    bg="#f0f0f0",
    activeforeground="white",
    activebackground="#d9534f",
    width=20,
    height=2
)
cancel_button.pack(pady=10)

# ---------------- Main Loop ---------------- #
root.mainloop()
