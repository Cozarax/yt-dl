import customtkinter as ctk
import subprocess
import threading
import shutil
import sys
import os
import re


# --- Chemins (fonctionne en script et en exe PyInstaller) ---
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

BIN_DIR    = os.path.join(BASE_DIR, "bin")
OUTPUT_DIR = os.path.join(BASE_DIR, "downloads")
TEMP_DIR   = os.path.join(BASE_DIR, "temp")
YTDLP_EXE  = os.path.join(BIN_DIR, "yt-dlp.exe")
FFMPEG_EXE = os.path.join(BIN_DIR, "ffmpeg.exe")

# Regex pour extraire le pourcentage depuis les logs yt-dlp
# Exemple : [download]  23.3% of ~ 108.80MiB at 397.97KiB/s ETA 03:33
PROGRESS_RE = re.compile(r'\[download\]\s+(\d+\.?\d*)%')


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("FetchUrl")
        self.geometry("700x560")
        self.minsize(600, 480)
        self.resizable(True, True)
        self._build_ui()
        self._check_binaries()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- En-tête ---
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(24, 0), sticky="ew")

        ctk.CTkLabel(header, text="FetchUrl", font=ctk.CTkFont(size=28, weight="bold")).pack(side="left")
        ctk.CTkLabel(
            header,
            text="YouTube · Vimeo · et plus",
            font=ctk.CTkFont(size=13),
            text_color="gray",
        ).pack(side="left", padx=(12, 0), pady=(6, 0))

        # --- Champ URL ---
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.grid(row=1, column=0, padx=24, pady=(20, 0), sticky="ew")
        url_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(url_frame, text="URL de la vidéo", font=ctk.CTkFont(size=13)).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 6)
        )

        self.url_var = ctk.StringVar()
        self.url_entry = ctk.CTkEntry(
            url_frame,
            textvariable=self.url_var,
            placeholder_text="Colle le lien ici…",
            height=40,
            font=ctk.CTkFont(size=13),
        )
        self.url_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10))
        self.url_entry.bind("<Return>", lambda _: self._start_download())

        self.btn_download = ctk.CTkButton(
            url_frame,
            text="Télécharger",
            height=40,
            width=140,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._start_download,
        )
        self.btn_download.grid(row=1, column=1)

        # --- Barre de progression ---
        progress_frame = ctk.CTkFrame(self, fg_color="transparent")
        progress_frame.grid(row=2, column=0, padx=24, pady=(16, 0), sticky="ew")
        progress_frame.grid_columnconfigure(0, weight=1)

        self.progress = ctk.CTkProgressBar(progress_frame, height=10)
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.progress.set(0)

        self.pct_label = ctk.CTkLabel(
            progress_frame, text="", width=40, font=ctk.CTkFont(size=12), text_color="gray"
        )
        self.pct_label.grid(row=0, column=1)

        # --- Zone de log ---
        self.log = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word",
            state="disabled",
        )
        self.log.grid(row=3, column=0, padx=24, pady=(12, 0), sticky="nsew")

        # --- Barre de statut ---
        self.status_var = ctk.StringVar(value="Prêt.")
        ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="gray",
        ).grid(row=4, column=0, padx=24, pady=(8, 16), sticky="w")

    def _check_binaries(self):
        missing = []
        if not os.path.exists(YTDLP_EXE):
            missing.append("yt-dlp.exe introuvable dans bin/")
        if not os.path.exists(FFMPEG_EXE):
            missing.append("ffmpeg.exe introuvable dans bin/")
        for msg in missing:
            self._append_log(f"[ERREUR] {msg}\n")
        if missing:
            self.btn_download.configure(state="disabled")
            self.status_var.set("Binaires manquants — lance setup.bat d'abord.")

    def _append_log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text)
        self.log.see("end")
        self.log.configure(state="disabled")

    def _start_download(self):
        url = self.url_var.get().strip()
        if not url:
            self.status_var.set("Colle une URL d'abord.")
            return

        self.btn_download.configure(state="disabled")
        self.url_entry.configure(state="disabled")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        self.progress.set(0)
        self.progress.configure(mode="indeterminate")
        self.progress.start()
        self.pct_label.configure(text="")
        self.status_var.set("Téléchargement en cours…")

        threading.Thread(target=self._run_download, args=(url,), daemon=True).start()

    def _run_download(self, url):
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(TEMP_DIR, exist_ok=True)

        cmd = [
            YTDLP_EXE,
            "-U",
            "-S", "res:1080,codec:avc,fps,br",
            "-f", "bv*[ext=mp4]+ba[ext=m4a]/bv*+ba/best",
            "--merge-output-format", "mp4",
            "-o", os.path.join(OUTPUT_DIR, "%(title)s [%(id)s].%(ext)s"),
            "--embed-thumbnail",
            "--embed-metadata",
            "--compat-options", "no-keep-subs",
            "--extractor-args", "vimeo:dash=0",
            "--ffmpeg-location", BIN_DIR,
            "--no-keep-fragments",
            "--paths", f"temp:{TEMP_DIR}",
            url,
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            determinate_started = False

            for line in process.stdout:
                self.after(0, self._append_log, line)

                match = PROGRESS_RE.search(line)
                if match:
                    percent = float(match.group(1))
                    if not determinate_started:
                        self.after(0, self._switch_to_determinate)
                        determinate_started = True
                    self.after(0, self._update_progress, percent)

            process.wait()
            success = process.returncode == 0

        except Exception as exc:
            self.after(0, self._append_log, f"[ERREUR] {exc}\n")
            success = False

        self.after(0, self._on_done, success)

    def _switch_to_determinate(self):
        self.progress.stop()
        self.progress.configure(mode="determinate")

    def _update_progress(self, percent):
        self.progress.set(percent / 100)
        self.pct_label.configure(text=f"{int(percent)}%")

    def _on_done(self, success):
        self.progress.stop()
        self.btn_download.configure(state="normal")
        self.url_entry.configure(state="normal")

        if success:
            self.progress.set(1)
            self.pct_label.configure(text="100%")
            self.url_var.set("")
            self.status_var.set(f"Terminé ! Fichier dans : {OUTPUT_DIR}")
            self._append_log(f"\n--- Terminé. Fichier dans : {OUTPUT_DIR} ---\n")
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
        else:
            self.progress.set(0)
            self.pct_label.configure(text="")
            self.status_var.set("Échec — voir le log ci-dessus.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
