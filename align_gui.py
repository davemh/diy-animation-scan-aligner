#!/usr/bin/env python3
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import os
import sys
from align_pages import process_folder

# ---------------- Main GUI ---------------- #
class AlignGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DIY Animation Scan Aligner")

        # Source folder where raw scans are located.
        tk.Label(root, text="Source Directory:").grid(row=0, column=0, sticky="e")
        self.src_var = tk.StringVar(value="scans/")
        tk.Entry(root, textvariable=self.src_var, width=40).grid(row=0, column=1)
        tk.Button(root, text="Browse", command=self.browse_src).grid(row=0, column=2)

        # Destination folder where aligned pngs should be saved
        tk.Label(root, text="Destination Directory:").grid(row=1, column=0, sticky="e")
        self.dst_var = tk.StringVar(value="aligned/")
        tk.Entry(root, textvariable=self.dst_var, width=40).grid(row=1, column=1)
        tk.Button(root, text="Browse", command=self.browse_dst).grid(row=1, column=2)

        # Peg hole position
        tk.Label(root, text="Peg Hole Position:").grid(row=2, column=0, sticky="e")
        self.peg_var = tk.StringVar(value="top")
        tk.Radiobutton(root, text="Top", variable=self.peg_var, value="top").grid(row=2, column=1, sticky="w")
        tk.Radiobutton(root, text="Bottom", variable=self.peg_var, value="bottom").grid(row=2, column=1, sticky="e")

        # Progress bar
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.grid(row=3, column=0, columnspan=3, pady=10)

        # Buttons
        self.run_btn = tk.Button(root, text="Run Alignment", command=self.run_alignment)
        self.run_btn.grid(row=4, column=0, pady=10)
        self.cancel_btn = tk.Button(root, text="Cancel", command=self.root.quit)
        self.cancel_btn.grid(row=4, column=2, pady=10)

        self.running = False

    def browse_src(self):
        folder = filedialog.askdirectory()
        if folder:
            self.src_var.set(folder)

    def browse_dst(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dst_var.set(folder)

    def run_alignment(self):
        if self.running:
            return
        self.running = True
        self.progress["value"] = 0
        thread = threading.Thread(target=self._process)
        thread.start()

    def _process(self):
        try:
            src = self.src_var.get()
            dst = self.dst_var.get()
            peg = self.peg_var.get()
            files = sorted([f for f in os.listdir(src) if f.lower().endswith(('.png','.jpg','.jpeg','.tif','.tiff'))])
            total = len(files)
            if total == 0:
                messagebox.showerror("Error", "No image files found in source directory.")
                self.running = False
                return
            for idx, fname in enumerate(files, start=1):
                process_folder(src, dst, holes_position=peg, debug=False, preview=False, preview_delay=1)
                self.progress["value"] = (idx / total) * 100
                self.root.update_idletasks()
            messagebox.showinfo("Done", "All pages aligned successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.running = False
            self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = AlignGUI(root)
    root.mainloop()
