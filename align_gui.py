import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess


class AlignGUI:
    def __init__(self, master):
        self.master = master
        master.title("DIY Animation Scan Aligner")

        # File/folder variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()

        # Create the GUI layout
        self.create_widgets()

    def create_widgets(self):
        # Input directory
        input_frame = ttk.Frame(self.master, padding="10")
        input_frame.grid(row=0, column=0, sticky="ew")
        ttk.Label(input_frame, text="Input folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(input_frame, textvariable=self.input_dir, width=50).grid(row=0, column=1, sticky="ew")
        ttk.Button(input_frame, text="Browse", command=self.browse_input).grid(row=0, column=2, padx=5)

        # Output directory
        output_frame = ttk.Frame(self.master, padding="10")
        output_frame.grid(row=1, column=0, sticky="ew")
        ttk.Label(output_frame, text="Output folder:").grid(row=0, column=0, sticky="w")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=1, sticky="ew")
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=2, padx=5)

        # Run button
        run_frame = ttk.Frame(self.master, padding="10")
        run_frame.grid(row=2, column=0, sticky="ew")
        self.run_button = ttk.Button(run_frame, text="Run Alignment", command=self.run_alignment)
        self.run_button.grid(row=0, column=0, pady=10)

        # Progress text
        progress_frame = ttk.Frame(self.master, padding="10")
        progress_frame.grid(row=3, column=0, sticky="nsew")
        self.progress_text = tk.Text(progress_frame, wrap="word", height=15, width=80)
        self.progress_text.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(progress_frame, command=self.progress_text.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.progress_text['yscrollcommand'] = scrollbar.set

        self.master.grid_rowconfigure(3, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_dir.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_dir.set(folder)

    def run_alignment(self):
        input_dir = self.input_dir.get()
        output_dir = self.output_dir.get()

        if not input_dir or not output_dir:
            messagebox.showerror("Error", "Please select both input and output folders.")
            return

        self.run_button.config(state="disabled")
        self.progress_text.delete(1.0, tk.END)

        thread = threading.Thread(target=self.run_alignment_thread, args=(input_dir, output_dir))
        thread.start()

    def run_alignment_thread(self, input_dir, output_dir):
        try:
            # Ensure align_pages.py runs in the same directory as this GUI
            script_path = os.path.join(os.path.dirname(sys.argv[0]), "align_pages.py")

            process = subprocess.Popen(
                [sys.executable, script_path, input_dir, output_dir],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            for line in process.stdout:
                self.append_progress(line)

            process.wait()

            if process.returncode == 0:
                self.append_progress("\nAlignment completed successfully.\n")
            else:
                self.append_progress("\nError: Alignment process failed.\n")
                for line in process.stderr:
                    self.append_progress(line)

        except Exception as e:
            self.append_progress(f"\nUnexpected error: {e}\n")
        finally:
            self.run_button.config(state="normal")

    def append_progress(self, text):
        self.progress_text.insert(tk.END, text)
        self.progress_text.see(tk.END)


if __name__ == "__main__":
    root = tk.Tk()
    app = AlignGUI(root)
    root.mainloop()
