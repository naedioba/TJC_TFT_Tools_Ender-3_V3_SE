#!/usr/bin/env python3
"""
Interface graphique bilingue (français / English) pour tjc_tft_tool.py —
personnalisation de l'écran de l'Ender-3 V3 SE.
Bilingual (French / English) graphical interface for tjc_tft_tool.py —
Ender-3 V3 SE display customization.

Placer ce fichier dans le même dossier que tjc_tft_tool.py, puis double-cliquer dessus.
Put this file in the same folder as tjc_tft_tool.py, then double-click it.
Dépendances / Requirements : pip install pillow numpy

Copyright (C) 2026 Mamadou Bâ Neige

This program is free software: you can redistribute it and/or modify it under the terms
of the GNU General Public License as published by the Free Software Foundation, either
version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details (file COPYING, or
<https://www.gnu.org/licenses/>).

Crédits / Credits : CLARK SCHEFF (0xD34D) et/and MAX ZUIDBERG (projet/project UNUF)
— détail dans / details in tjc_tft_tool.py.
"""
import contextlib, io, json, os, pathlib, queue, subprocess, sys, threading, traceback, webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import tjc_tft_tool as tool
except Exception as e:                                   # dépendance ou script manquant / missing file
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("TJC TFT Tool",
        "Impossible de charger tjc_tft_tool.py / Cannot load tjc_tft_tool.py.\n\n"
        "Vérifiez qu'il est dans le même dossier et que les bibliothèques sont installées.\n"
        "Check that it is in the same folder and that the libraries are installed:\n"
        "python -m pip install pillow numpy\n\nDétail / Details: " + str(e))
    sys.exit(1)

NAVY, NAVY2, CYAN, INK, MUTED = "#0b1a3a", "#13264f", "#2fc6d6", "#e8eef8", "#8fa3c7"
OK, ERR = "#5bd38a", "#ff7a7a"
PREFS = os.path.join(os.path.expanduser("~"), ".tjc_tft_tool.json")
HELP_DIR = "aide"                                        # dossier du manuel / manual folder
HELP_FILES = {"fr": "manuel_fr.html", "en": "manual_en.html"}

# ---------------------------------------------------------------- textes de l'interface / UI strings
UI = {
 "fr": {
  "win_title": "TJC TFT Tool {v} — écran Ender-3 V3 SE",
  "title": "Personnalisation de l'écran de l'Ender-3 V3 SE",
  "subtitle": "Extraire les images du tjc.tft, les modifier, puis reconstruire un fichier que l'écran accepte.",
  "src": "Fichier .tft d'origine", "src_hint": "Le tjc.tft original de Creality, jamais modifié.",
  "img": "Dossier des images", "img_hint": "Où les PNG sont créés (extraire) ou lus (reconstruire).",
  "out": "Fichier .tft de sortie", "out_hint": "Le nouveau fichier à copier sur la carte SD (nommé tjc.tft).",
  "browse": "Parcourir…",
  "extract": "Extraire les images", "pack": "Reconstruire le .tft", "check": "Vérifier un .tft",
  "open_dir": "Ouvrir le dossier des images", "clear": "Effacer le journal",
  "based_on": "D'après les travaux de ", "and": " et ",
  "copyright_short": "© 2026 Mamadou Bâ Neige — GNU GPL v3",
  "about_btn": "À propos et crédits", "ready": "Prêt.",
  "about_title": "À propos", "about_sub": "Personnalisation des images de l'écran de l'Ender-3 V3 SE",
  "relies_on": "Cet outil repose sur le travail de rétro-ingénierie de :", "thanks": "Merci à eux.",
  "free_sw": "Ce programme est un logiciel libre : vous pouvez le redistribuer et le modifier\n"
             "selon les termes de la GNU General Public License, version 3 ou ultérieure.\n"
             "Texte complet : fichier COPYING, ou https://www.gnu.org/licenses/",
  "close": "Fermer",
  "ft_tft": "Fichier écran TJC", "ft_all": "Tous", "dlg_check": "Fichier .tft à vérifier",
  "dir_title": "Dossier", "dir_missing": "Ce dossier n'existe pas encore.",
  "missing_title": "Information manquante",
  "need_src": "Choisissez le fichier .tft d'origine.",
  "need_img_new": "Choisissez le dossier où créer les images.",
  "need_img": "Choisissez le dossier contenant les images modifiées.",
  "need_out": "Choisissez le fichier .tft de sortie.",
  "nonempty_title": "Dossier non vide",
  "nonempty": "Ce dossier contient déjà des PNG.\nLes images portant le même nom seront écrasées. Continuer ?",
  "protect_title": "Protection de l'original",
  "protect": "Le fichier de sortie ne peut pas remplacer le fichier d'origine.",
  "exists_title": "Fichier existant", "exists": "{p}\nexiste déjà. Le remplacer ?",
  "t_extract": "Extraction", "t_pack": "Reconstruction", "t_check": "Vérification",
  "running": "{t} en cours…", "done": "{t} terminée.", "failed": "{t} : échec (voir le journal).",
  "done_title": "Terminé",
  "done_msg": "Le nouveau fichier est prêt.\nCopiez-le sur la carte SD, en gardant toujours le fichier d'origine à part.",
  "out_dir": "sortie",
  "help": "? Aide",
  "help_missing_title": "Manuel introuvable",
  "help_missing": "Le manuel n'a pas été trouvé.\nPlacez le dossier « aide » à côté de tjc_tft_gui.pyw.",
 },
 "en": {
  "win_title": "TJC TFT Tool {v} — Ender-3 V3 SE display",
  "title": "Ender-3 V3 SE display customization",
  "subtitle": "Extract the images from tjc.tft, edit them, then rebuild a file the display accepts.",
  "src": "Original .tft file", "src_hint": "Creality's original tjc.tft, never modified.",
  "img": "Images folder", "img_hint": "Where PNGs are created (extract) or read (rebuild).",
  "out": "Output .tft file", "out_hint": "The new file to copy to the SD card (named tjc.tft).",
  "browse": "Browse…",
  "extract": "Extract images", "pack": "Rebuild .tft", "check": "Check a .tft",
  "open_dir": "Open images folder", "clear": "Clear log",
  "based_on": "Based on the work of ", "and": " and ",
  "copyright_short": "© 2026 Mamadou Bâ Neige — GNU GPL v3",
  "about_btn": "About & credits", "ready": "Ready.",
  "about_title": "About", "about_sub": "Image customization for the Ender-3 V3 SE display",
  "relies_on": "This tool builds on the reverse-engineering work of:", "thanks": "Thank you both.",
  "free_sw": "This program is free software: you can redistribute it and/or modify it\n"
             "under the terms of the GNU General Public License, version 3 or later.\n"
             "Full text: COPYING file, or https://www.gnu.org/licenses/",
  "close": "Close",
  "ft_tft": "TJC display file", "ft_all": "All files", "dlg_check": ".tft file to check",
  "dir_title": "Folder", "dir_missing": "This folder does not exist yet.",
  "missing_title": "Missing information",
  "need_src": "Choose the original .tft file.",
  "need_img_new": "Choose the folder where the images will be created.",
  "need_img": "Choose the folder containing the modified images.",
  "need_out": "Choose the output .tft file.",
  "nonempty_title": "Folder not empty",
  "nonempty": "This folder already contains PNG files.\nImages with the same name will be overwritten. Continue?",
  "protect_title": "Original file protection",
  "protect": "The output file cannot replace the original file.",
  "exists_title": "File exists", "exists": "{p}\nalready exists. Replace it?",
  "t_extract": "Extraction", "t_pack": "Rebuild", "t_check": "Check",
  "running": "{t} in progress…", "done": "{t} complete.", "failed": "{t}: failed (see log).",
  "done_title": "Done",
  "done_msg": "The new file is ready.\nCopy it to the SD card, and always keep the original file aside.",
  "out_dir": "output",
  "help": "? Help",
  "help_missing_title": "Manual not found",
  "help_missing": "The manual could not be found.\nPut the \"aide\" folder next to tjc_tft_gui.pyw.",
 },
}

class QueueWriter(io.TextIOBase):
    def __init__(self, q): self.q = q
    def write(self, s):
        if s: self.q.put(("log", s))
        return len(s)

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.lang = self._load_lang(); tool.set_lang(self.lang)
        self.geometry("760x620"); self.minsize(700, 540); self.configure(bg=NAVY)
        self.q = queue.Queue(); self.busy = False; self.status_key = ("ready", None)
        self.v_src = tk.StringVar(); self.v_img = tk.StringVar(); self.v_out = tk.StringVar()
        self.i18n = []                                   # (widget, clé / key)
        self._set_icon()
        self._style(); self._build(); self._apply_lang(); self.after(100, self._poll)

    def _set_icon(self):
        for base in filter(None, [getattr(sys, "_MEIPASS", None), os.path.dirname(os.path.abspath(__file__))]):
            p = os.path.join(base, "tjc_tft_tool.ico")
            if os.path.isfile(p) and sys.platform.startswith("win"):
                try: self.iconbitmap(p)
                except Exception: pass
                return

    # ------------------------------------------------------------ langue / language
    def t(self, key, **kw): return UI[self.lang][key].format(**kw)

    def _load_lang(self):
        try:
            with open(PREFS, encoding="utf-8") as f: return json.load(f).get("lang", "fr")
        except Exception:
            return tool._detect_lang()

    def _save_lang(self):
        try:
            with open(PREFS, "w", encoding="utf-8") as f: json.dump({"lang": self.lang}, f)
        except Exception:
            pass

    def set_lang(self, lang):
        if lang == self.lang: return
        self.lang = lang; tool.set_lang(lang); self._save_lang(); self._apply_lang()

    def _apply_lang(self):
        self.title(self.t("win_title", v=tool.__version__))
        for w, key in self.i18n: w.configure(text=self.t(key))
        self._set_status(*self.status_key)
        for code, btn in self.lang_btns.items():
            btn.configure(style="LangOn.TButton" if code == self.lang else "Lang.TButton")

    def _tw(self, widget, key):
        self.i18n.append((widget, key)); return widget

    # ------------------------------------------------------------ apparence
    def _style(self):
        s = ttk.Style(self); s.theme_use("clam")
        s.configure(".", background=NAVY, foreground=INK, fieldbackground=NAVY2, font=("Segoe UI", 10))
        s.configure("TLabel", background=NAVY, foreground=INK)
        s.configure("Muted.TLabel", foreground=MUTED, font=("Segoe UI", 9))
        s.configure("Title.TLabel", font=("Segoe UI Semibold", 16))
        s.configure("TEntry", fieldbackground=NAVY2, foreground=INK, insertcolor=INK, bordercolor="#2a3f6e")
        s.configure("TButton", background="#20365f", foreground=INK, borderwidth=0, padding=(10, 6))
        s.map("TButton", background=[("active", "#2a4778"), ("disabled", "#18284a")],
              foreground=[("disabled", "#5a6c90")])
        s.configure("Task.TButton", background=CYAN, foreground=NAVY, font=("Segoe UI Semibold", 11), padding=(14, 10))
        s.map("Task.TButton", background=[("active", "#5ad8e4"), ("disabled", "#2a4a5e")],
              foreground=[("disabled", "#6d8199")])
        s.configure("Help.TButton", background=NAVY2, foreground=INK, padding=(8, 3), font=("Segoe UI Semibold", 9))
        s.map("Help.TButton", background=[("active", "#2a4778")])
        s.configure("Lang.TButton", background=NAVY2, foreground=MUTED, padding=(8, 3), font=("Segoe UI Semibold", 9))
        s.map("Lang.TButton", background=[("active", "#2a4778")])
        s.configure("LangOn.TButton", background=CYAN, foreground=NAVY, padding=(8, 3), font=("Segoe UI Semibold", 9))
        s.map("LangOn.TButton", background=[("active", "#5ad8e4")])

    def _build(self):
        pad = {"padx": 18}
        top = ttk.Frame(self); top.pack(fill="x", pady=(16, 0), **pad)
        self._tw(ttk.Label(top, style="Title.TLabel"), "title").pack(side="left")
        lf_ = ttk.Frame(top); lf_.pack(side="right")
        self._tw(ttk.Button(lf_, style="Help.TButton", width=8, command=self._open_help), "help").pack(side="left", padx=(0, 10))
        self.bind("<F1>", lambda e: self._open_help())
        self.lang_btns = {}
        for code in ("fr", "en"):
            b = ttk.Button(lf_, text=code.upper(), width=3, command=lambda c=code: self.set_lang(c))
            b.pack(side="left", padx=(4, 0)); self.lang_btns[code] = b
        self._tw(ttk.Label(self, style="Muted.TLabel"), "subtitle").pack(anchor="w", pady=(2, 12), **pad)

        f = ttk.Frame(self); f.pack(fill="x", **pad); f.columnconfigure(1, weight=1)
        rows = [("src", self.v_src, self._pick_src), ("img", self.v_img, self._pick_img),
                ("out", self.v_out, self._pick_out)]
        for r, (key, var, cmd) in enumerate(rows):
            self._tw(ttk.Label(f), key).grid(row=2 * r, column=0, sticky="w", padx=(0, 10), pady=(6, 0))
            ttk.Entry(f, textvariable=var).grid(row=2 * r, column=1, sticky="ew", pady=(6, 0))
            self._tw(ttk.Button(f, command=cmd), "browse").grid(row=2 * r, column=2, padx=(8, 0), pady=(6, 0))
            self._tw(ttk.Label(f, style="Muted.TLabel"), key + "_hint").grid(row=2 * r + 1, column=1, sticky="w")

        b = ttk.Frame(self); b.pack(fill="x", pady=(16, 8), **pad)
        self.buttons = [
            self._tw(ttk.Button(b, style="Task.TButton", command=self.do_extract), "extract"),
            self._tw(ttk.Button(b, style="Task.TButton", command=self.do_pack), "pack"),
            self._tw(ttk.Button(b, style="Task.TButton", command=self.do_check), "check")]
        for i, btn in enumerate(self.buttons):
            b.columnconfigure(i, weight=1); btn.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 8, 0))

        tools = ttk.Frame(self); tools.pack(fill="x", **pad)
        self._tw(ttk.Button(tools, command=self._open_img), "open_dir").pack(side="left")
        self._tw(ttk.Button(tools, command=lambda: self.log.delete("1.0", "end")), "clear").pack(side="right")

        foot = ttk.Frame(self); foot.pack(side="bottom", fill="x", pady=(0, 10), **pad)
        left = ttk.Frame(foot); left.pack(side="left", fill="x")
        row1 = ttk.Frame(left); row1.pack(anchor="w")
        self._tw(ttk.Label(row1, style="Muted.TLabel"), "based_on").pack(side="left")
        names = [n for n, *_ in tool.CREDITS_LIST]
        for i, n in enumerate(names):
            tk.Label(row1, text=n, bg=NAVY, fg=CYAN, font=("Segoe UI Semibold", 10)).pack(side="left")
            if i < len(names) - 1:
                self._tw(ttk.Label(row1, style="Muted.TLabel"), "and").pack(side="left")
        self._tw(ttk.Label(left, style="Muted.TLabel"), "copyright_short").pack(anchor="w")
        self._tw(ttk.Button(foot, command=self._about), "about_btn").pack(side="right")
        self.status = ttk.Label(self, style="Muted.TLabel")
        self.status.pack(side="bottom", anchor="w", pady=(6, 6), **pad)

        lf = tk.Frame(self, bg=NAVY); lf.pack(fill="both", expand=True, padx=18, pady=(8, 0))
        self.log = tk.Text(lf, bg="#071228", fg=INK, insertbackground=INK, relief="flat", wrap="word",
                           font=("Consolas", 10), padx=10, pady=8, highlightthickness=1, highlightbackground="#2a3f6e")
        sb = ttk.Scrollbar(lf, command=self.log.yview); self.log.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y"); self.log.pack(side="left", fill="both", expand=True)
        self.log.tag_configure("ok", foreground=OK); self.log.tag_configure("err", foreground=ERR)
        self.log.tag_configure("head", foreground=CYAN)
        self.bar = ttk.Progressbar(self, mode="indeterminate")

    def _set_status(self, key, task=None):
        self.status_key = (key, task)
        self.status.configure(text=self.t(key, t=self.t(task)) if task else self.t(key))

    def _about(self):
        w = tk.Toplevel(self); w.title(self.t("about_title")); w.configure(bg=NAVY); w.resizable(False, False); w.transient(self)
        ttk.Label(w, text=f"TJC TFT Tool {tool.__version__}", style="Title.TLabel").pack(anchor="w", padx=20, pady=(18, 2))
        ttk.Label(w, text=self.t("about_sub"), style="Muted.TLabel").pack(anchor="w", padx=20)
        ttk.Label(w, text=tool.tr("copyright")).pack(anchor="w", padx=20, pady=(14, 0))
        ttk.Label(w, text=self.t("relies_on"), style="Muted.TLabel").pack(anchor="w", padx=20, pady=(16, 6))
        for name, alias, contrib, lic in tool.CREDITS_LIST:
            card = tk.Frame(w, bg=NAVY2, highlightthickness=0)
            card.pack(fill="x", padx=20, pady=4)
            tk.Frame(card, bg=CYAN, width=4).pack(side="left", fill="y")
            body = tk.Frame(card, bg=NAVY2); body.pack(side="left", fill="x", expand=True, padx=12, pady=8)
            tk.Label(body, text=name, bg=NAVY2, fg=CYAN, font=("Segoe UI Semibold", 15)).pack(anchor="w")
            tk.Label(body, text=tool.L(alias), bg=NAVY2, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w")
            tk.Label(body, text=f"{tool.L(contrib)}  ·  {tool.tr('license')} {lic}", bg=NAVY2, fg=INK,
                     font=("Segoe UI", 10)).pack(anchor="w", pady=(4, 0))
        ttk.Label(w, text=self.t("thanks"), style="Muted.TLabel").pack(anchor="w", padx=20, pady=(4, 0))
        ttk.Label(w, text=self.t("free_sw"), justify="left").pack(anchor="w", padx=20, pady=(14, 0))
        ttk.Label(w, text=tool.tr("disclaimer"), style="Muted.TLabel", justify="left").pack(anchor="w", padx=20, pady=(14, 0))
        ttk.Button(w, text=self.t("close"), command=w.destroy).pack(anchor="e", padx=20, pady=16)
        w.grab_set()

    # ------------------------------------------------------------ choix des fichiers / file selection
    def _ft(self, all_files=False):
        ft = [(self.t("ft_tft"), "*.tft")]
        return ft + [(self.t("ft_all"), "*.*")] if all_files else ft

    def _pick_src(self):
        p = filedialog.askopenfilename(title=self.t("src"), filetypes=self._ft(True))
        if p:
            self.v_src.set(os.path.normpath(p)); d = os.path.dirname(p)
            if not self.v_img.get(): self.v_img.set(os.path.normpath(os.path.join(d, "images")))
            if not self.v_out.get(): self.v_out.set(os.path.normpath(os.path.join(d, self.t("out_dir"), "tjc.tft")))

    def _pick_img(self):
        p = filedialog.askdirectory(title=self.t("img"))
        if p: self.v_img.set(os.path.normpath(p))

    def _pick_out(self):
        p = filedialog.asksaveasfilename(title=self.t("out"), defaultextension=".tft", initialfile="tjc.tft",
                                         filetypes=self._ft())
        if p: self.v_out.set(os.path.normpath(p))

    def _help_path(self):
        bases = [getattr(sys, "_MEIPASS", None), os.path.dirname(os.path.abspath(__file__)),
                 os.path.dirname(os.path.abspath(sys.executable))]
        langs = [self.lang] + [l for l in HELP_FILES if l != self.lang]   # repli sur l'autre langue
        for lang in langs:
            for base in filter(None, bases):
                p = os.path.join(base, HELP_DIR, HELP_FILES[lang])
                if os.path.isfile(p): return p
        return None

    def _open_help(self):
        p = self._help_path()
        if not p: return messagebox.showinfo(self.t("help_missing_title"), self.t("help_missing"))
        webbrowser.open(pathlib.Path(p).resolve().as_uri())

    def _open_img(self):
        d = self.v_img.get()
        if not d or not os.path.isdir(d): return messagebox.showinfo(self.t("dir_title"), self.t("dir_missing"))
        if sys.platform.startswith("win"): os.startfile(d)
        else: subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", d])

    # ------------------------------------------------------------ tâches / tasks
    def _need(self, *checks):
        for ok, key in checks:
            if not ok: messagebox.showwarning(self.t("missing_title"), self.t(key)); return False
        return True

    def do_extract(self):
        src, img = self.v_src.get(), self.v_img.get()
        if not self._need((os.path.isfile(src), "need_src"), (img, "need_img_new")): return
        if os.path.isdir(img) and any(f.lower().endswith(".png") for f in os.listdir(img)):
            if not messagebox.askyesno(self.t("nonempty_title"), self.t("nonempty")): return
        self._run("t_extract", tool.cmd_extract, src, img)

    def do_pack(self):
        src, img, out = self.v_src.get(), self.v_img.get(), self.v_out.get()
        if not self._need((os.path.isfile(src), "need_src"), (os.path.isdir(img), "need_img"), (out, "need_out")): return
        if os.path.abspath(out) == os.path.abspath(src):
            return messagebox.showerror(self.t("protect_title"), self.t("protect"))
        if os.path.exists(out) and not messagebox.askyesno(self.t("exists_title"), self.t("exists", p=out)): return
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        self._run("t_pack", tool.cmd_pack, src, img, out)

    def do_check(self):
        out, src = self.v_out.get(), self.v_src.get()
        target = out if out and os.path.isfile(out) else src
        if not target or not os.path.isfile(target):
            target = filedialog.askopenfilename(title=self.t("dlg_check"), filetypes=self._ft())
            if not target: return
        self._run("t_check", tool.cmd_check, target)

    def _run(self, task, fn, *args):
        if self.busy: return
        self.busy = True; tool.set_lang(self.lang)
        for b in self.buttons: b.state(["disabled"])
        for b in self.lang_btns.values(): b.state(["disabled"])     # pas de changement de langue pendant une tâche
        self._set_status("running", task)
        self.bar.pack(side="bottom", fill="x", padx=18, pady=(0, 4), before=self.status); self.bar.start(12)
        self.q.put(("head", f"\n— {self.t(task)} —\n"))
        def worker():
            w = QueueWriter(self.q); ok = True
            try:
                with contextlib.redirect_stdout(w): fn(*args)
            except SystemExit as e:
                ok = False; self.q.put(("err", str(e.code) + "\n"))
            except Exception:
                ok = False; self.q.put(("err", traceback.format_exc()))
            self.q.put(("done", (task, ok)))
        threading.Thread(target=worker, daemon=True).start()

    def _poll(self):
        okw = [f": {m['ok']} " for m in tool.MSG.values()] + [m["consistent"] for m in tool.MSG.values()]
        errw = [m["error"] for m in tool.MSG.values()] + [m["inconsistent"] for m in tool.MSG.values()]
        try:
            while True:
                kind, data = self.q.get_nowait()
                if kind == "done":
                    task, ok = data; self.busy = False
                    for b in self.buttons + list(self.lang_btns.values()): b.state(["!disabled"])
                    self.bar.stop(); self.bar.pack_forget()
                    self._set_status("done" if ok else "failed", task)
                    if ok and task == "t_pack":
                        messagebox.showinfo(self.t("done_title"), self.t("done_msg"))
                    continue
                tag = kind if kind in ("err", "head") else ""
                if kind == "log":
                    if any(x in data for x in errw): tag = "err"
                    elif any(x in data for x in okw): tag = "ok"
                self.log.insert("end", data, tag); self.log.see("end")
        except queue.Empty:
            pass
        self.after(100, self._poll)

if __name__ == "__main__":
    App().mainloop()
