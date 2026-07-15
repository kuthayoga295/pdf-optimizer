import sys
import os
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
    import pypdf
except ImportError:
    install_root = tk.Tk()
    install_root.title("PDF Sanitizer")
    install_root.geometry("420x140")
    install_root.resizable(False, False)

    status = tk.Label(
        install_root,
        text="Menginstal library pypdf...\nMohon tunggu...",
        font=("Arial", 10)
    )
    status.pack(pady=(15, 10))

    progress = ttk.Progressbar(
        install_root,
        mode="indeterminate",
        length=360
    )
    progress.pack(pady=5)
    progress.start(12)

    def install_pypdf():
        try:
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "--disable-pip-version-check",
                    "--no-input",
                    "pypdf"
                ],
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True
            )

            install_root.after(0, lambda: status.config(
                text="Instalasi berhasil.\nMembuka aplikasi..."
            ))

            global pypdf
            import pypdf

            install_root.after(800, install_root.destroy)

        except subprocess.CalledProcessError as e:
            error = e.stderr.strip() if e.stderr else str(e)

            def gagal():
                progress.stop()
                messagebox.showerror(
                    "Instalasi Gagal",
                    f"Gagal menginstal pypdf.\n\n{error}"
                )
                install_root.destroy()
                sys.exit(1)

            install_root.after(0, gagal)

    threading.Thread(
        target=install_pypdf,
        daemon=True
    ).start()

    install_root.mainloop()

from pypdf import PdfReader, PdfWriter

class PDFOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Sanitizer")
        self.root.geometry("720x560")

        self.setup_ui()
        
        self.root.lift()
        self.root.attributes('-topmost', True)
        self.root.after(1, lambda: self.root.attributes('-topmost', False))

    def setup_ui(self):
        frame_input = tk.LabelFrame(self.root, text=" Target File atau Folder (termasuk subfolder) ", padx=10, pady=10)
        frame_input.pack(fill="x", padx=15, pady=10)

        self.target_var = tk.StringVar()
        self.target_var.trace_add("write", self.update_button_state)

        self.txt_target = tk.Entry(frame_input, textvariable=self.target_var, font=("Arial", 10))
        self.txt_target.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_file = tk.Button(frame_input, text="Pilih File", command=self.browse_file)
        btn_file.pack(side="left", padx=2)

        btn_folder = tk.Button(frame_input, text="Pilih Folder", command=self.browse_folder)
        btn_folder.pack(side="left", padx=2)

        frame_features = tk.LabelFrame(self.root, text=" Fitur Sanitasi", padx=10, pady=5)
        frame_features.pack(fill="x", padx=15, pady=5)
        
        features_text = (
            "- Flatten Forms (Remove Widgets) \t - Remove Metadata \t\t - Remove Annotations\n"
            "- Remove JavaScript & OpenAction \t - Remove Embedded Files \t\t - Remove Layers (OCG)\n"
            "- Remove Links / URI Construction \t - Remove Structure Tree Root \t - Remove MarkInfo"
        )
        lbl_features = tk.Label(frame_features, text=features_text, justify="left", fg="#555555", font=("Arial", 9))
        lbl_features.pack(anchor="w")

        self.btn_process = tk.Button(self.root, text="PROSES PDF", bg="#0078D7", fg="white", font=("Arial", 11, "bold"), command=self.pemicu_thread_proses, state="disabled")
        self.btn_process.pack(fill="x", padx=15, pady=10)

        lbl_log = tk.Label(self.root, text="Engine Status: Active (pypdf)", fg="green", anchor="w")
        lbl_log.pack(fill="x", padx=15, pady=(5, 0))

        self.log_area = scrolledtext.ScrolledText(self.root, height=12, state="disabled", font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def log(self, text):
        self.log_area.configure(state="normal")
        self.log_area.insert(tk.END, text + "\n")
        self.log_area.configure(state="disabled")
        self.log_area.see(tk.END)

    def update_button_state(self, *args):
        if self.target_var.get().strip():
            self.btn_process.config(state="normal")
        else:
            self.btn_process.config(state="disabled")

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if path:
            self.target_var.set(os.path.normpath(path))

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.target_var.set(os.path.normpath(path))

    def process_pdf(self, file_path):
        if file_path.lower().endswith("_tmp.pdf"):
            return False

        base_no_ext, _ = os.path.splitext(file_path)
        tmp_path = base_no_ext + "_tmp.pdf"

        try:
            reader = PdfReader(file_path)
            
            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    self.log("     [INFO] File terenkripsi password manual. Dilewati.")
                    return False

            writer = PdfWriter()

            try:
                if reader.trailer and "/Root" in reader.trailer:
                    root = reader.trailer["/Root"]
                    if hasattr(root, "get_object"):
                        root = root.get_object()
                    
                    if "/OpenAction" in root:
                        del root["/OpenAction"]
                    
                    if "/Names" in root:
                        names = root["/Names"].get_object()
                        if "/JavaScript" in names:
                            del names["/JavaScript"]
                        if "/EmbeddedFiles" in names:
                            del names["/EmbeddedFiles"]
                    
                    if "/StructTreeRoot" in root:
                        del root["/StructTreeRoot"]
                        
                    if "/MarkInfo" in root:
                        del root["/MarkInfo"]
                        
                    if "/OCProperties" in root:
                        del root["/OCProperties"]
            except Exception as e_root:
                self.log(f"     [INFO] Root Sanitization Skip: {e_root}")

            for page in reader.pages:
                if "/Annots" in page:
                    try:
                        del page["/Annots"]
                    except Exception:
                        try:
                            page["/Annots"].clear()
                        except Exception:
                            pass

                if "/AA" in page:
                    try:
                        del page["/AA"]
                    except Exception:
                        pass
                
                try:
                    page.compress_content_streams()
                except Exception:
                    pass
                    
                writer.add_page(page)

            with open(tmp_path, "wb") as f:
                writer.write(f)

            if os.path.exists(tmp_path):
                if os.path.exists(file_path):
                    os.remove(file_path)
                os.rename(tmp_path, file_path)
                return True
                
        except Exception as e:
            self.log(f"     [ERROR DETAIL] {str(e)}")
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        return False

    def pemicu_thread_proses(self):
        user_input = self.txt_target.get().strip().replace('"', '')

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
        self.log("                     PDF SANITIZER                    ")
        self.log("======================================================\n")

        count = 0
        failed_count = 0

        if os.path.isdir(user_input):
            self.log("[MODE] Folder + Subfolder terdeteksi.\n")
            for root_dir, _, files in os.walk(user_input):
                for file in files:
                    if file.lower().endswith(".pdf"):
                        full_path = os.path.join(root_dir, file)
                        self.log(f"Memproses: {full_path}...")
                        
                        sukses = self.process_pdf(full_path)
                        if sukses:
                            count += 1
                        else:
                            failed_count += 1
                            self.log(f"     [GAGAL] Gagal mensanitasi file ini.")
        else:
            self.log("[MODE] Single File terdeteksi.\n")
            file_name = os.path.basename(user_input)
            self.log(f"Memproses: {file_name}...")
            
            sukses = self.process_pdf(user_input)
            if sukses:
                count = 1
            else:
                failed_count = 1
                self.log(f"     [GAGAL] {user_input}")

        self.log("\n------------------------------------------------------")
        self.log(f"Selesai! {count} file berhasil diproses.")
        if failed_count > 0:
            self.log(f"Terdapat {failed_count} file gagal diproses.")
        
        self.root.after(0, lambda: self.btn_process.config(state="normal", text="PROSES PDF", bg="#0078D7"))
        self.root.after(0, lambda: messagebox.showinfo("Selesai", f"Proses Selesai.\nTotal {count} file sukses dibersihkan."))
        self.root.after(0, lambda: self.target_var.set(""))

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFOptimizerGUI(root)
    root.mainloop()