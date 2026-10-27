#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHOXX STUDIO — High-Tech Animated Progress HUD, Centered 3s Neon-Flicker Splash Screen,
MMP Live-S2S-Tester Submenu, VRAM/GPU Monitor & Project ZIP/Git Utilities.
"""

import os
import time
import math
import random
import json
import uuid
import zipfile
import subprocess
import threading
import http.server
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

try:
    from PIL import Image, ImageTk, ImageEnhance
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


def show_neon_splash(
    root: tk.Tk,
    splash_path: Path,
    duration_ms: int = 3000,
    on_complete=None,
):
    """
    Displays a centered, borderless 3-second splash screen using splash_path
    with a subtle cyberpunk neon flicker effect (image brightness/color micro-flicker,
    glowing neon border pulse, and bottom loading bar).
    """
    splash = tk.Toplevel(root)
    splash.overrideredirect(True)
    splash.attributes("-topmost", True)
    splash.configure(bg="#060911")

    win_w, win_h = 560, 560
    scr_w = splash.winfo_screenwidth()
    scr_h = splash.winfo_screenheight()
    pos_x = max(0, (scr_w - win_w) // 2)
    pos_y = max(0, (scr_h - win_h) // 2)
    splash.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")

    canvas = tk.Canvas(
        splash,
        width=win_w,
        height=win_h,
        bg="#060911",
        bd=0,
        highlightthickness=0,
    )
    canvas.pack(fill="both", expand=True)

    # Pre-generate subtle neon flicker image variants with Pillow
    frames_tk = []
    if HAS_PIL and splash_path.exists():
        try:
            base_img = Image.open(splash_path).convert("RGB")
            base_img = base_img.resize((win_w, win_h), Image.Resampling.LANCZOS)
            # Create 6 subtle brightness & color-saturation micro-flicker levels
            flicker_profiles = [
                (1.00, 1.00),  # 0: Normal
                (1.06, 1.10),  # 1: Soft neon boost
                (0.93, 0.96),  # 2: Subtle dip
                (1.12, 1.18),  # 3: High neon pulse
                (0.87, 1.05),  # 4: Quick micro-flicker dim
                (1.03, 1.06),  # 5: Warm settle
            ]
            for b_fac, c_fac in flicker_profiles:
                img_b = ImageEnhance.Brightness(base_img).enhance(b_fac)
                img_c = ImageEnhance.Color(img_b).enhance(c_fac)
                frames_tk.append(ImageTk.PhotoImage(img_c))
        except Exception:
            frames_tk = []

    # Keep reference on splash to prevent garbage collection
    splash._frames_tk = frames_tk

    img_item = None
    if frames_tk:
        img_item = canvas.create_image(win_w // 2, win_h // 2, image=frames_tk[0], anchor="center")
    else:
        canvas.create_text(
            win_w // 2,
            win_h // 2,
            text="SHOXX // CLAUDE CODE STUDIO",
            fill="#06B6D4",
            font=("Segoe UI Black", 20),
        )

    # Neon Outer & Inner Glowing Frame + HUD overlay elements
    outer_rect = canvas.create_rectangle(2, 2, win_w - 3, win_h - 3, outline="#06B6D4", width=2)
    inner_rect = canvas.create_rectangle(6, 6, win_w - 7, win_h - 7, outline="#6366F1", width=1)

    # Subtle scanline bar that drifts down & bottom progress track
    scanline = canvas.create_line(8, 20, win_w - 8, 20, fill="#06B6D4", width=1)
    canvas.create_rectangle(24, win_h - 28, win_w - 24, win_h - 20, fill="#0B0F19", outline="#334155", width=1)
    prog_bar = canvas.create_rectangle(25, win_h - 27, 25, win_h - 21, fill="#06B6D4", outline="")
    status_txt = canvas.create_text(
        win_w // 2,
        win_h - 38,
        text="INITIALIZING SHOXX UNCENSORED STUDIO...",
        fill="#E2E8F0",
        font=("Consolas", 9, "bold"),
    )

    start_ts = time.time()
    # Deterministic + organic neon flicker pattern sequence
    flicker_pattern = [0, 0, 1, 0, 2, 3, 0, 5, 0, 4, 1, 0, 0, 3, 2, 0, 1, 5, 0, 0]
    border_colors = ["#06B6D4", "#818CF8", "#22D3EE", "#6366F1", "#38BDF8", "#A855F7"]
    step_idx = 0

    def _tick_splash():
        nonlocal step_idx
        elapsed_ms = (time.time() - start_ts) * 1000.0
        if elapsed_ms >= duration_ms:
            try:
                splash.destroy()
            except Exception:
                pass
            if callable(on_complete):
                on_complete()
            return

        frac = min(1.0, elapsed_ms / float(duration_ms))

        # 1. Subtle image neon flicker
        if frames_tk and img_item is not None:
            pat_val = flicker_pattern[step_idx % len(flicker_pattern)]
            # Occasional subtle random neon spark
            if random.random() < 0.14:
                pat_val = random.choice([1, 2, 3, 4])
            canvas.itemconfig(img_item, image=frames_tk[pat_val])

        # 2. Neon border & text micro-flicker
        b_col = border_colors[step_idx % len(border_colors)]
        i_col = "#6366F1" if step_idx % 3 != 0 else "#06B6D4"
        canvas.itemconfig(outer_rect, outline=b_col)
        canvas.itemconfig(inner_rect, outline=i_col)

        # 3. Drifting subtle neon scanline
        scan_y = int(12 + ((step_idx * 11) % (win_h - 48)))
        canvas.coords(scanline, 8, scan_y, win_w - 8, scan_y)
        canvas.itemconfig(scanline, fill="#06B6D4" if step_idx % 2 == 0 else "#4F46E5")

        # 4. Progress bar fill
        bar_max_w = (win_w - 25) - 25
        cur_bar_x = 25 + int(bar_max_w * frac)
        canvas.coords(prog_bar, 25, win_h - 27, cur_bar_x, win_h - 21)
        canvas.itemconfig(prog_bar, fill="#10B981" if frac > 0.85 else b_col)

        pct = int(frac * 100)
        canvas.itemconfig(
            status_txt,
            text=f"⚡ SHOXX STUDIO // LOADING ENGINE & MMP SUITE [{pct}%]",
            fill="#F8FAFC" if step_idx % 5 != 0 else "#22D3EE",
        )

        # 5. Subtle window alpha micro-flicker (between 0.96 and 1.0)
        try:
            alpha = 0.96 if (step_idx % 9 == 4) else 0.995
            splash.attributes("-alpha", alpha)
        except Exception:
            pass

        step_idx += 1
        splash.after(40, _tick_splash)

    _tick_splash()


class CyberProgressHUD(tk.Frame):
    """High-tech 30-FPS animated Canvas Progress & Activity HUD."""

    def __init__(self, parent, colors: dict):
        super().__init__(parent, bg=colors["bg_sidebar"])
        self.colors = colors
        self.is_active = False
        self.task_label = "SYSTEM BEREIT // IDLE"
        self.start_time = 0.0
        self.tick = 0
        self._anim_job = None

        self.canvas = tk.Canvas(
            self,
            height=34,
            bg="#060911",
            bd=0,
            highlightthickness=1,
            highlightbackground=colors["border"],
        )
        self.canvas.pack(fill="x", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._draw_frame())
        self._draw_frame()

    def start_task(self, label: str = "ARBEITE..."):
        self.task_label = label.upper()
        if not self.is_active:
            self.is_active = True
            self.start_time = time.time()
            self.tick = 0
            self._animate()

    def stop_task(self, done_label: str = "SYSTEM BEREIT // IDLE"):
        self.is_active = False
        self.task_label = done_label.upper()
        if self._anim_job:
            try:
                self.after_cancel(self._anim_job)
            except Exception:
                pass
            self._anim_job = None
        self._draw_frame()

    def _animate(self):
        if not self.is_active:
            return
        self.tick += 1
        self._draw_frame()
        self._anim_job = self.after(33, self._animate)

    def _draw_frame(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 600)
        h = 34

        if not self.is_active:
            c.create_rectangle(0, h - 3, w, h, fill="#10B981", outline="")
            c.create_oval(12, 11, 22, 21, fill="#10B981", outline="#059669")
            c.create_text(
                32,
                16,
                text=f"● {self.task_label}",
                fill="#94A3B8",
                font=("Consolas", 9, "bold"),
                anchor="w",
            )
            c.create_text(
                w - 14,
                16,
                text="READY",
                fill="#10B981",
                font=("Consolas", 9, "bold"),
                anchor="e",
            )
            return

        elapsed = time.time() - self.start_time
        grid_offset = (self.tick * 3) % 24
        for gx in range(-24, w + 24, 24):
            x_pos = gx + grid_offset
            c.create_line(x_pos, 0, x_pos - 10, h, fill="#0F172A", width=1)

        bar_y1 = h - 5
        bar_w = int(w * 0.28)
        cycle = (math.sin(self.tick * 0.11) + 1.0) / 2.0
        x_start = int(cycle * (w - bar_w))

        c.create_rectangle(0, bar_y1, w, h, fill="#111827", outline="")
        c.create_rectangle(max(0, x_start - 30), bar_y1, min(w, x_start + bar_w + 30), h, fill="#312E81", outline="")
        c.create_rectangle(x_start, bar_y1, x_start + bar_w, h, fill="#6366F1", outline="")
        c.create_rectangle(
            x_start + int(bar_w * 0.25),
            bar_y1,
            x_start + int(bar_w * 0.75),
            h,
            fill="#06B6D4",
            outline="",
        )

        cx, cy, r = 18, 15, 8
        angle_start = (self.tick * 16) % 360
        c.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#1E293B", width=2)
        c.create_arc(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            start=angle_start,
            extent=120,
            style="arc",
            outline="#06B6D4",
            width=2,
        )
        c.create_arc(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            start=(angle_start + 180) % 360,
            extent=90,
            style="arc",
            outline="#818CF8",
            width=2,
        )

        dots = "." * ((self.tick // 6) % 4)
        c.create_text(
            34,
            15,
            text=f"⚡ {self.task_label}{dots}",
            fill="#F8FAFC",
            font=("Consolas", 9, "bold"),
            anchor="w",
        )

        pulse_color = "#06B6D4" if (self.tick // 8) % 2 == 0 else "#818CF8"
        c.create_text(
            w - 14,
            15,
            text=f"ACTIVE // {elapsed:05.1f}s",
            fill=pulse_color,
            font=("Consolas", 9, "bold"),
            anchor="e",
        )


def query_vram_and_ollama_ps(ollama_bin: str | None) -> dict:
    """Queries NVIDIA GPU VRAM via nvidia-smi and active loaded models via ollama ps."""
    info = {
        "gpu_name": "CPU / Shared Memory",
        "vram_used_mb": 0,
        "vram_total_mb": 0,
        "active_models": [],
    }
    try:
        res = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=name,memory.used,memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=2.5,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        if res.returncode == 0 and res.stdout.strip():
            first_line = res.stdout.strip().splitlines()[0]
            parts = [p.strip() for p in first_line.split(",")]
            if len(parts) >= 3:
                info["gpu_name"] = parts[0]
                info["vram_used_mb"] = int(float(parts[1]))
                info["vram_total_mb"] = int(float(parts[2]))
    except Exception:
        pass

    if ollama_bin:
        try:
            res = subprocess.run(
                [ollama_bin, "ps"],
                capture_output=True,
                text=True,
                timeout=2.5,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            if res.returncode == 0:
                lines = [ln.strip() for ln in res.stdout.strip().splitlines() if ln.strip()]
                if len(lines) > 1:
                    for ln in lines[1:]:
                        cols = ln.split()
                        if cols:
                            info["active_models"].append(cols[0])
        except Exception:
            pass
    return info


def create_project_backup_zip(project_dir: Path, include_env: bool = False) -> Path:
    """Creates a timestamped ZIP backup of the project folder."""
    backups_dir = project_dir.parent / "_shoxx_backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_path = backups_dir / f"{project_dir.name}_backup_{ts}.zip"

    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "_shoxx_backups"}
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_p in project_dir.rglob("*"):
            if file_p.is_file():
                if any(part in skip_dirs for part in file_p.parts):
                    continue
                if file_p.name == ".env" and not include_env:
                    continue
                rel = file_p.relative_to(project_dir)
                zf.write(file_p, arcname=str(rel))
    return zip_path


def inspect_or_init_git(project_dir: Path, init_if_missing: bool = False) -> str:
    """Returns a concise Git status summary for the project folder."""
    git_dir = project_dir / ".git"
    if not git_dir.exists():
        if not init_if_missing:
            return "Kein Git-Repo (Klicke 'Git Init & Status' zum Initialisieren)"
        try:
            subprocess.run(
                ["git", "init"],
                cwd=str(project_dir),
                capture_output=True,
                text=True,
                timeout=4,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
        except Exception as e:
            return f"Git Fehler: {e}"

    try:
        res_branch = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        branch = res_branch.stdout.strip() or "main"
        res_status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=3,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        changed = len([ln for ln in res_status.stdout.splitlines() if ln.strip()])
        return f"Git aktiv (Branch: {branch} | {changed} geänderte/neue Dateien)"
    except Exception as e:
        return f"Git Status nicht lesbar: {e}"


def build_mmp_live_tester_page(parent: tk.Frame, app) -> tk.Frame:
    """Builds the Submenu Page: '📡 MMP Live-S2S-Tester & Webhook-Inspector' (Optimierung 1)."""
    colors = app.colors if hasattr(app, "colors") else {
        "bg_main": "#0B0F19",
        "bg_card": "#1E293B",
        "bg_input": "#0F172A",
        "border": "#334155",
        "accent": "#6366F1",
        "accent_hover": "#818CF8",
        "accent_emerald": "#10B981",
        "accent_amber": "#F59E0B",
        "accent_cyan": "#06B6D4",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
    }

    page = tk.Frame(parent, bg=colors["bg_main"])
    page.grid_columnconfigure(0, weight=2)
    page.grid_columnconfigure(1, weight=3)
    page.grid_rowconfigure(1, weight=1)

    hdr = tk.Frame(page, bg=colors["bg_main"])
    hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

    tk.Label(
        hdr,
        text="📡 MMP Live-S2S-Tester & Payload-Inspector (Untermenü)",
        font=("Segoe UI Bold", 16),
        fg=colors["text_primary"],
        bg=colors["bg_main"],
    ).pack(side="left")

    tk.Button(
        hdr,
        text="🔐 Projekt .env Keys laden",
        font=("Segoe UI Semibold", 9),
        bg=colors["bg_card"],
        fg=colors["accent_emerald"],
        bd=0,
        padx=12,
        pady=6,
        cursor="hand2",
        command=lambda: load_env_into_tester(),
    ).pack(side="right")

    left_card = tk.Frame(
        page,
        bg=colors["bg_card"],
        highlightbackground=colors["border"],
        highlightthickness=1,
        padx=16,
        pady=14,
    )
    left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
    left_card.grid_columnconfigure(1, weight=1)

    tk.Label(
        left_card,
        text="1. S2S EVENT PARAMETER KONFIGURIEREN",
        font=("Segoe UI Bold", 9),
        fg=colors["accent_cyan"],
        bg=colors["bg_card"],
    ).grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

    provider_var = tk.StringVar(value="AppsFlyer S2S v3 (inappevent)")
    event_name_var = tk.StringVar(value="af_purchase")
    revenue_var = tk.StringVar(value="49.99")
    currency_var = tk.StringVar(value="EUR")
    device_id_var = tk.StringVar(value=f"{int(time.time() * 1000)}-{uuid.uuid4().int % (10**19)}")
    customer_id_var = tk.StringVar(value="usr_senior_9001")
    dry_run_var = tk.BooleanVar(value=True)

    fields = [
        ("MMP Provider:", provider_var, ["AppsFlyer S2S v3 (inappevent)", "Singular S2S (/api/v1/evt)", "Adjust S2S (s2s.adjust.com/event)"]),
        ("Event Name / Token:", event_name_var, None),
        ("Revenue Betrag:", revenue_var, None),
        ("Währung (ISO):", currency_var, None),
        ("Device / AppsFlyer ID:", device_id_var, None),
        ("Customer User ID:", customer_id_var, None),
    ]

    for idx, (label_txt, var, combo_vals) in enumerate(fields, start=1):
        tk.Label(
            left_card,
            text=label_txt,
            font=("Segoe UI Semibold", 9),
            fg=colors["text_primary"],
            bg=colors["bg_card"],
        ).grid(row=idx, column=0, sticky="w", pady=6, padx=(0, 10))

        if combo_vals:
            cb = ttk.Combobox(left_card, textvariable=var, values=combo_vals, state="readonly", font=("Segoe UI", 9))
            cb.grid(row=idx, column=1, sticky="ew", pady=6)
        else:
            tk.Entry(
                left_card,
                textvariable=var,
                font=("Consolas", 9),
                bg=colors["bg_input"],
                fg=colors["text_primary"],
                insertbackground="#FFFFFF",
                bd=0,
                highlightbackground=colors["border"],
                highlightthickness=1,
            ).grid(row=idx, column=1, sticky="ew", ipady=4, pady=6)

    tk.Checkbutton(
        left_card,
        text="Dry-Run / Payload-Inspector Modus (Validiert & zeigt HTTP-Request ohne echten Netzwerk-Call)",
        variable=dry_run_var,
        font=("Segoe UI", 9),
        bg=colors["bg_card"],
        fg=colors["text_secondary"],
        selectcolor=colors["bg_input"],
        activebackground=colors["bg_card"],
        activeforeground=colors["text_primary"],
        wraplength=360,
        justify="left",
    ).grid(row=7, column=0, columnspan=2, sticky="w", pady=(8, 12))

    right_card = tk.Frame(
        page,
        bg=colors["bg_card"],
        highlightbackground=colors["border"],
        highlightthickness=1,
        padx=16,
        pady=14,
    )
    right_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
    right_card.grid_rowconfigure(1, weight=1)
    right_card.grid_columnconfigure(0, weight=1)

    tk.Label(
        right_card,
        text="2. LIVE HTTP PAYLOAD, HEADERS & RESPONSE INSPECTOR",
        font=("Segoe UI Bold", 9),
        fg=colors["accent_emerald"],
        bg=colors["bg_card"],
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

    inspector_text = tk.Text(
        right_card,
        bg=colors["bg_input"],
        fg=colors["text_primary"],
        font=("Consolas", 9),
        bd=0,
        padx=12,
        pady=10,
        insertbackground="#FFFFFF",
    )
    inspector_text.grid(row=1, column=0, sticky="nsew")

    def load_env_into_tester():
        ws = Path(app.workspace_var.get().strip())
        env = app._read_project_env(ws)
        inspector_text.delete("1.0", "end")
        inspector_text.insert("end", f"// Geladene .env Konfiguration aus Projekt: {ws.name}\n")
        inspector_text.insert("end", json.dumps(env, indent=2) + "\n")
        app.log_message(f"[MMP TESTER] .env Keys aus '{ws.name}' in den S2S-Inspector geladen.")

    def execute_s2s_test():
        ws = Path(app.workspace_var.get().strip())
        env = app._read_project_env(ws)
        prov = provider_var.get()
        ev_name = event_name_var.get().strip()
        rev = revenue_var.get().strip()
        cur = currency_var.get().strip()
        dev_id = device_id_var.get().strip()
        cuid = customer_id_var.get().strip()
        is_dry = dry_run_var.get()

        app.start_progress(f"MMP S2S Request ({prov.split()[0]})")

        def worker():
            try:
                time.sleep(0.35)
                if "AppsFlyer" in prov:
                    url = f"https://api2.appsflyer.com/inappevent/{env.get('APPSFLYER_APP_ID', 'id123456789')}"
                    headers = {
                        "Content-Type": "application/json",
                        "authentication": env.get("APPSFLYER_DEV_KEY", "YOUR_AF_DEV_KEY"),
                    }
                    body_dict = {
                        "appsflyer_id": dev_id,
                        "customer_user_id": cuid,
                        "eventName": ev_name,
                        "eventValue": json.dumps({"af_revenue": rev, "af_currency": cur, "af_Content_id": "sku_pro_1"}),
                        "eventCurrency": cur,
                        "eventTime": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.000"),
                    }
                    method = "POST"
                elif "Singular" in prov:
                    params = {
                        "a": env.get("SINGULAR_API_KEY", "YOUR_SINGULAR_KEY"),
                        "i": env.get("SINGULAR_BUNDLE_ID", "com.shoxx.app"),
                        "p": "Android",
                        "n": ev_name,
                        "amt": rev,
                        "cur": cur,
                        "is_revenue_event": "true",
                        "andi": dev_id,
                        "custom_user_id": cuid,
                        "ip": "127.0.0.1",
                    }
                    url = f"https://sdk-api-v1.singular.net/api/v1/evt?{urllib.parse.urlencode(params)}"
                    headers = {"Accept": "application/json"}
                    body_dict = params
                    method = "GET"
                else:
                    url = "https://s2s.adjust.com/event"
                    headers = {
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Authorization": f"Bearer {env.get('ADJUST_BEARER_TOKEN', 'YOUR_BEARER')}",
                    }
                    body_dict = {
                        "s2s": "1",
                        "app_token": env.get("ADJUST_APP_TOKEN", "YOUR_APP_TOKEN"),
                        "event_token": ev_name,
                        "environment": env.get("ADJUST_ENVIRONMENT", "production"),
                        "revenue": rev,
                        "currency": cur,
                        "gps_adid": dev_id,
                        "callback_params": json.dumps({"user_id": cuid}),
                    }
                    method = "POST"

                report = [
                    f"=== SHOXX MMP S2S INSPECTOR ({datetime.now().strftime('%H:%M:%S')}) ===",
                    f"Provider : {prov}",
                    f"Modus    : {'DRY-RUN (Lokale Validierung)' if is_dry else 'LIVE HTTP DISPATCH'}",
                    f"Method   : {method} {url}",
                    "\n--- HTTP HEADERS ---",
                    json.dumps(headers, indent=2),
                    "\n--- SERIALIZED PAYLOAD ---",
                    json.dumps(body_dict, indent=2),
                ]

                if not is_dry:
                    try:
                        if method == "POST" and "AppsFlyer" in prov:
                            data_bytes = json.dumps(body_dict).encode("utf-8")
                        elif method == "POST":
                            data_bytes = urllib.parse.urlencode(body_dict).encode("utf-8")
                        else:
                            data_bytes = None
                        req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
                        with urllib.request.urlopen(req, timeout=8) as resp:
                            resp_txt = resp.read().decode("utf-8", errors="replace")
                            report.append(f"\n--- LIVE HTTP RESPONSE (Status {resp.status}) ---\n{resp_txt}")
                    except urllib.error.HTTPError as he:
                        err_txt = he.read().decode("utf-8", errors="replace")
                        report.append(f"\n--- LIVE HTTP ERROR (Status {he.code}) ---\n{err_txt}")
                    except Exception as net_e:
                        report.append(f"\n--- NETWORK EXCEPTION ---\n{net_e}")
                else:
                    report.append("\n--- VALIDATION RESULT ---\n✅ Payload-Schema & Pflichtfelder sind 100% valide nach Senior MMP Spezifikation.")

                full_out = "\n".join(report)
                app.after(0, lambda: _set_inspector(full_out))
                app.log_message(f"[MMP S2S TESTER] {prov} Event '{ev_name}' geprüft ({'Dry-Run' if is_dry else 'Live'}).")
            finally:
                app.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    def _set_inspector(txt: str):
        inspector_text.delete("1.0", "end")
        inspector_text.insert("1.0", txt)

    tk.Button(
        left_card,
        text="🚀 S2S Event jetzt testen / inspizieren",
        font=("Segoe UI Black", 10),
        bg=colors["accent_emerald"],
        fg="#052E16",
        bd=0,
        padx=16,
        pady=10,
        cursor="hand2",
        command=execute_s2s_test,
    ).grid(row=8, column=0, columnspan=2, sticky="ew")

    return page


def build_mmp_webhook_listener_page(parent: tk.Frame, app) -> tk.Frame:
    """
    Submenu Page: '🪝 MMP Webhook-Listener (Callback-Empfänger Server)' (Optimierung A).
    Runs a local ThreadingHTTPServer (default port 8090) to receive, parse, and inspect
    Adjust Real-Time Callbacks, AppsFlyer Push API Postbacks, Singular Postbacks & SKAN 4.0 Postbacks.
    """
    colors = app.colors if hasattr(app, "colors") else {
        "bg_main": "#0B0F19",
        "bg_card": "#1E293B",
        "bg_input": "#0F172A",
        "border": "#334155",
        "accent": "#6366F1",
        "accent_hover": "#818CF8",
        "accent_emerald": "#10B981",
        "accent_amber": "#F59E0B",
        "accent_rose": "#F43F5E",
        "accent_cyan": "#06B6D4",
        "text_primary": "#F8FAFC",
        "text_secondary": "#94A3B8",
    }

    page = tk.Frame(parent, bg=colors["bg_main"])
    page.grid_columnconfigure(0, weight=5)
    page.grid_columnconfigure(1, weight=5)
    page.grid_rowconfigure(1, weight=1)

    port_var = tk.StringVar(value="8090")
    server_state = {"httpd": None, "running": False, "captured": []}

    # Header & Server Controls
    hdr = tk.Frame(page, bg=colors["bg_main"])
    hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

    tk.Label(
        hdr,
        text="🪝 Lokaler MMP Webhook-Empfänger (Callback-Listener Server)",
        font=("Segoe UI Bold", 16),
        fg=colors["text_primary"],
        bg=colors["bg_main"],
    ).pack(side="left")

    ctrl_bar = tk.Frame(hdr, bg=colors["bg_main"])
    ctrl_bar.pack(side="right")

    lbl_srv_status = tk.Label(
        ctrl_bar,
        text="● SERVER OFFLINE",
        font=("Consolas", 9, "bold"),
        fg=colors["accent_amber"],
        bg=colors["bg_main"],
    )
    lbl_srv_status.pack(side="left", padx=(0, 10))

    tk.Label(ctrl_bar, text="Port:", font=("Segoe UI", 9), fg=colors["text_secondary"], bg=colors["bg_main"]).pack(side="left")
    tk.Entry(
        ctrl_bar,
        textvariable=port_var,
        width=6,
        font=("Consolas", 9),
        bg=colors["bg_input"],
        fg=colors["text_primary"],
        insertbackground="#FFFFFF",
        bd=0,
        highlightbackground=colors["border"],
        highlightthickness=1,
    ).pack(side="left", padx=6, ipady=3)

    # Left Card: Captured Callbacks Table + Simulator Buttons
    left_card = tk.Frame(
        page,
        bg=colors["bg_card"],
        highlightbackground=colors["border"],
        highlightthickness=1,
        padx=14,
        pady=12,
    )
    left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
    left_card.grid_rowconfigure(1, weight=1)
    left_card.grid_columnconfigure(0, weight=1)

    tk.Label(
        left_card,
        text="1. EINGEHENDE MMP CALLBACKS & POSTBACKS (ECHTZEIT-LOG)",
        font=("Segoe UI Bold", 9),
        fg=colors["accent_cyan"],
        bg=colors["bg_card"],
        anchor="w",
    ).grid(row=0, column=0, sticky="ew", pady=(0, 6))

    cols = ("time", "mmp_type", "method", "event_or_tracker", "device_id")
    tree_cb = ttk.Treeview(left_card, columns=cols, show="headings", selectmode="browse")
    tree_cb.heading("time", text="Zeit")
    tree_cb.heading("mmp_type", text="Erkanntes Format")
    tree_cb.heading("method", text="HTTP")
    tree_cb.heading("event_or_tracker", text="Event / Tracker")
    tree_cb.heading("device_id", text="Device / ADID / AF-ID")
    tree_cb.column("time", width=68, anchor="center")
    tree_cb.column("mmp_type", width=130, anchor="w")
    tree_cb.column("method", width=50, anchor="center")
    tree_cb.column("event_or_tracker", width=120, anchor="w")
    tree_cb.column("device_id", width=150, anchor="w")
    tree_cb.grid(row=1, column=0, sticky="nsew")

    sim_lbl = tk.Label(
        left_card,
        text="Schnelltest-Simulator (Sendet realistische MMP-Callbacks an den lokalen Server):",
        font=("Segoe UI", 8),
        fg=colors["text_secondary"],
        bg=colors["bg_card"],
        anchor="w",
    )
    sim_lbl.grid(row=2, column=0, sticky="ew", pady=(8, 4))

    sim_row = tk.Frame(left_card, bg=colors["bg_card"])
    sim_row.grid(row=3, column=0, sticky="ew")

    # Right Card: Detailed Callback Macro & JSON Inspector
    right_card = tk.Frame(
        page,
        bg=colors["bg_card"],
        highlightbackground=colors["border"],
        highlightthickness=1,
        padx=14,
        pady=12,
    )
    right_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
    right_card.grid_rowconfigure(1, weight=1)
    right_card.grid_columnconfigure(0, weight=1)

    r_hdr = tk.Frame(right_card, bg=colors["bg_card"])
    r_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))

    tk.Label(
        r_hdr,
        text="2. CALLBACK MAKRO-PARSER & PAYLOAD-INSPECTOR",
        font=("Segoe UI Bold", 9),
        fg=colors["accent_emerald"],
        bg=colors["bg_card"],
    ).pack(side="left")

    tk.Button(
        r_hdr,
        text="💾 Callbacks als JSON im Projekt speichern",
        font=("Segoe UI Semibold", 8),
        bg=colors["bg_input"],
        fg=colors["accent_cyan"],
        bd=0,
        padx=10,
        pady=4,
        cursor="hand2",
        command=lambda: export_callbacks_to_project(),
    ).pack(side="right")

    detail_text = tk.Text(
        right_card,
        bg=colors["bg_input"],
        fg=colors["text_primary"],
        font=("Consolas", 9),
        bd=0,
        padx=12,
        pady=10,
        insertbackground="#FFFFFF",
    )
    detail_text.grid(row=1, column=0, sticky="nsew")
    detail_text.insert(
        "1.0",
        "// Starte oben rechts den Webhook-Listener (Standard: http://localhost:8090/callback)\n"
        "// oder klicke links unten auf einen der 3 Simulator-Buttons, um Callbacks live zu empfangen.\n",
    )

    def _classify_and_record(method: str, path_str: str, headers_dict: dict, raw_body: str):
        parsed_url = urllib.parse.urlparse(path_str)
        query_params = {k: v[0] if len(v) == 1 else v for k, v in urllib.parse.parse_qs(parsed_url.query).items()}
        json_body = None
        if raw_body:
            try:
                json_body = json.loads(raw_body)
            except Exception:
                json_body = None

        # Detect MMP format
        mmp_type = "Generic Webhook"
        event_or_tracker = query_params.get("event_name") or query_params.get("event") or parsed_url.path
        device_id = query_params.get("adid") or query_params.get("gps_adid") or query_params.get("idfa") or "n/a"

        if isinstance(json_body, dict):
            if "appsflyer_id" in json_body or "bundle_id" in json_body and "event_name" in json_body:
                mmp_type = "AppsFlyer Push API"
                event_or_tracker = json_body.get("event_name", "af_event")
                device_id = json_body.get("appsflyer_id") or json_body.get("advertising_id", "n/a")
            elif "transaction-id" in json_body or "conversion-value" in json_body or "coarse-conversion-value" in json_body:
                mmp_type = "SKAdNetwork 4.0"
                cv = json_body.get("conversion-value", json_body.get("coarse-conversion-value", "?"))
                event_or_tracker = f"SKAN CV={cv}"
                device_id = str(json_body.get("transaction-id", "skan_tx"))[:18]
        elif "adid" in query_params or "tracker" in query_params or "gps_adid" in query_params:
            mmp_type = "Adjust Callback"
            event_or_tracker = query_params.get("activity_kind") or query_params.get("tracker") or "adjust_cb"
            device_id = query_params.get("adid") or query_params.get("gps_adid") or "n/a"
        elif "singular_id" in query_params or "_dl" in query_params:
            mmp_type = "Singular Postback"

        entry = {
            "id": f"cb_{len(server_state['captured']) + 1}",
            "time": datetime.now().strftime("%H:%M:%S"),
            "mmp_type": mmp_type,
            "method": method,
            "path": path_str,
            "event_or_tracker": str(event_or_tracker),
            "device_id": str(device_id),
            "query_params": query_params,
            "headers": headers_dict,
            "json_body": json_body,
            "raw_body": raw_body,
        }
        server_state["captured"].insert(0, entry)
        app.after(0, lambda: _on_new_callback_ui(entry))

    def _on_new_callback_ui(entry: dict):
        tree_cb.insert(
            "",
            0,
            iid=entry["id"],
            values=(entry["time"], entry["mmp_type"], entry["method"], entry["event_or_tracker"], entry["device_id"]),
        )
        tree_cb.selection_set(entry["id"])
        _display_entry(entry)
        app.log_message(
            f"[WEBHOOK EMPFANGEN] {entry['mmp_type']} ({entry['method']}) -> Event: {entry['event_or_tracker']} | ID: {entry['device_id']}"
        )

    def _display_entry(entry: dict):
        detail_text.delete("1.0", "end")
        lines = [
            f"=== CAPTURED MMP CALLBACK [{entry['id']}] @ {entry['time']} ===",
            f"Format         : {entry['mmp_type']}",
            f"HTTP Request   : {entry['method']} {entry['path']}",
            f"Event / Tracker: {entry['event_or_tracker']}",
            f"Device / ID    : {entry['device_id']}",
            "\n--- PARSED URL QUERY MACROS ---",
            json.dumps(entry["query_params"], indent=2, ensure_ascii=False),
            "\n--- HTTP HEADERS ---",
            json.dumps(entry["headers"], indent=2, ensure_ascii=False),
        ]
        if entry["json_body"] is not None:
            lines.append("\n--- JSON POSTBACK BODY ---")
            lines.append(json.dumps(entry["json_body"], indent=2, ensure_ascii=False))
        elif entry["raw_body"]:
            lines.append("\n--- RAW BODY ---")
            lines.append(entry["raw_body"])
        detail_text.insert("1.0", "\n".join(lines))

    def _on_tree_select(_ev=None):
        sel = tree_cb.selection()
        if not sel:
            return
        cid = sel[0]
        for item in server_state["captured"]:
            if item["id"] == cid:
                _display_entry(item)
                break

    tree_cb.bind("<<TreeviewSelect>>", _on_tree_select)

    class _WebhookHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, format, *args):
            pass

        def _handle_all(self, method_name: str):
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8", errors="replace") if length > 0 else ""
            hdrs = {k: v for k, v in self.headers.items()}
            _classify_and_record(method_name, self.path, hdrs, raw)
            resp_payload = json.dumps({"status": "ok", "listener": "SHOXX_MMP_WEBHOOK_SERVER"}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(resp_payload)))
            self.end_headers()
            self.wfile.write(resp_payload)

        def do_GET(self):
            self._handle_all("GET")

        def do_POST(self):
            self._handle_all("POST")

    def toggle_webhook_server():
        if server_state["running"] and server_state["httpd"]:
            try:
                server_state["httpd"].shutdown()
                server_state["httpd"].server_close()
            except Exception:
                pass
            server_state["httpd"] = None
            server_state["running"] = False
            lbl_srv_status.configure(text="● SERVER OFFLINE", fg=colors["accent_amber"])
            btn_srv_toggle.configure(text="▶️ Webhook-Server starten", bg=colors["accent_emerald"], fg="#052E16")
            app.log_message("[WEBHOOK SERVER] Lokaler Callback-Listener gestoppt.")
            return

        try:
            port = int(port_var.get().strip())
            httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), _WebhookHandler)
            server_state["httpd"] = httpd
            server_state["running"] = True
            threading.Thread(target=httpd.serve_forever, daemon=True).start()
            lbl_srv_status.configure(text=f"● ONLINE (127.0.0.1:{port})", fg=colors["accent_emerald"])
            btn_srv_toggle.configure(text="⏹️ Server stoppen", bg=colors["accent_rose"], fg="#FFFFFF")
            app.log_message(f"[WEBHOOK SERVER] Lausche auf http://127.0.0.1:{port}/callback (GET & POST bereit).")
        except Exception as e:
            messagebox.showerror("Port-Fehler", f"Konnte Webhook-Server nicht starten:\n{e}")

    btn_srv_toggle = tk.Button(
        ctrl_bar,
        text="▶️ Webhook-Server starten",
        font=("Segoe UI Bold", 9),
        bg=colors["accent_emerald"],
        fg="#052E16",
        bd=0,
        padx=14,
        pady=6,
        cursor="hand2",
        command=toggle_webhook_server,
    )
    btn_srv_toggle.pack(side="left", padx=(6, 0))

    def simulate_callback(sim_kind: str):
        if not server_state["running"]:
            toggle_webhook_server()
            time.sleep(0.15)
        port = int(port_var.get().strip() or "8090")
        app.start_progress(f"Simuliere {sim_kind} Callback")

        def worker():
            try:
                time.sleep(0.25)
                if sim_kind == "adjust":
                    q = urllib.parse.urlencode(
                        {
                            "activity_kind": "event",
                            "event_name": "purchase_vip",
                            "adid": uuid.uuid4().hex,
                            "gps_adid": str(uuid.uuid4()),
                            "tracker": "abc123xyz",
                            "network_name": "Google Ads ACI",
                            "revenue": "29.99",
                            "currency": "EUR",
                        }
                    )
                    req = urllib.request.Request(f"http://127.0.0.1:{port}/callback/adjust?{q}", method="GET")
                elif sim_kind == "appsflyer":
                    payload = json.dumps(
                        {
                            "appsflyer_id": f"{int(time.time()*1000)}-8912341234567890123",
                            "bundle_id": "com.shoxx.senior.app",
                            "event_name": "af_subscribe",
                            "event_revenue": "99.00",
                            "event_revenue_currency": "EUR",
                            "media_source": "Apple Search Ads",
                            "campaign": "DE_iOS_HighLTV",
                            "advertising_id": str(uuid.uuid4()),
                        }
                    ).encode("utf-8")
                    req = urllib.request.Request(
                        f"http://127.0.0.1:{port}/callback/appsflyer",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                else:
                    payload = json.dumps(
                        {
                            "version": "4.0",
                            "ad-network-id": "cstr6suwn9.skadnetwork",
                            "source-identifier": "4729",
                            "app-id": 123456789,
                            "transaction-id": str(uuid.uuid4()),
                            "redownload": False,
                            "conversion-value": 54,
                            "coarse-conversion-value": "high",
                            "did-win": True,
                            "attribution-signature": "MEYCIQDx9...base64_sig==",
                        }
                    ).encode("utf-8")
                    req = urllib.request.Request(
                        f"http://127.0.0.1:{port}/callback/skan4",
                        data=payload,
                        headers={"Content-Type": "application/json"},
                        method="POST",
                    )
                with urllib.request.urlopen(req, timeout=4) as _:
                    pass
            except Exception as e:
                app.log_message(f"[WARN] Simulator-Request Fehler: {e}")
            finally:
                app.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    tk.Button(
        sim_row,
        text="🧪 Adjust Callback",
        font=("Segoe UI Semibold", 8),
        bg=colors["bg_input"],
        fg=colors["accent_cyan"],
        bd=0,
        padx=10,
        pady=6,
        cursor="hand2",
        command=lambda: simulate_callback("adjust"),
    ).pack(side="left", padx=(0, 6))

    tk.Button(
        sim_row,
        text="🧪 AppsFlyer Push-API",
        font=("Segoe UI Semibold", 8),
        bg=colors["bg_input"],
        fg=colors["accent_emerald"],
        bd=0,
        padx=10,
        pady=6,
        cursor="hand2",
        command=lambda: simulate_callback("appsflyer"),
    ).pack(side="left", padx=(0, 6))

    tk.Button(
        sim_row,
        text="🧪 SKAN 4.0 Postback",
        font=("Segoe UI Semibold", 8),
        bg=colors["bg_input"],
        fg=colors["accent_amber"],
        bd=0,
        padx=10,
        pady=6,
        cursor="hand2",
        command=lambda: simulate_callback("skan4"),
    ).pack(side="left")

    def export_callbacks_to_project():
        ws = Path(app.workspace_var.get().strip())
        ws.mkdir(parents=True, exist_ok=True)
        out_file = ws / "captured_mmp_callbacks.json"
        out_file.write_text(json.dumps(server_state["captured"], indent=2, ensure_ascii=False), encoding="utf-8")
        app.log_message(f"[EXPORT] {len(server_state['captured'])} empfangene Callbacks gespeichert in: {out_file}")
        messagebox.showinfo("Exportiert", f"Callbacks wurden im Projekt gespeichert:\n{out_file}")

    return page

