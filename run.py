import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import threading

class PDFOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Optimizer (Auto File/Folder Mode)")
        self.root.geometry("800x600")
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.exe_path = os.path.join(base_dir, "bin", "qpdf.exe")

        self.setup_ui()
        
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(1, lambda: self.root.attributes('-topmost', False))

    def setup_ui(self):
        frame_input = tk.LabelFrame(self.root, text=" Target File atau Folder (termasuk subfolder) ", padx=10, pady=10)
        frame_input.pack(fill="x", padx=15, pady=10)

        self.txt_target = tk.Entry(frame_input, font=("Arial", 10))
        self.txt_target.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_file = tk.Button(frame_input, text="Pilih File", command=self.browse_file)
        btn_file.pack(side="left", padx=2)

        btn_folder = tk.Button(frame_input, text="Pilih Folder", command=self.browse_folder)
        btn_folder.pack(side="left", padx=2)

        self.btn_process = tk.Button(self.root, text="PROSES", bg="#0078D7", fg="white", font=("Arial", 11, "bold"), command=self.pemicu_thread_proses)
        self.btn_process.pack(fill="x", padx=15, pady=5)

        lbl_log = tk.Label(self.root, text=f"PDF Tool: {self.exe_path}", fg="gray", anchor="w")
        lbl_log.pack(fill="x", padx=15, pady=(10, 0))

        self.log_area = scrolledtext.ScrolledText(self.root, height=12, state="disabled", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def log(self, text):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.configure(state="disabled")
        self.log_area.see(tk.END)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.txt_target.delete(0, tk.END)
            self.txt_target.insert(0, os.path.normpath(path))

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.txt_target.delete(0, tk.END)
            self.txt_target.insert(0, os.path.normpath(path))

    def process_pdf(self, file_path):
        if file_path.lower().endswith("_tmp.pdf"):
            return False

        base_no_ext, _ = os.path.splitext(file_path)
        tmp_path = base_no_ext + "_tmp.pdf"
        cmd = [self.exe_path, "--empty", "--pages", file_path, "1-z", "--", tmp_path]

        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True, 
                           creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if os.path.exists(tmp_path):
                os.replace(tmp_path, file_path)
                return True
        except Exception:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return False

    def pemicu_thread_proses(self):
        user_input = self.txt_target.get().strip().replace('"', '')

        if not os.path.exists(self.exe_path):
            messagebox.showerror("Error", f"Executable file tidak ditemukan di:\n\"{self.exe_path}\"")
            return
        if not user_input:
            messagebox.showwarning("Peringatan", "Silahkan pilih file atau folder target terlebih dahulu.")
            return
        if not os.path.exists(user_input):
            messagebox.showerror("Error", f"Target tidak ditemukan:\n\"{user_input}\"")
            return

        self.btn_process.config(state="disabled", text="SEDANG MEMPROSES...", bg="gray")

        thread_kerja = threading.Thread(target=self.start_processing, args=(user_input,))
        thread_kerja.daemon = True
        thread_kerja.start()

    def start_processing(self, user_input):
        self.log_area.configure(state="normal")
        self.log_area.delete(1.0, tk.END)
        self.log_area.configure(state="disabled")

        self.log("======================================================")
        self.log("      PDF OPTIMIZER (Auto File/Folder Mode)           ")
        self.log("======================================================\n")

        count = 0

        if os.path.isdir(user_input):
            self.log("[MODE] Folder + Subfolder terdeteksi.\n")
            for root_dir, _, files in os.walk(user_input):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        count += 1
                        full_path = os.path.join(root_dir, file)
                        self.log(f"[{count}] Memproses: {full_path}...")
                        
                        sukses = self.process_pdf(full_path)
                        if not sukses:
                            self.log(f"     [GAGAL] {full_path}")
        else:
            self.log("[MODE] Single File terdeteksi.\n")
            file_name = os.path.basename(user_input)
            self.log(f"Memproses: {file_name}...")
            
            sukses = self.process_pdf(user_input)
            if sukses:
                count = 1
            else:
                self.log(f"     [GAGAL] {user_input}")

        self.log("\n------------------------------------------------------")
        self.log(f"Selesai! {count} file telah diproses.")
        
        self.btn_process.config(state="normal", text="PROSES", bg="#0078D7")
        
        messagebox.showinfo("Selesai", f"Proses selesai.\nTotal {count} file diproses.")
        
        self.txt_target.delete(0, tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFOptimizerGUI(root)
    root.mainloop()
