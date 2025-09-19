import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import os
import align_pages


class AlignGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DIY Animation Scan Aligner")

        # Cancel flag
        self.cancel_flag = threading.Event()

        # Peg hole position
        self.peg_var = tk.StringVar(value="top")
        tk.Label(root, text="Peg hole position:").pack(anchor="w", padx=10, pady=5)
        tk.Radiobutton(root, text="Top", variable=self.peg_var, value="top").pack(
            anchor="w", padx=20
        )
        tk.Radiobutton(root, text="Left", variable=self.peg_var, value="left").pack(
            anchor="w", padx=20
        )

        # Source directory
        self.src_var = tk.StringVar(value="scans")
        tk.Label(root, text="Source directory:").pack(anchor="w", padx=10, pady=5)
        src_frame = tk.Frame(root)
        src_frame.pack(fill="x", padx=10)
        tk.Entry(src_frame, textvariable=self.src_var, width=40).pack(side="left")
        tk.Button(src_frame, text="Browse", command=self.browse_src).pack(side="left")

        # Destination directory
        self.dst_var = tk.StringVar(value="aligned")
        tk.Label(root, text="Destination directory:").pack(anchor="w", padx=10, pady=5)
        dst_frame = tk.Frame(root)
        dst_frame.pack(fill="x", padx=10)
        tk.Entry(dst_frame, textvariable=self.dst_var, width=40).pack(side="left")
        tk.Button(dst_frame, text="Browse", command=self.browse_dst).pack(side="left")

        # Progress
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = tk.Scale(
            root,
            variable=self.progress_var,
            from_=0,
            to=100,
            orient="horizontal",
            length=300,
            state="disabled",
            label="Progress",
        )
        self.progress.pack(pady=10)

        # Status label
        self.status_var = tk.StringVar(value="Idle")
        tk.Label(root, textvariable=self.status_var).pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.run_button = tk.Button(
            btn_frame,
            text="Run Alignment",
            command=self.run_alignment,
            bg="#e0e0e0",
            fg="black",
            activebackground="#d0d0d0",
        )
        self.run_button.pack(side="left", padx=10)

        self.cancel_button = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.cancel_alignment,
            bg="#e0e0e0",
            fg="black",
            activebackground="#d0d0d0",
        )
        self.cancel_button.pack(side="left", padx=10)

    def browse_src(self):
        directory = filedialog.askdirectory(initialdir=self.src_var.get())
        if directory:
            self.src_var.set(directory)

    def browse_dst(self):
        directory = filedialog.askdirectory(initialdir=self.dst_var.get())
        if directory:
            self.dst_var.set(directory)

    def run_alignment(self):
        src = self.src_var.get()
        dst = self.dst_var.get()
        peg_pos = self.peg_var.get()

        if not os.path.isdir(src):
            messagebox.showerror("Error", f"Source folder does not exist: {src}")
            return

        os.makedirs(dst, exist_ok=True)

        self.cancel_flag.clear()
        self.status_var.set("Running...")
        self.progress_var.set(0)

        thread = threading.Thread(
            target=self.worker, args=(src, dst, peg_pos), daemon=True
        )
        thread.start()

    def worker(self, src, dst, peg_pos):
        def update_progress(i, total, fname):
            if self.cancel_flag.is_set():
                raise RuntimeError("Alignment cancelled by user.")
            self.progress_var.set(i / total * 100)
            self.status_var.set(f"Processing {fname} ({i}/{total})")
            self.root.update_idletasks()

        try:
            align_pages.process_folder(
                src,
                dst,
                holes_position=peg_pos,
                debug=False,
                preview=False,
                progress_callback=update_progress,
            )
            if not self.cancel_flag.is_set():
                self.status_var.set("Done")
                self.progress_var.set(100)
                messagebox.showinfo("Done", "Alignment complete!")
        except Exception as e:
            if str(e) == "Alignment cancelled by user.":
                self.status_var.set("Cancelled")
                messagebox.showinfo("Cancelled", "Alignment was cancelled.")
            else:
                self.status_var.set("Error")
                messagebox.showerror("Error", str(e))

    def cancel_alignment(self):
        self.cancel_flag.set()
        self.status_var.set("Cancelling...")


if __name__ == "__main__":
    root = tk.Tk()
    app = AlignGUI(root)
    root.mainloop()
