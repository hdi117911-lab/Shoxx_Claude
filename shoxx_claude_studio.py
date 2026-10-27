#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SHOXX CLAUDE CODE STUDIO — Local Open-Weight AI, Project Manager & Senior MMP Coding Suite
v2.8.0 Features:
- High-Tech Animated 30-FPS CyberProgressHUD for all background operations
- Collapsible Sidebar Submenu: '↳ 📡 MMP Live-S2S-Tester & Payload-Inspector'
- Live GPU/VRAM Telemetry (nvidia-smi + ollama ps) & 1-Click VRAM Unload ('ollama stop')
- Project ZIP-Backup Exporter & Git Status / Init Integration
- Project & Folder Manager with per-project .env MMP Keys & Quick-Script-Runner
"""

import os
import sys
import json
import shutil
import subprocess
import threading
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from shoxx_widgets import (
    show_neon_splash,
    CyberProgressHUD,
    query_vram_and_ollama_ps,
    create_project_backup_zip,
    inspect_or_init_git,
    build_mmp_live_tester_page,
    build_mmp_webhook_listener_page,
)

# ---------------------------------------------------------------------------
# APPLICATION CONSTANTS & CONFIGURATION
# ---------------------------------------------------------------------------
APP_TITLE = "SHOXX // CLAUDE CODE LOCAL STUDIO"
APP_VERSION = "3.0.0"
BASE_DIR = Path(__file__).resolve().parent
SPLASH_IMAGE_PATH = BASE_DIR / "bin" / "splash.jpg"
CONFIG_FILE = BASE_DIR / "shoxx_config.json"
PROJECTS_FILE = BASE_DIR / "shoxx_projects.json"
AGENTS_FILE = BASE_DIR / "AGENTS.md"
CLAUDE_MD_FILE = BASE_DIR / "CLAUDE.md"
OLLAMA_INSTALLER_PATH = BASE_DIR / "OllamaSetup.exe"
DEFAULT_PROJECTS_ROOT = BASE_DIR / "projects"

OLLAMA_HOST = "http://localhost:11434"
OLLAMA_DOWNLOAD_URL = "https://ollama.com/download/OllamaSetup.exe"

LOCAL_OLLAMA_DIR = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama"
if LOCAL_OLLAMA_DIR.exists() and str(LOCAL_OLLAMA_DIR) not in os.environ.get("PATH", ""):
    os.environ["PATH"] = f"{LOCAL_OLLAMA_DIR};{os.environ.get('PATH', '')}"

COLORS = {
    "bg_main": "#0B0F19",
    "bg_sidebar": "#111827",
    "bg_card": "#1E293B",
    "bg_card_hover": "#26354D",
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
    "text_muted": "#64748B",
}

CURATED_MODELS = [
    {
        "tag": "dolphin-llama3:8b",
        "name": "Dolphin 2.9 Llama-3 (8B)",
        "category": "Uncensored General & Coding",
        "vram": "~5.5 GB",
        "desc": "Hartford's Dolphin fine-tune auf Llama-3 Basis. Direkt, ungefiltert, stark in Python & JS.",
    },
    {
        "tag": "dolphin-mistral:latest",
        "name": "Dolphin Mistral (7B)",
        "category": "Uncensored Fast Coding",
        "vram": "~4.5 GB",
        "desc": "Schnelles, direktes Modell fuer Scripting, API-Payloads und Debugging.",
    },
    {
        "tag": "dolphin-mixtral:8x7b",
        "name": "Dolphin 2.7 Mixtral (8x7B MoE)",
        "category": "Uncensored Senior Architecture",
        "vram": "~26 GB",
        "desc": "High-End Mixture-of-Experts Modell fuer komplexe Systemarchitektur & MMP-Pipelines.",
    },
    {
        "tag": "llama3-uncensored:8b",
        "name": "Llama-3 Uncensored (8B)",
        "category": "Uncensored Core",
        "vram": "~5.0 GB",
        "desc": "Offenes Llama-3 8B Modell fuer direkte technische Antworten ohne Umwege.",
    },
    {
        "tag": "wizard-vicuna-uncensored:13b",
        "name": "Wizard Vicuna (13B)",
        "category": "Uncensored Reasoning",
        "vram": "~8.0 GB",
        "desc": "Klassisches 13B Modell fuer tiefe Logik und komplexe Transformationen.",
    },
    {
        "tag": "qwen2.5-coder:latest",
        "name": "Qwen 2.5 Coder (7B)",
        "category": "Open-Weight Coding Specialist",
        "vram": "~4.7 GB",
        "desc": "Starkes Code-Modell fuer Claude-Code Tool-Calls, TypeScript, Python & SDK-Integration.",
    },
    {
        "tag": "qwen2.5-coder:14b",
        "name": "Qwen 2.5 Coder (14B Senior)",
        "category": "Open-Weight Senior Coding",
        "vram": "~9.0 GB",
        "desc": "Senior-Level Code-Generierung mit exzellenter Unterstuetzung fuer Claude Code Agent-Workflows.",
    },
    {
        "tag": "deepseek-coder-v2:16b",
        "name": "DeepSeek Coder V2 Lite (16B)",
        "category": "Open-Weight MoE Coder",
        "vram": "~9.5 GB",
        "desc": "Schnelles MoE Coding-Modell mit grossem Kontextfenster fuer umfangreiche Repositories.",
    },
]

MMP_PRESETS = {
    "All-in-One Senior MMP Suite (AppsFlyer + Singular + Adjust)": (
        "Fokus auf alle drei grossen MMPs: AppsFlyer (S2S v2/v3, OneLink, Pull/Push API, SKAN 4.0), "
        "Singular (S2S Event/Session API, Singular Links, Cohort ETL) und Adjust (S2S Event/Session API, "
        "Callback Webhook Listeners, Double-Encoded Params)."
    ),
    "AppsFlyer Senior Architect (S2S v3, OneLink, Conversion Data, SKAN)": (
        "Spezialisierung auf AppsFlyer: Server-to-Server In-App Events API, OneLink Universal/App Links, "
        "Deferred Deep Linking (UDL), Raw Data Reports & SKAdNetwork 4.0 Postback-Verarbeitung."
    ),
    "Singular Senior Architect (S2S API, Attribution, Singular Links, ETL)": (
        "Spezialisierung auf Singular: `/api/v1/launch` & `/api/v1/evt` S2S-Endpunkte, Parameter-Signierung, "
        "Deep-Link-Routing (`_dl`, `_ddl`, `_p`) und asynchrone Reporting-Pipelines."
    ),
    "Adjust Senior Architect (S2S API, Real-Time Callbacks, Signature Auth)": (
        "Spezialisierung auf Adjust: `https://s2s.adjust.com/event` & `/session`, Bearer Token Security, "
        "`callback_params` / `partner_params` Serialisierung und Echtzeit-Webhook-Ingestion."
    ),
}

DEFAULT_ENV_TEMPLATE = {
    "APPSFLYER_APP_ID": "id123456789",
    "APPSFLYER_DEV_KEY": "YOUR_AF_DEV_KEY",
    "SINGULAR_API_KEY": "YOUR_SINGULAR_API_KEY",
    "SINGULAR_BUNDLE_ID": "com.shoxx.app",
    "ADJUST_APP_TOKEN": "YOUR_ADJUST_APP_TOKEN",
    "ADJUST_BEARER_TOKEN": "YOUR_ADJUST_BEARER_TOKEN",
    "ADJUST_ENVIRONMENT": "production",
}

DEFAULT_AGENTS_MD = AGENTS_FILE.read_text(encoding="utf-8") if AGENTS_FILE.exists() else "# AGENTS.md\n"


class ShoxxClaudeStudio(tk.Tk):
    def __init__(self, show_splash: bool = True):
        super().__init__()
        self.colors = COLORS
        self.title(f"{APP_TITLE} v{APP_VERSION}")
        win_w, win_h = 1360, 890
        scr_w = self.winfo_screenwidth()
        scr_h = self.winfo_screenheight()
        pos_x = max(0, (scr_w - win_w) // 2)
        pos_y = max(0, (scr_h - win_h) // 2)
        self.geometry(f"{win_w}x{win_h}+{pos_x}+{pos_y}")
        self.minsize(1160, 780)
        self.configure(bg=COLORS["bg_main"])

        if show_splash and SPLASH_IMAGE_PATH.exists():
            self.withdraw()

        DEFAULT_PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

        self.config_data = self.load_config()
        self.projects_list = self.load_projects()

        self.selected_model_var = tk.StringVar(value=self.config_data.get("active_model", "dolphin-llama3:8b"))
        self.workspace_var = tk.StringVar(value=self.config_data.get("workspace", str(BASE_DIR)))
        self.active_project_name_var = tk.StringVar(value=self.config_data.get("active_project_name", "SHOXX Haupt-Workspace"))
        self.mmp_preset_var = tk.StringVar(value=self.config_data.get("mmp_preset", list(MMP_PRESETS.keys())[0]))
        self.launch_mode_var = tk.StringVar(value=self.config_data.get("launch_mode", "env_bridge"))
        self.ollama_ctx_var = tk.StringVar(value=str(self.config_data.get("ollama_ctx", "32768")))
        self.custom_model_var = tk.StringVar(value="")
        self.initial_prompt_var = tk.StringVar(value="")

        self.new_proj_name_var = tk.StringVar(value="")
        self.new_proj_path_var = tk.StringVar(value=str(DEFAULT_PROJECTS_ROOT))
        self.new_proj_mmp_var = tk.StringVar(value="All-in-One MMP (AppsFlyer + Singular + Adjust)")
        self.new_proj_model_var = tk.StringVar(value=self.selected_model_var.get())
        self.new_proj_template_var = tk.BooleanVar(value=True)

        self.installed_models = []
        self.status_ollama_installed = False
        self.status_ollama_running = False
        self.status_ollama_version = "Nicht installiert"
        self.status_node = False
        self.status_claude = False
        self.vram_info = {"gpu_name": "Prüfe GPU...", "vram_used_mb": 0, "vram_total_mb": 0, "active_models": []}

        self._setup_styles()
        self._build_layout()
        self._ensure_agents_md()
        self._ensure_project_env_file(Path(self.workspace_var.get()))
        self._refresh_projects_ui()
        self.after(200, self.refresh_all_status)

        if show_splash and SPLASH_IMAGE_PATH.exists():
            show_neon_splash(
                self,
                SPLASH_IMAGE_PATH,
                duration_ms=3000,
                on_complete=self._reveal_main_window,
            )

    def _reveal_main_window(self):
        self.deiconify()
        self.lift()
        try:
            self.focus_force()
        except Exception:
            pass

    # -----------------------------------------------------------------------
    # ANIMATED PROGRESS HUD WRAPPERS
    # -----------------------------------------------------------------------
    def start_progress(self, label: str = "ARBEITE..."):
        self.after(0, lambda: self.progress_hud.start_task(label))

    def stop_progress(self, done_label: str = "SYSTEM BEREIT // IDLE"):
        self.after(0, lambda: self.progress_hud.stop_task(done_label))

    # -----------------------------------------------------------------------
    # CONFIG, PROJECTS & .ENV HELPERS
    # -----------------------------------------------------------------------
    def load_config(self) -> dict:
        if CONFIG_FILE.exists():
            try:
                return json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "active_model": "dolphin-llama3:8b",
            "workspace": str(BASE_DIR),
            "active_project_name": "SHOXX Haupt-Workspace",
            "mmp_preset": list(MMP_PRESETS.keys())[0],
            "launch_mode": "env_bridge",
            "ollama_host": OLLAMA_HOST,
            "ollama_ctx": 32768,
        }

    def save_config(self):
        self.config_data["active_model"] = self.selected_model_var.get().strip()
        self.config_data["workspace"] = self.workspace_var.get().strip()
        self.config_data["active_project_name"] = self.active_project_name_var.get().strip()
        self.config_data["mmp_preset"] = self.mmp_preset_var.get().strip()
        self.config_data["launch_mode"] = self.launch_mode_var.get().strip()
        try:
            self.config_data["ollama_ctx"] = int(self.ollama_ctx_var.get().strip())
        except ValueError:
            self.config_data["ollama_ctx"] = 32768
        try:
            CONFIG_FILE.write_text(json.dumps(self.config_data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            self.log_message(f"[WARN] Konfiguration konnte nicht gespeichert werden: {e}")

    def load_projects(self) -> list:
        default_projs = [
            {
                "name": "SHOXX Haupt-Workspace",
                "path": str(BASE_DIR),
                "mmp_stack": "All-in-One MMP",
                "preferred_model": "qwen2.5-coder:latest",
                "last_used": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        ]
        if PROJECTS_FILE.exists():
            try:
                loaded = json.loads(PROJECTS_FILE.read_text(encoding="utf-8"))
                if isinstance(loaded, list) and len(loaded) > 0:
                    for p in loaded:
                        if "preferred_model" not in p:
                            p["preferred_model"] = self.config_data.get("active_model", "dolphin-llama3:8b")
                    return loaded
            except Exception:
                pass
        PROJECTS_FILE.write_text(json.dumps(default_projs, indent=2, ensure_ascii=False), encoding="utf-8")
        return default_projs

    def save_projects(self):
        try:
            PROJECTS_FILE.write_text(json.dumps(self.projects_list, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception as e:
            self.log_message(f"[WARN] Projektliste konnte nicht gespeichert werden: {e}")

    def _ensure_project_env_file(self, project_dir: Path) -> Path:
        project_dir.mkdir(parents=True, exist_ok=True)
        env_path = project_dir / ".env"
        if not env_path.exists():
            lines = ["# SHOXX Senior MMP Project Environment (.env)"]
            for k, v in DEFAULT_ENV_TEMPLATE.items():
                lines.append(f"{k}={v}")
            env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return env_path

    def _read_project_env(self, project_dir: Path) -> dict:
        env_path = self._ensure_project_env_file(project_dir)
        result = dict(DEFAULT_ENV_TEMPLATE)
        try:
            for line in env_path.read_text(encoding="utf-8").splitlines():
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                result[k.strip()] = v.strip().strip('"').strip("'")
        except Exception:
            pass
        return result

    def _write_project_env(self, project_dir: Path, env_dict: dict):
        env_path = project_dir / ".env"
        lines = ["# SHOXX Senior MMP Project Environment (.env)"]
        for k, v in env_dict.items():
            lines.append(f"{k}={v}")
        env_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def _ensure_agents_md(self):
        if not AGENTS_FILE.exists():
            AGENTS_FILE.write_text(DEFAULT_AGENTS_MD, encoding="utf-8")
        if not CLAUDE_MD_FILE.exists():
            CLAUDE_MD_FILE.write_text(AGENTS_FILE.read_text(encoding="utf-8"), encoding="utf-8")

    def _resolve_ollama_bin(self) -> str | None:
        found = shutil.which("ollama")
        if found:
            return found
        candidate = LOCAL_OLLAMA_DIR / "ollama.exe"
        if candidate.exists():
            os.environ["PATH"] = f"{LOCAL_OLLAMA_DIR};{os.environ.get('PATH', '')}"
            return str(candidate)
        return None

    # -----------------------------------------------------------------------
    # TTK STYLING
    # -----------------------------------------------------------------------
    def _setup_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=COLORS["bg_input"],
            foreground=COLORS["text_primary"],
            fieldbackground=COLORS["bg_input"],
            borderwidth=0,
            rowheight=28,
            font=("Segoe UI", 9),
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["bg_card"],
            foreground=COLORS["text_secondary"],
            borderwidth=0,
            font=("Segoe UI Semibold", 9),
        )
        style.map(
            "Treeview",
            background=[("selected", COLORS["accent"])],
            foreground=[("selected", "#FFFFFF")],
        )

        style.configure(
            "TCombobox",
            fieldbackground=COLORS["bg_input"],
            background=COLORS["bg_card"],
            foreground=COLORS["text_primary"],
            arrowcolor=COLORS["text_primary"],
            bordercolor=COLORS["border"],
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", COLORS["bg_input"])],
            selectbackground=[("readonly", COLORS["accent"])],
            selectforeground=[("readonly", "#FFFFFF")],
        )

    # -----------------------------------------------------------------------
    # UI LAYOUT CONSTRUCTION (WITH SUBMENU & CYBER PROGRESS HUD)
    # -----------------------------------------------------------------------
    def _build_layout(self):
        self.grid_columnconfigure(0, weight=0, minsize=270)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar
        self.sidebar = tk.Frame(self, bg=COLORS["bg_sidebar"], width=270)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        brand_frame = tk.Frame(self.sidebar, bg=COLORS["bg_sidebar"], padx=20, pady=18)
        brand_frame.pack(fill="x")

        tk.Label(
            brand_frame,
            text="SHOXX // STUDIO",
            font=("Segoe UI Black", 15),
            fg=COLORS["accent_hover"],
            bg=COLORS["bg_sidebar"],
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            brand_frame,
            text="Local Claude Code + Senior MMP",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_sidebar"],
            anchor="w",
        ).pack(fill="x", pady=(2, 0))

        tk.Frame(self.sidebar, bg=COLORS["border"], height=1).pack(fill="x", padx=16, pady=(0, 10))

        self.nav_buttons = {}
        nav_items = [
            ("home", "🚀  Hauptseite & Launch", False),
            ("projects", "📂  Projekt- & Ordnerverwaltung", False),
            ("models", "🧠  Modell-Verwaltung & 32k", False),
            ("setup", "⚙️  Setup & Ollama Installer", False),
            ("agents", "📜  AGENTS.md & MMP Studio ▾", False),
            ("mmp_tester", "     ↳ 📡 MMP Live-S2S-Tester", True),
            ("mmp_webhooks", "     ↳ 🪝 MMP Webhook-Listener", True),
        ]
        for key, label, is_sub in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=label,
                font=("Segoe UI Semibold" if not is_sub else "Segoe UI", 10 if not is_sub else 9),
                fg=COLORS["text_primary"] if not is_sub else COLORS["accent_cyan"],
                bg=COLORS["bg_sidebar"],
                activebackground=COLORS["bg_card"],
                activeforeground="#FFFFFF",
                bd=0,
                padx=18,
                pady=10 if not is_sub else 7,
                anchor="w",
                cursor="hand2",
                command=lambda k=key: self.show_page(k),
            )
            btn.pack(fill="x", padx=10 if not is_sub else 18, pady=2 if not is_sub else 1)
            self.nav_buttons[key] = btn

        # Sidebar Telemetry + VRAM Monitor Card at Bottom (Optimierung 2)
        status_card = tk.Frame(
            self.sidebar,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        status_card.pack(side="bottom", fill="x", padx=14, pady=14)

        tk.Label(
            status_card,
            text="SYSTEM & VRAM TELEMETRIE",
            font=("Segoe UI Bold", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        self.lbl_side_ollama = tk.Label(
            status_card, text="● Ollama API: Prüfe...", font=("Segoe UI", 9), fg=COLORS["text_secondary"], bg=COLORS["bg_card"], anchor="w"
        )
        self.lbl_side_ollama.pack(fill="x", pady=1)

        self.lbl_side_claude = tk.Label(
            status_card, text="● Claude CLI: Prüfe...", font=("Segoe UI", 9), fg=COLORS["text_secondary"], bg=COLORS["bg_card"], anchor="w"
        )
        self.lbl_side_claude.pack(fill="x", pady=1)

        self.lbl_side_vram = tk.Label(
            status_card, text="● GPU/VRAM: Prüfe...", font=("Consolas", 8), fg=COLORS["accent_emerald"], bg=COLORS["bg_card"], anchor="w"
        )
        self.lbl_side_vram.pack(fill="x", pady=(2, 1))

        self.lbl_side_proj = tk.Label(
            status_card,
            textvariable=self.active_project_name_var,
            font=("Segoe UI Semibold", 9),
            fg=COLORS["accent_amber"],
            bg=COLORS["bg_card"],
            anchor="w",
        )
        self.lbl_side_proj.pack(fill="x", pady=(3, 0))

        self.lbl_side_model = tk.Label(
            status_card,
            textvariable=self.selected_model_var,
            font=("Consolas", 9, "bold"),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"],
            anchor="w",
        )
        self.lbl_side_model.pack(fill="x", pady=(1, 0))

        # 2. Main Container (Pages + Animated CyberProgressHUD + Log Console)
        self.main_area = tk.Frame(self, bg=COLORS["bg_main"])
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_rowconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=0)
        self.main_area.grid_rowconfigure(2, weight=0)
        self.main_area.grid_columnconfigure(0, weight=1)

        self.pages_container = tk.Frame(self.main_area, bg=COLORS["bg_main"])
        self.pages_container.grid(row=0, column=0, sticky="nsew", padx=22, pady=(14, 6))
        self.pages_container.grid_rowconfigure(0, weight=1)
        self.pages_container.grid_columnconfigure(0, weight=1)

        # Animated CyberProgressHUD bar
        self.progress_hud = CyberProgressHUD(self.main_area, COLORS)
        self.progress_hud.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 6))

        # Build Pages
        self.pages = {}
        self._build_page_home()
        self._build_page_projects()
        self._build_page_models()
        self._build_page_setup()
        self._build_page_agents()
        self.pages["mmp_tester"] = build_mmp_live_tester_page(self.pages_container, self)
        self.pages["mmp_webhooks"] = build_mmp_webhook_listener_page(self.pages_container, self)

        # Bottom Live Terminal Log
        log_frame = tk.Frame(
            self.main_area,
            bg=COLORS["bg_sidebar"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        )
        log_frame.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 14))

        log_header = tk.Frame(log_frame, bg=COLORS["bg_sidebar"], padx=10, pady=4)
        log_header.pack(fill="x")

        tk.Label(
            log_header,
            text="⚡ LIVE SYSTEM-, SKRIPT- & PROZESS-KONSOLE",
            font=("Consolas", 9, "bold"),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_sidebar"],
        ).pack(side="left")

        tk.Button(
            log_header,
            text="Konsole leeren",
            font=("Segoe UI", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            bd=0,
            padx=8,
            pady=2,
            cursor="hand2",
            command=self.clear_log,
        ).pack(side="right")

        self.log_text = tk.Text(
            log_frame,
            height=5,
            bg="#070A12",
            fg="#E2E8F0",
            font=("Consolas", 9),
            bd=0,
            padx=10,
            pady=6,
            insertbackground="#FFFFFF",
        )
        self.log_text.pack(fill="x")
        self.log_message("SHOXX Studio v3.0 initialisiert — Neon-Splash, CyberProgressHUD, VRAM-Monitor, S2S-Tester & Webhook-Listener bereit.")

        self.show_page("home")

    def show_page(self, page_key: str):
        for k, frame in self.pages.items():
            frame.grid_forget()
        self.pages[page_key].grid(row=0, column=0, sticky="nsew")

        for k, btn in self.nav_buttons.items():
            if k == page_key:
                btn.configure(bg=COLORS["accent"], fg="#FFFFFF")
            else:
                is_sub = k in ("mmp_tester", "mmp_webhooks")
                btn.configure(
                    bg=COLORS["bg_sidebar"],
                    fg=COLORS["accent_cyan"] if is_sub else COLORS["text_primary"],
                )

        if page_key == "projects":
            self._refresh_project_files_tree()

    # -----------------------------------------------------------------------
    # PAGE 1: HAUPTSEITE (DASHBOARD & CLAUDE CODE LAUNCHER)
    # -----------------------------------------------------------------------
    def _build_page_home(self):
        page = tk.Frame(self.pages_container, bg=COLORS["bg_main"])
        self.pages["home"] = page

        hdr = tk.Frame(page, bg=COLORS["bg_main"])
        hdr.pack(fill="x", pady=(0, 12))

        tk.Label(
            hdr,
            text="Claude Code — Local Open-Weight Launchpad",
            font=("Segoe UI Bold", 18),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_main"],
        ).pack(side="left")

        tk.Button(
            hdr,
            text="🔄 Status & VRAM aktualisieren",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
            activebackground=COLORS["accent"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.refresh_all_status,
        ).pack(side="right")

        kpi_row = tk.Frame(page, bg=COLORS["bg_main"])
        kpi_row.pack(fill="x", pady=(0, 12))
        for i in range(4):
            kpi_row.grid_columnconfigure(i, weight=1, uniform="kpi")

        self.card_kpi_ollama = self._create_kpi_card(
            kpi_row, 0, "OLLAMA LOCAL ENGINE", "Prüfe...", "Anthropic Bridge (Port 11434)"
        )
        self.card_kpi_claude = self._create_kpi_card(
            kpi_row, 1, "GPU & VRAM MONITOR", "Prüfe...", "Hardware & Geladene Modelle"
        )
        self.card_kpi_model = self._create_kpi_card(
            kpi_row, 2, "AKTIVES LOKALES MODELL", self.selected_model_var.get(), "Uncensored / Open-Weight"
        )
        self.card_kpi_project = self._create_kpi_card(
            kpi_row, 3, "AKTIVES PROJEKT", self.active_project_name_var.get(), self.workspace_var.get()
        )

        launch_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=20,
            pady=15,
        )
        launch_card.pack(fill="x", pady=(0, 12))
        launch_card.grid_columnconfigure(1, weight=1)

        tk.Label(
            launch_card,
            text="1. PROJEKT-ORDNER & LOKALES KI-MODELL FÜR DEN START AUSWÄHLEN",
            font=("Segoe UI Bold", 10),
            fg=COLORS["accent_hover"],
            bg=COLORS["bg_card"],
        ).grid(row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        tk.Label(
            launch_card,
            text="Gespeichertes Projekt wählen:",
            font=("Segoe UI Semibold", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).grid(row=1, column=0, sticky="w", padx=(0, 14), pady=5)

        self.combo_home_projects = ttk.Combobox(
            launch_card,
            textvariable=self.active_project_name_var,
            font=("Segoe UI Semibold", 10),
            state="readonly",
        )
        self.combo_home_projects.grid(row=1, column=1, sticky="ew", pady=5)
        self.combo_home_projects.bind("<<ComboboxSelected>>", self._on_home_project_selected)

        tk.Button(
            launch_card,
            text="🔐 Projekt .env / Keys",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_emerald"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.open_project_env_dialog,
        ).grid(row=1, column=2, padx=(10, 0), pady=5)

        tk.Button(
            launch_card,
            text="📂 Projektverwaltung →",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_amber"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda: self.show_page("projects"),
        ).grid(row=1, column=3, padx=(6, 0), pady=5)

        tk.Label(
            launch_card,
            text="Aktiver Projekt-Ordnerpfad:",
            font=("Segoe UI Semibold", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).grid(row=2, column=0, sticky="w", padx=(0, 14), pady=5)

        tk.Entry(
            launch_card,
            textvariable=self.workspace_var,
            font=("Consolas", 10),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground="#FFFFFF",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        ).grid(row=2, column=1, sticky="ew", pady=5, ipady=5)

        tk.Button(
            launch_card,
            text="📁 Ordner wechseln",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.browse_workspace,
        ).grid(row=2, column=2, padx=(10, 0), pady=5)

        tk.Button(
            launch_card,
            text="🔍 Im Explorer",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.open_workspace_in_explorer,
        ).grid(row=2, column=3, padx=(6, 0), pady=5)

        tk.Label(
            launch_card,
            text="Aktives KI-Modell (Lokal):",
            font=("Segoe UI Semibold", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).grid(row=3, column=0, sticky="w", padx=(0, 14), pady=5)

        self.combo_models = ttk.Combobox(
            launch_card,
            textvariable=self.selected_model_var,
            font=("Consolas", 10),
            state="normal",
        )
        self.combo_models.grid(row=3, column=1, sticky="ew", pady=5)
        self.combo_models.bind("<<ComboboxSelected>>", lambda e: self.on_model_changed())

        tk.Button(
            launch_card,
            text="⚡ 32k-MMP Klon bauen",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_hover"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.create_32k_mmp_model_from_active,
        ).grid(row=3, column=2, padx=(10, 0), pady=5)

        tk.Button(
            launch_card,
            text="🧠 Modelle →",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=lambda: self.show_page("models"),
        ).grid(row=3, column=3, padx=(6, 0), pady=5)

        tk.Label(
            launch_card,
            text="Senior MMP Coding Fokus:",
            font=("Segoe UI Semibold", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).grid(row=4, column=0, sticky="w", padx=(0, 14), pady=5)

        self.combo_mmp = ttk.Combobox(
            launch_card,
            textvariable=self.mmp_preset_var,
            values=list(MMP_PRESETS.keys()),
            font=("Segoe UI", 10),
            state="readonly",
        )
        self.combo_mmp.grid(row=4, column=1, columnspan=3, sticky="ew", pady=5)
        self.combo_mmp.bind("<<ComboboxSelected>>", lambda e: self.save_config())

        tk.Label(
            launch_card,
            text="Start-Prompt (Optional):",
            font=("Segoe UI Semibold", 10),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
        ).grid(row=5, column=0, sticky="w", padx=(0, 14), pady=5)

        tk.Entry(
            launch_card,
            textvariable=self.initial_prompt_var,
            font=("Segoe UI", 10),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground="#FFFFFF",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        ).grid(row=5, column=1, columnspan=3, sticky="ew", pady=5, ipady=5)

        action_bar = tk.Frame(launch_card, bg=COLORS["bg_card"], pady=10)
        action_bar.grid(row=6, column=0, columnspan=4, sticky="ew")

        tk.Radiobutton(
            action_bar,
            text="Anthropic-Ollama Bridge (ANTHROPIC_BASE_URL=localhost:11434)",
            variable=self.launch_mode_var,
            value="env_bridge",
            font=("Segoe UI", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            selectcolor=COLORS["bg_input"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_primary"],
        ).pack(side="left", padx=(0, 16))

        tk.Radiobutton(
            action_bar,
            text="Native Ollama Launcher (ollama launch claude)",
            variable=self.launch_mode_var,
            value="ollama_launch",
            font=("Segoe UI", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            selectcolor=COLORS["bg_input"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_primary"],
        ).pack(side="left")

        btn_launch = tk.Button(
            action_bar,
            text="🚀  START: CLAUDE CODE IM GEWÄHLTEN PROJEKT-ORDNER ÖFFNEN",
            font=("Segoe UI Black", 10),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            activebackground="#34D399",
            activeforeground="#052E16",
            bd=0,
            padx=20,
            pady=10,
            cursor="hand2",
            command=self.launch_claude_code,
        )
        btn_launch.pack(side="right")

        mmp_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=20,
            pady=13,
        )
        mmp_card.pack(fill="x")

        tk.Label(
            mmp_card,
            text="2. SENIOR MMP CODING SCRIPTS & LIVE S2S-TESTER",
            font=("Segoe UI Bold", 10),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(0, 4))

        mmp_btn_row = tk.Frame(mmp_card, bg=COLORS["bg_card"])
        mmp_btn_row.pack(fill="x", pady=(4, 0))

        tk.Button(
            mmp_btn_row,
            text="⚡ AppsFlyer S2S Script",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda: self.generate_mmp_template("appsflyer"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            mmp_btn_row,
            text="⚡ Singular S2S Script",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda: self.generate_mmp_template("singular"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            mmp_btn_row,
            text="⚡ Adjust S2S Script",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda: self.generate_mmp_template("adjust"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            mmp_btn_row,
            text="📡 MMP Live-S2S-Tester öffnen",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=lambda: self.show_page("mmp_tester"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            mmp_btn_row,
            text="📦 Alle 3 MMP Senior-Suites erstellen",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=lambda: self.generate_mmp_template("all"),
        ).pack(side="right")

    def _create_kpi_card(self, parent, col, title, value, subtitle):
        card = tk.Frame(
            parent,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 8, 0))

        lbl_title = tk.Label(card, text=title, font=("Segoe UI Bold", 8), fg=COLORS["text_secondary"], bg=COLORS["bg_card"], anchor="w")
        lbl_title.pack(fill="x")

        lbl_val = tk.Label(card, text=value, font=("Segoe UI Black", 11), fg=COLORS["text_primary"], bg=COLORS["bg_card"], anchor="w")
        lbl_val.pack(fill="x", pady=(3, 2))

        lbl_sub = tk.Label(card, text=subtitle, font=("Segoe UI", 8), fg=COLORS["text_muted"], bg=COLORS["bg_card"], anchor="w")
        lbl_sub.pack(fill="x")

        return {"frame": card, "val": lbl_val, "sub": lbl_sub}

    # -----------------------------------------------------------------------
    # PAGE 2: PROJEKT- & ORDNERVERWALTUNG (+ ZIP BACKUP & GIT INTEGRATION)
    # -----------------------------------------------------------------------
    def _build_page_projects(self):
        page = tk.Frame(self.pages_container, bg=COLORS["bg_main"])
        self.pages["projects"] = page
        page.grid_columnconfigure(0, weight=3)
        page.grid_columnconfigure(1, weight=2)
        page.grid_rowconfigure(1, weight=1)
        page.grid_rowconfigure(2, weight=1)

        hdr = tk.Frame(page, bg=COLORS["bg_main"])
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        tk.Label(
            hdr,
            text="Projekt- & Ordnerverwaltung — .env Profile, ZIP-Backup, Git & Quick-Runner",
            font=("Segoe UI Bold", 15),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_main"],
        ).pack(side="left")

        tk.Button(
            hdr,
            text="🚀 Ausgewähltes Projekt aktivieren & Claude Code starten",
            font=("Segoe UI Black", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            activebackground="#34D399",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            command=self.activate_and_launch_selected_project,
        ).pack(side="right")

        left_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8), pady=(0, 8))
        left_card.grid_rowconfigure(1, weight=1)
        left_card.grid_columnconfigure(0, weight=1)

        top_l = tk.Frame(left_card, bg=COLORS["bg_card"])
        top_l.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        tk.Label(
            top_l,
            text="1. VERWALTETE PROJEKTE & ARBEITSORDNER",
            font=("Segoe UI Bold", 9),
            fg=COLORS["accent_hover"],
            bg=COLORS["bg_card"],
        ).pack(side="left")

        self.lbl_git_status = tk.Label(
            top_l,
            text="Git: Prüfe...",
            font=("Consolas", 8, "bold"),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"],
        )
        self.lbl_git_status.pack(side="right")

        p_cols = ("name", "preferred_model", "mmp_stack", "path")
        self.tree_projects = ttk.Treeview(left_card, columns=p_cols, show="headings", selectmode="browse", height=5)
        self.tree_projects.heading("name", text="Projektname")
        self.tree_projects.heading("preferred_model", text="Projekt-Modell")
        self.tree_projects.heading("mmp_stack", text="MMP Stack")
        self.tree_projects.heading("path", text="Ordnerpfad")
        self.tree_projects.column("name", width=140, anchor="w")
        self.tree_projects.column("preferred_model", width=130, anchor="w")
        self.tree_projects.column("mmp_stack", width=115, anchor="w")
        self.tree_projects.column("path", width=220, anchor="w")
        self.tree_projects.grid(row=1, column=0, sticky="nsew")
        self.tree_projects.bind("<<TreeviewSelect>>", self._on_project_tree_select)
        self.tree_projects.bind("<Double-1>", lambda e: self.activate_and_launch_selected_project())

        proj_btn_bar = tk.Frame(left_card, bg=COLORS["bg_card"])
        proj_btn_bar.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        tk.Button(
            proj_btn_bar,
            text="✅ Aktivieren",
            font=("Segoe UI Semibold", 8),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            bd=0,
            padx=9,
            pady=6,
            cursor="hand2",
            command=self.set_selected_project_active,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            proj_btn_bar,
            text="🔐 .env Keys",
            font=("Segoe UI Semibold", 8),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_emerald"],
            bd=0,
            padx=9,
            pady=6,
            cursor="hand2",
            command=self.open_project_env_dialog,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            proj_btn_bar,
            text="📦 ZIP-Backup",
            font=("Segoe UI Semibold", 8),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_amber"],
            bd=0,
            padx=9,
            pady=6,
            cursor="hand2",
            command=self.backup_active_project_zip,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            proj_btn_bar,
            text="🔧 Git Init & Status",
            font=("Segoe UI Semibold", 8),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=9,
            pady=6,
            cursor="hand2",
            command=self.init_or_check_git_active_project,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            proj_btn_bar,
            text="📂 Import",
            font=("Segoe UI", 8),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.import_existing_folder_as_project,
        ).pack(side="left", padx=(0, 5))

        tk.Button(
            proj_btn_bar,
            text="🗑️",
            font=("Segoe UI", 8),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_rose"],
            bd=0,
            padx=8,
            pady=6,
            cursor="hand2",
            command=self.remove_selected_project,
        ).pack(side="right")

        # Bottom-Left Panel: File Tree & Quick-Runner
        files_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=14,
            pady=10,
        )
        files_card.grid(row=2, column=0, sticky="nsew", padx=(0, 8))
        files_card.grid_rowconfigure(1, weight=1)
        files_card.grid_columnconfigure(0, weight=1)

        f_hdr = tk.Frame(files_card, bg=COLORS["bg_card"])
        f_hdr.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        tk.Label(
            f_hdr,
            text="2. PROJEKT-DATEIEN & QUICK-SCRIPT-RUNNER (INKL. .ENV INJEKTION)",
            font=("Segoe UI Bold", 9),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"],
        ).pack(side="left")

        tk.Button(
            f_hdr,
            text="🔄 Dateien aktualisieren",
            font=("Segoe UI", 8),
            bg=COLORS["bg_input"],
            fg=COLORS["text_secondary"],
            bd=0,
            padx=8,
            pady=3,
            cursor="hand2",
            command=self._refresh_project_files_tree,
        ).pack(side="right")

        f_cols = ("rel_path", "type", "size")
        self.tree_proj_files = ttk.Treeview(files_card, columns=f_cols, show="headings", selectmode="browse", height=5)
        self.tree_proj_files.heading("rel_path", text="Datei im aktiven Projekt")
        self.tree_proj_files.heading("type", text="Typ")
        self.tree_proj_files.heading("size", text="Größe")
        self.tree_proj_files.column("rel_path", width=360, anchor="w")
        self.tree_proj_files.column("type", width=110, anchor="center")
        self.tree_proj_files.column("size", width=90, anchor="e")
        self.tree_proj_files.grid(row=1, column=0, sticky="nsew")

        f_actions = tk.Frame(files_card, bg=COLORS["bg_card"])
        f_actions.grid(row=2, column=0, sticky="ew", pady=(8, 0))

        tk.Button(
            f_actions,
            text="▶️ Ausgewähltes Skript direkt ausführen",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.run_selected_project_script,
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            f_actions,
            text="🤖 Datei gezielt in Claude Code öffnen & bearbeiten",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.launch_claude_on_selected_file,
        ).pack(side="left")

        # Right Panel: Create New Project Wizard
        right_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=18,
            pady=14,
        )
        right_card.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(8, 0))
        right_card.grid_columnconfigure(0, weight=1)

        tk.Label(
            right_card,
            text="✨ NEUES PROJEKT / NEUEN ORDNER ANLEGEN",
            font=("Segoe UI Bold", 10),
            fg=COLORS["accent_emerald"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        tk.Label(
            right_card,
            text="Projektname (Ordnername):",
            font=("Segoe UI Semibold", 9),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(2, 2))

        tk.Entry(
            right_card,
            textvariable=self.new_proj_name_var,
            font=("Segoe UI", 10),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground="#FFFFFF",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        ).pack(fill="x", ipady=5, pady=(0, 8))

        tk.Label(
            right_card,
            text="Übergeordnetes Stammverzeichnis:",
            font=("Segoe UI Semibold", 9),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(2, 2))

        path_row = tk.Frame(right_card, bg=COLORS["bg_card"])
        path_row.pack(fill="x", pady=(0, 8))
        path_row.grid_columnconfigure(0, weight=1)

        tk.Entry(
            path_row,
            textvariable=self.new_proj_path_var,
            font=("Consolas", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground="#FFFFFF",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        ).grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 6))

        tk.Button(
            path_row,
            text="📂 Wählen",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=10,
            pady=5,
            cursor="hand2",
            command=self._browse_new_project_parent,
        ).grid(row=0, column=1)

        tk.Label(
            right_card,
            text="Bevorzugtes lokales Modell für dieses Projekt:",
            font=("Segoe UI Semibold", 9),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(2, 2))

        self.combo_new_proj_model = ttk.Combobox(
            right_card,
            textvariable=self.new_proj_model_var,
            values=[m["tag"] for m in CURATED_MODELS],
            font=("Consolas", 9),
        )
        self.combo_new_proj_model.pack(fill="x", pady=(0, 8))

        tk.Label(
            right_card,
            text="MMP Fokus / Architektur-Vorlage:",
            font=("Segoe UI Semibold", 9),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(2, 2))

        ttk.Combobox(
            right_card,
            textvariable=self.new_proj_mmp_var,
            values=[
                "All-in-One MMP (AppsFlyer + Singular + Adjust)",
                "AppsFlyer Senior S2S & OneLink",
                "Singular S2S & Attribution ETL",
                "Adjust S2S & Real-Time Callbacks",
                "Leeres Custom Coding Projekt",
            ],
            font=("Segoe UI", 9),
            state="readonly",
        ).pack(fill="x", pady=(0, 10))

        tk.Checkbutton(
            right_card,
            text="AGENTS.md, CLAUDE.md, .env, Git-Repo & passende Senior-MMP-Skripte direkt erzeugen",
            variable=self.new_proj_template_var,
            font=("Segoe UI", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_secondary"],
            selectcolor=COLORS["bg_input"],
            activebackground=COLORS["bg_card"],
            activeforeground=COLORS["text_primary"],
            wraplength=360,
            justify="left",
        ).pack(fill="x", pady=(0, 12))

        tk.Button(
            right_card,
            text="➕ Projektordner erstellen & aktivieren",
            font=("Segoe UI Bold", 10),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            activebackground=COLORS["accent_hover"],
            bd=0,
            padx=16,
            pady=9,
            cursor="hand2",
            command=lambda: self.create_new_project(launch_immediately=False),
        ).pack(fill="x", pady=(0, 8))

        tk.Button(
            right_card,
            text="🚀 Projektordner erstellen & SOFORT Claude Code starten",
            font=("Segoe UI Black", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            activebackground="#34D399",
            bd=0,
            padx=16,
            pady=9,
            cursor="hand2",
            command=lambda: self.create_new_project(launch_immediately=True),
        ).pack(fill="x")

    # -----------------------------------------------------------------------
    # PROJECT MANAGEMENT, ZIP BACKUP & GIT LOGIC
    # -----------------------------------------------------------------------
    def backup_active_project_zip(self):
        ws = Path(self.workspace_var.get().strip())
        if not ws.exists():
            return
        self.start_progress(f"Erstelle Projekt ZIP-Backup ({ws.name})")

        def worker():
            try:
                zip_p = create_project_backup_zip(ws, include_env=False)
                self.log_message(f"[BACKUP] Projekt '{ws.name}' erfolgreich als ZIP gesichert: {zip_p}")
            except Exception as e:
                self.log_message(f"[ERROR] Backup fehlgeschlagen: {e}")
            finally:
                self.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    def init_or_check_git_active_project(self):
        ws = Path(self.workspace_var.get().strip())
        ws.mkdir(parents=True, exist_ok=True)
        self.start_progress(f"Prüfe / Initialisiere Git ({ws.name})")

        def worker():
            try:
                summary = inspect_or_init_git(ws, init_if_missing=True)
                self.after(0, lambda: self.lbl_git_status.configure(text=summary))
                self.log_message(f"[GIT] {ws.name}: {summary}")
            finally:
                self.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    def _refresh_projects_ui(self):
        if hasattr(self, "tree_projects"):
            for item in self.tree_projects.get_children():
                self.tree_projects.delete(item)
            for idx, proj in enumerate(self.projects_list):
                iid = f"proj_{idx}"
                self.tree_projects.insert(
                    "",
                    "end",
                    iid=iid,
                    values=(
                        proj.get("name", "Projekt"),
                        proj.get("preferred_model", self.selected_model_var.get()),
                        proj.get("mmp_stack", "All-in-One MMP"),
                        proj.get("path", ""),
                    ),
                )

        if hasattr(self, "combo_home_projects"):
            names = [p.get("name", "") for p in self.projects_list]
            self.combo_home_projects["values"] = names

        if hasattr(self, "card_kpi_project"):
            self.card_kpi_project["val"].configure(text=self.active_project_name_var.get(), fg=COLORS["accent_amber"])
            self.card_kpi_project["sub"].configure(text=self.workspace_var.get())

        ws = Path(self.workspace_var.get().strip())
        if hasattr(self, "lbl_git_status") and ws.exists():
            self.lbl_git_status.configure(text=inspect_or_init_git(ws, init_if_missing=False))

        self._refresh_project_files_tree()

    def _refresh_project_files_tree(self):
        if not hasattr(self, "tree_proj_files"):
            return
        for item in self.tree_proj_files.get_children():
            self.tree_proj_files.delete(item)

        ws = Path(self.workspace_var.get().strip())
        if not ws.exists():
            return

        allowed_exts = {".py", ".ts", ".js", ".ps1", ".bat", ".json", ".md", ".env"}
        files_found = []
        try:
            for p in ws.rglob("*"):
                if p.is_file() and (p.suffix.lower() in allowed_exts or p.name == ".env"):
                    if any(skip in p.parts for skip in (".git", "node_modules", "__pycache__", "_shoxx_backups")):
                        continue
                    rel = str(p.relative_to(ws))
                    size_kb = f"{round(p.stat().st_size / 1024, 1)} KB"
                    ftype = "Python Script" if p.suffix == ".py" else (
                        "Env Config" if p.name == ".env" else p.suffix.upper().lstrip(".")
                    )
                    files_found.append((rel, ftype, size_kb, str(p)))
        except Exception:
            pass

        files_found.sort(key=lambda x: (0 if x[0].endswith(".py") else 1, x[0].lower()))
        for rel, ftype, size_kb, full_p in files_found[:80]:
            self.tree_proj_files.insert("", "end", iid=full_p, values=(rel, ftype, size_kb))

    def run_selected_project_script(self):
        sel = self.tree_proj_files.selection()
        if not sel:
            messagebox.showinfo("Skript auswählen", "Bitte wähle unten in der Dateiliste ein Skript (.py, .js, .ps1) zum Ausführen aus.")
            return
        file_path = Path(sel[0])
        if not file_path.exists():
            return

        ws = Path(self.workspace_var.get().strip())
        proj_env = self._read_project_env(ws)

        if file_path.suffix.lower() == ".py":
            cmd = [sys.executable, str(file_path)]
        elif file_path.suffix.lower() == ".js":
            cmd = ["node", str(file_path)]
        elif file_path.suffix.lower() == ".ps1":
            cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(file_path)]
        else:
            messagebox.showinfo("Hinweis", f"Dateityp '{file_path.suffix}' ist kein direkt ausführbares Skript (.py / .js / .ps1).")
            return

        self.start_progress(f"Führe Skript aus: {file_path.name}")
        self.log_message(f"[QUICK-RUNNER] Starte '{file_path.name}' im Projekt '{ws.name}' (inkl. .env Variablen)...")

        def worker():
            env = os.environ.copy()
            env.update(proj_env)
            try:
                proc = subprocess.Popen(
                    cmd,
                    cwd=str(ws),
                    env=env,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log_message(f"[{file_path.name}] {line.strip()}")
                proc.wait()
                self.log_message(f"[QUICK-RUNNER] '{file_path.name}' beendet (Exit-Code: {proc.returncode}).")
            except Exception as e:
                self.log_message(f"[ERROR] Skript-Ausführung fehlgeschlagen: {e}")
            finally:
                self.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    def launch_claude_on_selected_file(self):
        sel = self.tree_proj_files.selection()
        if not sel:
            messagebox.showinfo("Datei auswählen", "Bitte wähle eine Datei aus der Projekt-Dateiliste aus.")
            return
        file_path = Path(sel[0])
        ws = Path(self.workspace_var.get().strip())
        try:
            rel = file_path.relative_to(ws)
        except ValueError:
            rel = file_path.name

        self.initial_prompt_var.set(f"Analysiere und optimiere die Datei {rel} nach unseren Senior MMP Richtlinien in AGENTS.md.")
        self.launch_claude_code()

    def open_project_env_dialog(self):
        ws = Path(self.workspace_var.get().strip())
        env_data = self._read_project_env(ws)

        dlg = tk.Toplevel(self)
        dlg.title(f"Projekt-Profil & .env MMP Keys — {self.active_project_name_var.get()}")
        dlg.geometry("620x480")
        dlg.configure(bg=COLORS["bg_card"])
        dlg.transient(self)
        dlg.grab_set()

        tk.Label(
            dlg,
            text=f"🔐 PROJEKT-.ENV & MODELL-PROFIL ({self.active_project_name_var.get()})",
            font=("Segoe UI Bold", 11),
            fg=COLORS["accent_emerald"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", padx=20, pady=(16, 4))

        tk.Label(
            dlg,
            text=f"Gespeichert in: {ws / '.env'} (Wird automatisch an Claude Code & Skripte übergeben)",
            font=("Consolas", 8),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", padx=20, pady=(0, 12))

        form = tk.Frame(dlg, bg=COLORS["bg_card"], padx=20)
        form.pack(fill="both", expand=True)
        form.grid_columnconfigure(1, weight=1)

        tk.Label(
            form,
            text="Bevorzugtes Modell:",
            font=("Segoe UI Semibold", 9),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"],
        ).grid(row=0, column=0, sticky="w", pady=5, padx=(0, 12))

        proj_model_var = tk.StringVar(value=self.selected_model_var.get())
        for p in self.projects_list:
            if Path(p.get("path", "")) == ws:
                proj_model_var.set(p.get("preferred_model", self.selected_model_var.get()))
                break

        ttk.Combobox(
            form,
            textvariable=proj_model_var,
            values=self.combo_models["values"] if hasattr(self, "combo_models") else [m["tag"] for m in CURATED_MODELS],
            font=("Consolas", 9),
        ).grid(row=0, column=1, sticky="ew", pady=5)

        entry_vars = {}
        row_idx = 1
        for k, default_v in DEFAULT_ENV_TEMPLATE.items():
            tk.Label(
                form,
                text=f"{k}:",
                font=("Consolas", 9),
                fg=COLORS["text_primary"],
                bg=COLORS["bg_card"],
            ).grid(row=row_idx, column=0, sticky="w", pady=4, padx=(0, 12))

            v_var = tk.StringVar(value=env_data.get(k, default_v))
            entry_vars[k] = v_var
            tk.Entry(
                form,
                textvariable=v_var,
                font=("Consolas", 9),
                bg=COLORS["bg_input"],
                fg=COLORS["text_primary"],
                insertbackground="#FFFFFF",
                bd=0,
                highlightbackground=COLORS["border"],
                highlightthickness=1,
            ).grid(row=row_idx, column=1, sticky="ew", ipady=4, pady=4)
            row_idx += 1

        def save_and_close():
            new_env = {k: var.get().strip() for k, var in entry_vars.items()}
            self._write_project_env(ws, new_env)
            chosen_m = proj_model_var.get().strip()
            for p in self.projects_list:
                if Path(p.get("path", "")) == ws:
                    p["preferred_model"] = chosen_m
            self.selected_model_var.set(chosen_m)
            self.save_projects()
            self.save_config()
            self._refresh_projects_ui()
            self.log_message(f"[PROJEKT .ENV] MMP-Keys & Modell ('{chosen_m}') für '{ws.name}' gespeichert.")
            dlg.destroy()

        btn_row = tk.Frame(dlg, bg=COLORS["bg_card"], padx=20, pady=14)
        btn_row.pack(fill="x")

        tk.Button(
            btn_row,
            text="💾 .env & Modell-Profil speichern",
            font=("Segoe UI Bold", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            bd=0,
            padx=16,
            pady=8,
            cursor="hand2",
            command=save_and_close,
        ).pack(side="right")

        tk.Button(
            btn_row,
            text="Abbrechen",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_secondary"],
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=dlg.destroy,
        ).pack(side="right", padx=(0, 8))

    def _on_home_project_selected(self, _event=None):
        chosen_name = self.active_project_name_var.get()
        for proj in self.projects_list:
            if proj.get("name") == chosen_name:
                self.workspace_var.set(proj.get("path", str(BASE_DIR)))
                if proj.get("preferred_model"):
                    self.selected_model_var.set(proj["preferred_model"])
                proj["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self._ensure_project_env_file(Path(self.workspace_var.get()))
                self.save_projects()
                self.save_config()
                self._refresh_projects_ui()
                self.log_message(
                    f"[PROJEKT] Aktives Projekt gewechselt auf '{chosen_name}' ({self.workspace_var.get()}) | Modell: {self.selected_model_var.get()}"
                )
                break

    def _on_project_tree_select(self, _event=None):
        sel = self.tree_projects.selection()
        if not sel:
            return
        idx = int(sel[0].replace("proj_", ""))
        if 0 <= idx < len(self.projects_list):
            proj = self.projects_list[idx]
            self.active_project_name_var.set(proj["name"])
            self.workspace_var.set(proj["path"])
            if proj.get("preferred_model"):
                self.selected_model_var.set(proj["preferred_model"])
            p_path = Path(proj["path"])
            self._ensure_project_env_file(p_path)
            if hasattr(self, "lbl_git_status"):
                self.lbl_git_status.configure(text=inspect_or_init_git(p_path, init_if_missing=False))
            self._refresh_project_files_tree()

    def set_selected_project_active(self) -> bool:
        sel = self.tree_projects.selection()
        if not sel:
            messagebox.showinfo("Projektauswahl", "Bitte wähle oben links ein Projekt aus der Liste aus.")
            return False
        idx = int(sel[0].replace("proj_", ""))
        if 0 <= idx < len(self.projects_list):
            proj = self.projects_list[idx]
            proj["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            self.active_project_name_var.set(proj["name"])
            self.workspace_var.set(proj["path"])
            if proj.get("preferred_model"):
                self.selected_model_var.set(proj["preferred_model"])
            self._ensure_project_env_file(Path(proj["path"]))
            self.save_projects()
            self.save_config()
            self._refresh_projects_ui()
            self.log_message(f"[PROJEKT AKTIVIERT] '{proj['name']}' -> {proj['path']}")
            return True
        return False

    def activate_and_launch_selected_project(self):
        if self.set_selected_project_active():
            self.launch_claude_code()

    def _browse_new_project_parent(self):
        folder = filedialog.askdirectory(initialdir=self.new_proj_path_var.get())
        if folder:
            self.new_proj_path_var.set(folder)

    def create_new_project(self, launch_immediately: bool = False):
        raw_name = self.new_proj_name_var.get().strip()
        if not raw_name:
            messagebox.showwarning("Projektname fehlt", "Bitte gib einen Projektnamen ein (z.B. AppsFlyer_S2S_Pipeline).")
            return

        safe_folder = "".join(c if c.isalnum() or c in ("-", "_", ".") else "_" for c in raw_name)
        parent_dir = Path(self.new_proj_path_var.get().strip())
        target_dir = parent_dir / safe_folder
        target_dir.mkdir(parents=True, exist_ok=True)

        mmp_choice = self.new_proj_mmp_var.get()
        pref_model = self.new_proj_model_var.get().strip() or self.selected_model_var.get().strip()

        new_entry = {
            "name": raw_name,
            "path": str(target_dir),
            "mmp_stack": mmp_choice,
            "preferred_model": pref_model,
            "last_used": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.projects_list = [p for p in self.projects_list if Path(p.get("path", "")) != target_dir]
        self.projects_list.insert(0, new_entry)
        self.save_projects()

        self.active_project_name_var.set(raw_name)
        self.workspace_var.set(str(target_dir))
        self.selected_model_var.set(pref_model)
        self._ensure_project_env_file(target_dir)
        self.save_config()

        if self.new_proj_template_var.get():
            content = self.agents_editor.get("1.0", "end").strip() + "\n"
            (target_dir / "AGENTS.md").write_text(content, encoding="utf-8")
            (target_dir / "CLAUDE.md").write_text(content, encoding="utf-8")
            inspect_or_init_git(target_dir, init_if_missing=True)
            if "AppsFlyer" in mmp_choice and "All-in-One" not in mmp_choice:
                self.generate_mmp_template("appsflyer")
            elif "Singular" in mmp_choice:
                self.generate_mmp_template("singular")
            elif "Adjust" in mmp_choice:
                self.generate_mmp_template("adjust")
            elif "All-in-One" in mmp_choice:
                self.generate_mmp_template("all")

        self._refresh_projects_ui()
        self.new_proj_name_var.set("")
        self.log_message(f"[NEUES PROJEKT] '{raw_name}' erstellt unter: {target_dir} (Modell: {pref_model})")

        if launch_immediately:
            self.launch_claude_code()
        else:
            messagebox.showinfo("Projekt erstellt", f"Projekt '{raw_name}' wurde unter\n{target_dir}\ninkl. .env & Git angelegt und aktiviert!")

    def import_existing_folder_as_project(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_var.get())
        if not folder:
            return
        p_path = Path(folder)
        proj_name = p_path.name or str(p_path)
        new_entry = {
            "name": proj_name,
            "path": str(p_path),
            "mmp_stack": "Importierter Workspace",
            "preferred_model": self.selected_model_var.get(),
            "last_used": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        self.projects_list = [p for p in self.projects_list if Path(p.get("path", "")) != p_path]
        self.projects_list.insert(0, new_entry)
        self._ensure_project_env_file(p_path)
        self.save_projects()

        self.active_project_name_var.set(proj_name)
        self.workspace_var.set(str(p_path))
        self.save_config()
        self._refresh_projects_ui()
        self.log_message(f"[ORDNER IMPORTIERT] '{proj_name}' ({p_path}) zur Projektverwaltung hinzugefügt.")

    def remove_selected_project(self):
        sel = self.tree_projects.selection()
        if not sel:
            messagebox.showinfo("Auswahl", "Bitte wähle ein Projekt aus der Liste aus.")
            return
        idx = int(sel[0].replace("proj_", ""))
        if 0 <= idx < len(self.projects_list):
            proj = self.projects_list[idx]
            if messagebox.askyesno(
                "Aus Liste entfernen",
                f"Soll '{proj['name']}' aus der Projektliste entfernt werden?\n(Die Dateien auf der Festplatte bleiben selbstverständlich erhalten.)",
            ):
                self.projects_list.pop(idx)
                self.save_projects()
                self._refresh_projects_ui()
                self.log_message(f"[PROJEKT] '{proj['name']}' aus der Liste entfernt.")

    def open_workspace_in_explorer(self):
        ws = Path(self.workspace_var.get().strip())
        ws.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(ws))
        else:
            subprocess.Popen(["xdg-open", str(ws)])

    # -----------------------------------------------------------------------
    # PAGE 3: MODELL-VERWALTUNG (+ VRAM MONITOR & UNLOAD + 32K BUILDER)
    # -----------------------------------------------------------------------
    def _build_page_models(self):
        page = tk.Frame(self.pages_container, bg=COLORS["bg_main"])
        self.pages["models"] = page
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)
        page.grid_rowconfigure(1, weight=1)

        hdr = tk.Frame(page, bg=COLORS["bg_main"])
        hdr.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 12))

        tk.Label(
            hdr,
            text="Lokale KI-Modelle — Download, VRAM-Steuerung & 32k-MMP Builder",
            font=("Segoe UI Bold", 16),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_main"],
        ).pack(side="left")

        tk.Button(
            hdr,
            text="🧹 VRAM leeren (Geladene Modelle entladen)",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["accent_amber"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.unload_all_vram_models,
        ).pack(side="right", padx=(8, 0))

        tk.Button(
            hdr,
            text="🔄 Modelle & VRAM prüfen",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["text_primary"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=self.refresh_installed_models,
        ).pack(side="right")

        left_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        left_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        left_card.grid_rowconfigure(1, weight=1)
        left_card.grid_columnconfigure(0, weight=1)

        tk.Label(
            left_card,
            text="KURATIERTER KATALOG (UNCENSORED & OPEN-WEIGHT CODING MODELLE)",
            font=("Segoe UI Bold", 9),
            fg=COLORS["accent_hover"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

        cols = ("tag", "category", "vram")
        self.tree_catalog = ttk.Treeview(left_card, columns=cols, show="headings", selectmode="browse")
        self.tree_catalog.heading("tag", text="Modell-Tag")
        self.tree_catalog.heading("category", text="Typ / Fokus")
        self.tree_catalog.heading("vram", text="VRAM")
        self.tree_catalog.column("tag", width=190, anchor="w")
        self.tree_catalog.column("category", width=170, anchor="w")
        self.tree_catalog.column("vram", width=70, anchor="center")
        self.tree_catalog.grid(row=1, column=0, sticky="nsew")

        for item in CURATED_MODELS:
            self.tree_catalog.insert("", "end", iid=item["tag"], values=(item["tag"], item["category"], item["vram"]))

        self.lbl_catalog_desc = tk.Label(
            left_card,
            text="Wähle ein Modell aus der Liste, um Details zu sehen oder es herunterzuladen.",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            wraplength=460,
            justify="left",
            anchor="w",
        )
        self.lbl_catalog_desc.grid(row=2, column=0, sticky="ew", pady=(8, 8))
        self.tree_catalog.bind("<<TreeviewSelect>>", self._on_catalog_select)

        cat_actions = tk.Frame(left_card, bg=COLORS["bg_card"])
        cat_actions.grid(row=3, column=0, sticky="ew")

        tk.Button(
            cat_actions,
            text="⬇️ Ausgewähltes Modell herunterladen (Pull)",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.pull_selected_catalog_model,
        ).pack(side="left")

        tk.Button(
            cat_actions,
            text="✅ Direkt aktivieren",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.activate_selected_catalog_model,
        ).pack(side="right")

        custom_frame = tk.Frame(left_card, bg=COLORS["bg_card"], pady=8)
        custom_frame.grid(row=4, column=0, sticky="ew")
        custom_frame.grid_columnconfigure(0, weight=1)

        tk.Entry(
            custom_frame,
            textvariable=self.custom_model_var,
            font=("Consolas", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            insertbackground="#FFFFFF",
            bd=0,
            highlightbackground=COLORS["border"],
            highlightthickness=1,
        ).grid(row=0, column=0, sticky="ew", ipady=5, padx=(0, 8))

        tk.Button(
            custom_frame,
            text="⬇️ Custom Tag Pull",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=10,
            pady=6,
            cursor="hand2",
            command=self.pull_custom_model,
        ).grid(row=0, column=1)

        right_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=16,
            pady=14,
        )
        right_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        right_card.grid_rowconfigure(1, weight=1)
        right_card.grid_columnconfigure(0, weight=1)

        tk.Label(
            right_card,
            text="LOKAL INSTALLIERTE OLLAMA MODELLE & 32K-MMP BUILDER",
            font=("Segoe UI Bold", 9),
            fg=COLORS["accent_emerald"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

        inst_cols = ("name", "size", "modified")
        self.tree_installed = ttk.Treeview(right_card, columns=inst_cols, show="headings", selectmode="browse")
        self.tree_installed.heading("name", text="Installiertes Modell")
        self.tree_installed.heading("size", text="Größe")
        self.tree_installed.heading("modified", text="Status / Geändert")
        self.tree_installed.column("name", width=210, anchor="w")
        self.tree_installed.column("size", width=90, anchor="center")
        self.tree_installed.column("modified", width=130, anchor="w")
        self.tree_installed.grid(row=1, column=0, sticky="nsew")

        inst_actions = tk.Frame(right_card, bg=COLORS["bg_card"])
        inst_actions.grid(row=2, column=0, sticky="ew", pady=(10, 4))

        tk.Button(
            inst_actions,
            text="⭐ Als aktives Modell setzen",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.activate_selected_installed_model,
        ).pack(side="left")

        tk.Button(
            inst_actions,
            text="🧪 Modell-Ping",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.test_active_model,
        ).pack(side="left", padx=6)

        tk.Button(
            inst_actions,
            text="🗑️ Löschen",
            font=("Segoe UI", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_rose"],
            bd=0,
            padx=10,
            pady=7,
            cursor="hand2",
            command=self.delete_selected_installed_model,
        ).pack(side="right")

        btn_32k = tk.Button(
            right_card,
            text="⚡ Ausgewähltes Modell als '32k-Senior-MMP' Spezialmodell klonen (num_ctx 32768 + MMP System-Prompt)",
            font=("Segoe UI Bold", 9),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            activebackground=COLORS["accent_hover"],
            bd=0,
            padx=12,
            pady=8,
            cursor="hand2",
            command=self.create_32k_mmp_model_from_selected,
        )
        btn_32k.grid(row=3, column=0, sticky="ew", pady=(6, 0))

    def unload_all_vram_models(self):
        ollama_bin = self._resolve_ollama_bin()
        if not ollama_bin:
            return
        self.start_progress("Entlade Modelle aus GPU VRAM (ollama stop)")

        def worker():
            try:
                info = query_vram_and_ollama_ps(ollama_bin)
                active = info.get("active_models", [])
                if not active:
                    # Also try stopping the currently selected model just in case
                    subprocess.run(
                        [ollama_bin, "stop", self.selected_model_var.get().strip()],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                    self.log_message("[VRAM] Keine laufenden Modelle in 'ollama ps' gefunden — VRAM ist frei.")
                else:
                    for m in active:
                        subprocess.run(
                            [ollama_bin, "stop", m],
                            capture_output=True,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                        )
                        self.log_message(f"[VRAM] Modell '{m}' aus dem Grafikspeicher entladen.")
            except Exception as e:
                self.log_message(f"[WARN] Fehler beim Entladen des VRAMs: {e}")
            finally:
                self.stop_progress()
                self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    def _on_catalog_select(self, _event=None):
        sel = self.tree_catalog.selection()
        if not sel:
            return
        tag = sel[0]
        for item in CURATED_MODELS:
            if item["tag"] == tag:
                self.lbl_catalog_desc.configure(text=f"{item['name']} — {item['desc']}")
                self.custom_model_var.set(tag)
                break

    def create_32k_mmp_model_from_selected(self):
        sel = self.tree_installed.selection()
        base_model = sel[0] if sel else self.selected_model_var.get().strip()
        self._build_32k_mmp_model(base_model)

    def create_32k_mmp_model_from_active(self):
        self._build_32k_mmp_model(self.selected_model_var.get().strip())

    def _build_32k_mmp_model(self, base_model: str):
        ollama_bin = self._resolve_ollama_bin()
        if not ollama_bin:
            messagebox.showwarning("Ollama fehlt", "Ollama wurde noch nicht gefunden. Bitte zuerst im Setup-Menü installieren.")
            return

        clean_base = base_model.split(":")[0].replace("-mmp32k", "")
        derived_tag = f"{clean_base}-mmp32k:latest"
        modelfile_path = BASE_DIR / f"Modelfile.{clean_base}.mmp32k"

        modelfile_content = f'''FROM {base_model}
PARAMETER num_ctx 32768
PARAMETER temperature 0.15
PARAMETER top_p 0.9

SYSTEM """You are a Principal Mobile Measurement Partner (MMP) & Senior Systems Architect running locally inside Claude Code.
Your primary specialization covers AppsFlyer (S2S Events API v2/v3, OneLink, UDL, SKAN 4.0, Pull/Push API), Singular (S2S /api/v1/launch & /api/v1/evt, Singular Links, Cohort ETL), and Adjust (S2S Event & Session API, Bearer auth, double-encoded callback_params/partner_params, Real-Time Webhook Callbacks).
Always provide complete, production-ready, end-to-end code without placeholders. After each completed step, propose targeted optimizations and wait for explicit user approval before implementing them."""
'''
        modelfile_path.write_text(modelfile_content, encoding="utf-8")
        self.start_progress(f"Baue 32k-Senior-MMP Modell: {derived_tag}")
        self.log_message(f"[32K BUILDER] Erzeuge '{derived_tag}' aus Basis '{base_model}' (num_ctx=32768)...")

        def worker():
            try:
                proc = subprocess.Popen(
                    [ollama_bin, "create", derived_tag, "-f", str(modelfile_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log_message(f"[ollama create] {line.strip()}")
                proc.wait()
                if proc.returncode == 0:
                    self.selected_model_var.set(derived_tag)
                    self.save_config()
                    self.log_message(f"[SUCCESS] 32k-Senior-MMP Modell '{derived_tag}' erstellt und als aktiv gesetzt!")
                else:
                    self.log_message(f"[ERROR] 'ollama create' beendet mit Code {proc.returncode}.")
            except Exception as e:
                self.log_message(f"[ERROR] Fehler beim 32k-Modelfile-Build: {e}")
            finally:
                self.stop_progress()
                self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    # -----------------------------------------------------------------------
    # PAGE 4: SETUP-MENÜ (ONE-CLICK SETUP, OLLAMA INSTALLER & KOMPONENTEN)
    # -----------------------------------------------------------------------
    def _build_page_setup(self):
        page = tk.Frame(self.pages_container, bg=COLORS["bg_main"])
        self.pages["setup"] = page

        banner = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["accent"],
            highlightthickness=1,
            padx=20,
            pady=14,
        )
        banner.pack(fill="x", pady=(0, 14))

        left_b = tk.Frame(banner, bg=COLORS["bg_card"])
        left_b.pack(side="left", fill="both", expand=True)

        tk.Label(
            left_b,
            text="⚡ ONE-CLICK VOLL-SETUP (OLLAMA SETUP + CLAUDE CODE + BRIDGE + MODELL + AGENTS.MD)",
            font=("Segoe UI Black", 11),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x")

        tk.Label(
            left_b,
            text="Prüft und installiert bei Bedarf Ollama komplett automatisch, startet den lokalen Ollama-Server, "
                 "installiert Claude Code CLI, richtet die lokale Anthropic-Bridge ein und synchronisiert die MMP AGENTS.md.",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            anchor="w",
            wraplength=760,
            justify="left",
        ).pack(fill="x", pady=(4, 0))

        tk.Button(
            banner,
            text="🚀 ONE-CLICK SETUP STARTEN",
            font=("Segoe UI Black", 10),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            activebackground=COLORS["accent_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=20,
            pady=12,
            cursor="hand2",
            command=self.run_one_click_setup,
        ).pack(side="right", padx=(16, 0))

        ollama_panel = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["accent_cyan"],
            highlightthickness=1,
            padx=20,
            pady=14,
        )
        ollama_panel.pack(fill="x", pady=(0, 14))

        ol_top = tk.Frame(ollama_panel, bg=COLORS["bg_card"])
        ol_top.pack(fill="x", pady=(0, 6))

        tk.Label(
            ol_top,
            text="🦙 OLLAMA KOMPLETT-SETUP, INSTALLER & ENGINE-KONFIGURATION",
            font=("Segoe UI Bold", 10),
            fg=COLORS["accent_cyan"],
            bg=COLORS["bg_card"],
        ).pack(side="left")

        self.lbl_ollama_setup_detail = tk.Label(
            ol_top,
            text="Prüfe Ollama Installation...",
            font=("Consolas", 9, "bold"),
            fg=COLORS["accent_amber"],
            bg=COLORS["bg_card"],
        )
        self.lbl_ollama_setup_detail.pack(side="right")

        tk.Label(
            ollama_panel,
            text="Installiert Ollama bei Bedarf vollautomatisch (via Winget oder offiziellem OllamaSetup.exe Downloader), "
                 "verwaltet den Hintergrund-Dienst und optimiert Flash-Attention sowie das Kontextfenster für Claude Code.",
            font=("Segoe UI", 9),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_card"],
            anchor="w",
        ).pack(fill="x", pady=(0, 10))

        ol_btn_row = tk.Frame(ollama_panel, bg=COLORS["bg_card"])
        ol_btn_row.pack(fill="x")

        tk.Button(
            ol_btn_row,
            text="⬇️ Ollama herunterladen & installieren (Auto-Installer)",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent"],
            fg="#FFFFFF",
            activebackground=COLORS["accent_hover"],
            activeforeground="#FFFFFF",
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.install_ollama_full,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            ol_btn_row,
            text="▶️ Ollama Server starten / Neustarten",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_emerald"],
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.setup_step_ollama,
        ).pack(side="left", padx=(0, 10))

        tk.Button(
            ol_btn_row,
            text="⚡ Performance-Tuning aktivieren (Flash-Attention + 32k Kontext)",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_input"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=14,
            pady=8,
            cursor="hand2",
            command=self.configure_ollama_performance,
        ).pack(side="left")

        tk.Label(
            page,
            text="WEITERE EINZELKOMPONENTEN SEPARAT INSTALLIEREN & KONFIGURIEREN",
            font=("Segoe UI Bold", 10),
            fg=COLORS["text_secondary"],
            bg=COLORS["bg_main"],
            anchor="w",
        ).pack(fill="x", pady=(0, 8))

        comp_grid = tk.Frame(page, bg=COLORS["bg_main"])
        comp_grid.pack(fill="both", expand=True)
        comp_grid.grid_columnconfigure(0, weight=1)
        comp_grid.grid_columnconfigure(1, weight=1)

        self.comp_cards = {}
        components = [
            (
                "ollama",
                0,
                0,
                "1. Ollama Local Engine & API Health",
                "Prüft den lokalen Port 11434 sowie die Anthropic Messages API Kompatibilität.",
                "API prüfen & Server starten",
                self.setup_step_ollama,
            ),
            (
                "claude_cli",
                0,
                1,
                "2. Claude Code CLI (@anthropic-ai/claude-code)",
                "Installiert oder aktualisiert das offizielle Claude Code CLI global über NPM.",
                "Claude CLI installieren/updaten",
                self.setup_step_claude_cli,
            ),
            (
                "bridge",
                1,
                0,
                "3. Local Anthropic-Ollama Bridge",
                "Konfiguriert ANTHROPIC_BASE_URL=http://localhost:11434 und lokale Claude-Settings.",
                "Bridge-Konfiguration schreiben",
                self.setup_step_bridge,
            ),
            (
                "mmp_agents",
                1,
                1,
                "4. Senior MMP AGENTS.md & Boilerplates",
                "Erstellt AGENTS.md, CLAUDE.md sowie die AppsFlyer, Singular & Adjust Referenz-Skripte.",
                "AGENTS.md & MMP-Suite ausrollen",
                self.setup_step_agents_and_mmp,
            ),
        ]

        for key, r, c, title, desc, btn_txt, cmd in components:
            card = tk.Frame(
                comp_grid,
                bg=COLORS["bg_card"],
                highlightbackground=COLORS["border"],
                highlightthickness=1,
                padx=18,
                pady=12,
            )
            card.grid(row=r, column=c, sticky="nsew", padx=(0 if c == 0 else 8, 0), pady=(0, 10))

            top_row = tk.Frame(card, bg=COLORS["bg_card"])
            top_row.pack(fill="x")

            tk.Label(top_row, text=title, font=("Segoe UI Bold", 10), fg=COLORS["text_primary"], bg=COLORS["bg_card"]).pack(side="left")

            lbl_status = tk.Label(
                top_row, text="● BEREIT", font=("Segoe UI Bold", 8), fg=COLORS["accent_amber"], bg=COLORS["bg_card"]
            )
            lbl_status.pack(side="right")

            tk.Label(
                card,
                text=desc,
                font=("Segoe UI", 9),
                fg=COLORS["text_secondary"],
                bg=COLORS["bg_card"],
                wraplength=420,
                justify="left",
                anchor="w",
            ).pack(fill="x", pady=(6, 10))

            tk.Button(
                card,
                text=f"⚙️  {btn_txt}",
                font=("Segoe UI Semibold", 9),
                bg=COLORS["bg_input"],
                fg=COLORS["accent_cyan"],
                activebackground=COLORS["accent"],
                activeforeground="#FFFFFF",
                bd=0,
                padx=14,
                pady=7,
                cursor="hand2",
                command=cmd,
            ).pack(anchor="w")

            self.comp_cards[key] = lbl_status

    # -----------------------------------------------------------------------
    # PAGE 5: AGENTS.MD & MMP STUDIO EDITOR
    # -----------------------------------------------------------------------
    def _build_page_agents(self):
        page = tk.Frame(self.pages_container, bg=COLORS["bg_main"])
        self.pages["agents"] = page
        page.grid_rowconfigure(1, weight=1)
        page.grid_columnconfigure(0, weight=1)

        hdr = tk.Frame(page, bg=COLORS["bg_main"])
        hdr.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        tk.Label(
            hdr,
            text="AGENTS.md & CLAUDE.md — Local Model Rules & Senior MMP Direktiven",
            font=("Segoe UI Bold", 16),
            fg=COLORS["text_primary"],
            bg=COLORS["bg_main"],
        ).pack(side="left")

        btn_bar = tk.Frame(hdr, bg=COLORS["bg_main"])
        btn_bar.pack(side="right")

        tk.Button(
            btn_bar,
            text="📡 Zum MMP Live-S2S-Tester →",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["bg_card"],
            fg=COLORS["accent_cyan"],
            bd=0,
            padx=12,
            pady=6,
            cursor="hand2",
            command=lambda: self.show_page("mmp_tester"),
        ).pack(side="left", padx=(0, 8))

        tk.Button(
            btn_bar,
            text="💾 Speichern & mit aktivem Projekt synchronisieren",
            font=("Segoe UI Semibold", 9),
            bg=COLORS["accent_emerald"],
            fg="#052E16",
            bd=0,
            padx=14,
            pady=6,
            cursor="hand2",
            command=self.save_agents_md,
        ).pack(side="left")

        editor_card = tk.Frame(
            page,
            bg=COLORS["bg_card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1,
            padx=12,
            pady=12,
        )
        editor_card.grid(row=1, column=0, sticky="nsew")
        editor_card.grid_rowconfigure(0, weight=1)
        editor_card.grid_columnconfigure(0, weight=1)

        self.agents_editor = tk.Text(
            editor_card,
            bg=COLORS["bg_input"],
            fg=COLORS["text_primary"],
            font=("Consolas", 10),
            bd=0,
            padx=14,
            pady=12,
            insertbackground="#FFFFFF",
            wrap="word",
        )
        self.agents_editor.grid(row=0, column=0, sticky="nsew")

        if AGENTS_FILE.exists():
            self.agents_editor.insert("1.0", AGENTS_FILE.read_text(encoding="utf-8"))
        else:
            self.agents_editor.insert("1.0", DEFAULT_AGENTS_MD)

    # -----------------------------------------------------------------------
    # SYSTEM CHECKS, VRAM TELEMETRY & OLLAMA API HELPERS
    # -----------------------------------------------------------------------
    def log_message(self, msg: str):
        ts = datetime.now().strftime("%H:%M:%S")
        line = f"[{ts}] {msg}\n"
        self.after(0, self._append_log, line)

    def _append_log(self, line: str):
        self.log_text.insert("end", line)
        self.log_text.see("end")

    def clear_log(self):
        self.log_text.delete("1.0", "end")

    def refresh_all_status(self):
        threading.Thread(target=self._refresh_status_worker, daemon=True).start()

    def _refresh_status_worker(self):
        ollama_bin = self._resolve_ollama_bin()
        ollama_installed = ollama_bin is not None
        ollama_ver = "Nicht installiert"
        if ollama_installed:
            try:
                res = subprocess.run(
                    [ollama_bin, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=4,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                ollama_ver = res.stdout.strip() or "Installiert"
            except Exception:
                ollama_ver = "Installiert"

        ollama_running = False
        models_list = []
        try:
            req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags", method="GET")
            with urllib.request.urlopen(req, timeout=2.5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                ollama_running = True
                for m in data.get("models", []):
                    name = m.get("name", "")
                    size_gb = round(m.get("size", 0) / (1024 ** 3), 2)
                    mod = m.get("modified_at", "")[:10]
                    models_list.append((name, f"{size_gb} GB", mod))
        except Exception:
            ollama_running = False

        claude_path = shutil.which("claude") or shutil.which("claude.cmd")
        claude_ok = claude_path is not None
        node_ok = shutil.which("node") is not None

        self.vram_info = query_vram_and_ollama_ps(ollama_bin)
        self.status_ollama_installed = ollama_installed
        self.status_ollama_running = ollama_running
        self.status_ollama_version = ollama_ver
        self.status_claude = claude_ok
        self.status_node = node_ok
        self.installed_models = models_list

        self.after(0, self._update_status_ui)

    def _update_status_ui(self):
        if self.status_ollama_running:
            self.lbl_side_ollama.configure(text="● Ollama API: ONLINE (11434)", fg=COLORS["accent_emerald"])
            self.card_kpi_ollama["val"].configure(text="ONLINE // BEREIT", fg=COLORS["accent_emerald"])
            self.lbl_ollama_setup_detail.configure(
                text=f"● INSTALLIERT & ONLINE ({self.status_ollama_version})", fg=COLORS["accent_emerald"]
            )
            if "ollama" in self.comp_cards:
                self.comp_cards["ollama"].configure(text="● AKTIV", fg=COLORS["accent_emerald"])
        elif self.status_ollama_installed:
            self.lbl_side_ollama.configure(text="● Ollama: BEREIT (Server gestoppt)", fg=COLORS["accent_amber"])
            self.card_kpi_ollama["val"].configure(text="SERVER GESTOPPT", fg=COLORS["accent_amber"])
            self.lbl_ollama_setup_detail.configure(
                text=f"● INSTALLIERT ({self.status_ollama_version}) - Server inaktiv", fg=COLORS["accent_amber"]
            )
            if "ollama" in self.comp_cards:
                self.comp_cards["ollama"].configure(text="● GESTOPPT", fg=COLORS["accent_amber"])
        else:
            self.lbl_side_ollama.configure(text="● Ollama: NICHT INSTALLIERT", fg=COLORS["accent_rose"])
            self.card_kpi_ollama["val"].configure(text="FEHLT (Setup nutzen)", fg=COLORS["accent_rose"])
            self.lbl_ollama_setup_detail.configure(
                text="● NICHT INSTALLIERT — Klicke auf 'Ollama herunterladen & installieren'", fg=COLORS["accent_rose"]
            )
            if "ollama" in self.comp_cards:
                self.comp_cards["ollama"].configure(text="● FEHLT", fg=COLORS["accent_rose"])

        if self.status_claude:
            self.lbl_side_claude.configure(text="● Claude CLI: INSTALLIERT", fg=COLORS["accent_emerald"])
            if "claude_cli" in self.comp_cards:
                self.comp_cards["claude_cli"].configure(text="● INSTALLIERT", fg=COLORS["accent_emerald"])
        else:
            self.lbl_side_claude.configure(text="● Claude CLI: FEHLT", fg=COLORS["accent_amber"])
            if "claude_cli" in self.comp_cards:
                self.comp_cards["claude_cli"].configure(text="● FEHLT", fg=COLORS["accent_amber"])

        # Update VRAM & GPU Telemetry (Optimierung 2)
        used_mb = self.vram_info.get("vram_used_mb", 0)
        tot_mb = self.vram_info.get("vram_total_mb", 0)
        act_m = self.vram_info.get("active_models", [])
        if tot_mb > 0:
            vram_txt = f"VRAM: {round(used_mb/1024, 1)} / {round(tot_mb/1024, 1)} GB"
            self.lbl_side_vram.configure(text=f"● {vram_txt}", fg=COLORS["accent_emerald"])
            self.card_kpi_claude["val"].configure(text=vram_txt, fg=COLORS["accent_emerald"])
            self.card_kpi_claude["sub"].configure(
                text=f"Aktiv im VRAM: {', '.join(act_m) if act_m else 'Kein Modell geladen'}"
            )
        else:
            self.lbl_side_vram.configure(text="● VRAM: Frei / Shared RAM", fg=COLORS["text_secondary"])
            self.card_kpi_claude["val"].configure(
                text="INSTALLIERT" if self.status_claude else "FEHLT",
                fg=COLORS["accent_emerald"] if self.status_claude else COLORS["accent_amber"],
            )

        if AGENTS_FILE.exists() and "mmp_agents" in self.comp_cards:
            self.comp_cards["mmp_agents"].configure(text="● SYNCHRONISIERT", fg=COLORS["accent_emerald"])

        for item in self.tree_installed.get_children():
            self.tree_installed.delete(item)
        for name, size_str, mod in self.installed_models:
            status_tag = f"🔥 IM VRAM ({mod})" if name in act_m else mod
            self.tree_installed.insert("", "end", iid=name, values=(name, size_str, status_tag))

        installed_names = [m[0] for m in self.installed_models]
        curated_names = [m["tag"] for m in CURATED_MODELS]
        combined = []
        for n in installed_names + curated_names:
            if n not in combined:
                combined.append(n)
        self.combo_models["values"] = combined
        if hasattr(self, "combo_new_proj_model"):
            self.combo_new_proj_model["values"] = combined
        self.card_kpi_model["val"].configure(text=self.selected_model_var.get(), fg=COLORS["accent_cyan"])
        self._refresh_projects_ui()

    def refresh_installed_models(self):
        self.start_progress("Aktualisiere Modell-Liste & GPU VRAM Status")
        self.log_message("Lese lokal installierte Ollama-Modelle & VRAM-Status ein...")
        self.refresh_all_status()
        self.after(600, self.stop_progress)

    def on_model_changed(self):
        model = self.selected_model_var.get().strip()
        self.card_kpi_model["val"].configure(text=model)
        ws = Path(self.workspace_var.get().strip())
        for p in self.projects_list:
            if Path(p.get("path", "")) == ws:
                p["preferred_model"] = model
        self.save_projects()
        self.save_config()
        self._refresh_projects_ui()
        self.log_message(f"Aktives Modell gewechselt auf: {model}")

    def browse_workspace(self):
        folder = filedialog.askdirectory(initialdir=self.workspace_var.get())
        if folder:
            p_path = Path(folder)
            self.workspace_var.set(str(p_path))
            self.active_project_name_var.set(p_path.name or str(p_path))
            exists = any(Path(p.get("path", "")) == p_path for p in self.projects_list)
            if not exists:
                self.projects_list.insert(
                    0,
                    {
                        "name": p_path.name or str(p_path),
                        "path": str(p_path),
                        "mmp_stack": "Manueller Ordner",
                        "preferred_model": self.selected_model_var.get(),
                        "last_used": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    },
                )
                self.save_projects()
            self._ensure_project_env_file(p_path)
            self.save_config()
            self._refresh_projects_ui()
            self.log_message(f"Arbeitsverzeichnis gesetzt auf: {folder}")

    # -----------------------------------------------------------------------
    # OLLAMA FULL INSTALLER, SERVICE CONTROL & PERFORMANCE TUNING
    # -----------------------------------------------------------------------
    def install_ollama_full(self):
        self.start_progress("Ollama Auto-Installer & Update läuft")
        self.log_message("[OLLAMA SETUP] Starte vollautomatische Ollama Installation / Update...")

        def worker():
            try:
                winget_bin = shutil.which("winget")
                installed_via_winget = False

                if winget_bin:
                    self.log_message("[OLLAMA SETUP] Winget erkannt. Führe 'winget install -e --id Ollama.Ollama' aus...")
                    proc = subprocess.Popen(
                        [
                            winget_bin,
                            "install",
                            "-e",
                            "--id",
                            "Ollama.Ollama",
                            "--accept-package-agreements",
                            "--accept-source-agreements",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                    for line in proc.stdout:
                        clean = line.strip()
                        if clean and len(clean) > 2:
                            self.log_message(f"[winget] {clean}")
                    proc.wait()
                    if self._resolve_ollama_bin() is not None:
                        installed_via_winget = True
                        self.log_message("[OLLAMA SETUP] Ollama erfolgreich über Winget bereitgestellt!")

                if not installed_via_winget:
                    self.log_message(f"[OLLAMA SETUP] Lade offiziellen Installer von {OLLAMA_DOWNLOAD_URL} herunter...")
                    req = urllib.request.Request(OLLAMA_DOWNLOAD_URL, headers={"User-Agent": "Mozilla/5.0"})
                    with urllib.request.urlopen(req, timeout=60) as resp, open(OLLAMA_INSTALLER_PATH, "wb") as out_file:
                        total = int(resp.headers.get("Content-Length", 0))
                        downloaded = 0
                        chunk_size = 1024 * 512
                        last_pct = -1
                        while True:
                            chunk = resp.read(chunk_size)
                            if not chunk:
                                break
                            out_file.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                pct = int((downloaded / total) * 100)
                                if pct >= last_pct + 10:
                                    last_pct = pct
                                    mb_done = round(downloaded / (1024 * 1024), 1)
                                    mb_tot = round(total / (1024 * 1024), 1)
                                    self.log_message(f"[DOWNLOAD] OllamaSetup.exe: {pct}% ({mb_done} MB / {mb_tot} MB)")

                    self.log_message("[OLLAMA SETUP] Starte OllamaSetup.exe (/SILENT)...")
                    subprocess.run([str(OLLAMA_INSTALLER_PATH), "/SILENT"], check=False)
                    self.log_message("[OLLAMA SETUP] Ollama Installer abgeschlossen.")

                self._start_ollama_daemon()
            except Exception as e:
                self.log_message(f"[ERROR] Fehler beim Ollama Setup: {e}")
            finally:
                self.stop_progress()
                self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    def _start_ollama_daemon(self):
        ollama_bin = self._resolve_ollama_bin()
        if not ollama_bin:
            self.log_message("[WARN] Ollama Binary noch nicht gefunden. Bitte 'Ollama herunterladen & installieren' nutzen.")
            return False

        try:
            urllib.request.urlopen(f"{OLLAMA_HOST}/api/tags", timeout=2)
            self.log_message("[OK] Ollama Server läuft bereits auf http://localhost:11434.")
            return True
        except Exception:
            self.log_message("[SETUP] Starte 'ollama serve' mit optimierten Parametern im Hintergrund...")
            env = os.environ.copy()
            env["OLLAMA_FLASH_ATTENTION"] = "1"
            env["OLLAMA_CONTEXT_LENGTH"] = self.ollama_ctx_var.get().strip() or "32768"
            subprocess.Popen(
                [ollama_bin, "serve"],
                env=env,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
            )
            return True

    def configure_ollama_performance(self):
        self.start_progress("Optimiere Ollama Performance-Parameter (32k Kontext)")

        def worker():
            self.log_message("[TUNING] Setze Ollama Performance-Umgebungsvariablen (Flash-Attention & 32k Kontext)...")
            vars_to_set = {
                "OLLAMA_FLASH_ATTENTION": "1",
                "OLLAMA_KV_CACHE_TYPE": "q8_0",
                "OLLAMA_CONTEXT_LENGTH": "32768",
            }
            for k, v in vars_to_set.items():
                os.environ[k] = v
                if os.name == "nt":
                    subprocess.run(
                        ["setx", k, v],
                        capture_output=True,
                        creationflags=subprocess.CREATE_NO_WINDOW,
                    )
            self.log_message("[OK] Performance-Tuning aktiviert (OLLAMA_FLASH_ATTENTION=1, OLLAMA_KV_CACHE_TYPE=q8_0, OLLAMA_CONTEXT_LENGTH=32768).")
            self.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    # -----------------------------------------------------------------------
    # MODEL MANAGEMENT ACTIONS
    # -----------------------------------------------------------------------
    def pull_selected_catalog_model(self):
        sel = self.tree_catalog.selection()
        if not sel:
            messagebox.showinfo("Modell wählen", "Bitte wähle zuerst ein Modell aus dem Katalog links aus.")
            return
        self._start_model_pull(sel[0])

    def pull_custom_model(self):
        tag = self.custom_model_var.get().strip()
        if not tag:
            messagebox.showinfo("Modell-Tag fehlt", "Bitte gib einen gültigen Ollama Modell-Tag ein (z.B. dolphin-llama3:8b).")
            return
        self._start_model_pull(tag)

    def _start_model_pull(self, model_tag: str):
        ollama_bin = self._resolve_ollama_bin()
        if not ollama_bin:
            messagebox.showwarning("Ollama fehlt", "Ollama ist noch nicht installiert. Bitte zuerst im Setup-Menü installieren.")
            return

        self.start_progress(f"Lade Modell herunter: {model_tag}")
        self.log_message(f"[DOWNLOAD] Starte Download von '{model_tag}' via Ollama...")

        def worker():
            try:
                proc = subprocess.Popen(
                    [ollama_bin, "pull", model_tag],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                for line in proc.stdout:
                    clean = line.strip()
                    if clean:
                        self.log_message(f"[ollama pull {model_tag}] {clean}")
                proc.wait()
                if proc.returncode == 0:
                    self.log_message(f"[SUCCESS] Modell '{model_tag}' erfolgreich heruntergeladen und bereit!")
                    self.selected_model_var.set(model_tag)
                    self.save_config()
                else:
                    self.log_message(f"[ERROR] Download von '{model_tag}' beendet mit Code {proc.returncode}.")
            except Exception as e:
                self.log_message(f"[ERROR] Fehler beim Modell-Download: {e}")
            finally:
                self.stop_progress()
                self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    def activate_selected_catalog_model(self):
        sel = self.tree_catalog.selection()
        if not sel:
            messagebox.showinfo("Auswahl", "Bitte wähle ein Modell aus dem Katalog aus.")
            return
        self.selected_model_var.set(sel[0])
        self.on_model_changed()

    def activate_selected_installed_model(self):
        sel = self.tree_installed.selection()
        if not sel:
            messagebox.showinfo("Auswahl", "Bitte wähle rechts ein lokal installiertes Modell aus.")
            return
        self.selected_model_var.set(sel[0])
        self.on_model_changed()
        messagebox.showinfo("Modell aktiviert", f"'{sel[0]}' ist jetzt als aktives Modell für Claude Code gesetzt!")

    def delete_selected_installed_model(self):
        sel = self.tree_installed.selection()
        if not sel:
            messagebox.showinfo("Auswahl", "Bitte wähle rechts ein lokal installiertes Modell zum Löschen aus.")
            return
        model_tag = sel[0]
        if not messagebox.askyesno("Modell löschen", f"Soll das Modell '{model_tag}' wirklich lokal gelöscht werden?"):
            return

        ollama_bin = self._resolve_ollama_bin() or "ollama"
        self.start_progress(f"Lösche Modell: {model_tag}")

        def worker():
            try:
                subprocess.run(
                    [ollama_bin, "rm", model_tag],
                    check=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                self.log_message(f"[DELETE] Modell '{model_tag}' wurde gelöscht.")
                self.refresh_all_status()
            except Exception as e:
                self.log_message(f"[ERROR] Konnte '{model_tag}' nicht löschen: {e}")
            finally:
                self.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    def test_active_model(self):
        model = self.selected_model_var.get().strip()
        self.start_progress(f"Sende Test-Ping an Modell: {model}")
        self.log_message(f"[TEST] Sende kurzen Test-Request an lokales Modell '{model}'...")

        def worker():
            payload = json.dumps(
                {
                    "model": model,
                    "prompt": "Antworte in einem kurzen Satz auf Deutsch: Bestätige, dass du lokal als Senior MMP Coding Assistent für AppsFlyer, Singular und Adjust bereit bist.",
                    "stream": False,
                }
            ).encode("utf-8")
            try:
                req = urllib.request.Request(
                    f"{OLLAMA_HOST}/api/generate",
                    data=payload,
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    reply = data.get("response", "").strip()
                    self.log_message(f"[MODELL-ANTWORT ({model})]: {reply}")
            except Exception as e:
                self.log_message(f"[WARN] Modell-Test fehlgeschlagen: {e}")
            finally:
                self.stop_progress()
                self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    # -----------------------------------------------------------------------
    # SETUP STEPS (ONE-CLICK & INDIVIDUAL)
    # -----------------------------------------------------------------------
    def setup_step_ollama(self):
        self.start_progress("Prüfe & starte lokalen Ollama Server")

        def worker():
            self.log_message("[SETUP] Prüfe Ollama Installation & Server auf http://localhost:11434...")
            if not self._resolve_ollama_bin():
                self.log_message("[SETUP] Ollama nicht gefunden — starte automatische Ollama-Installation...")
                self.after(0, self.install_ollama_full)
                return
            self._start_ollama_daemon()
            self.stop_progress()
            self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    def setup_step_claude_cli(self):
        self.start_progress("Installiere / Aktualisiere @anthropic-ai/claude-code via NPM")

        def worker():
            self.log_message("[SETUP] Prüfe / Installiere @anthropic-ai/claude-code via NPM...")
            npm_cmd = shutil.which("npm.cmd") or shutil.which("npm")
            if not npm_cmd:
                self.log_message("[ERROR] NPM wurde nicht gefunden. Bitte Node.js installieren.")
                self.stop_progress()
                return
            try:
                proc = subprocess.Popen(
                    [npm_cmd, "install", "-g", "@anthropic-ai/claude-code"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )
                for line in proc.stdout:
                    if line.strip():
                        self.log_message(f"[npm] {line.strip()}")
                proc.wait()
                self.log_message("[OK] Claude Code CLI Setup abgeschlossen.")
                self.refresh_all_status()
            except Exception as e:
                self.log_message(f"[ERROR] Fehler bei Claude CLI Installation: {e}")
            finally:
                self.stop_progress()

        threading.Thread(target=worker, daemon=True).start()

    def setup_step_bridge(self):
        self.save_config()
        bridge_script = BASE_DIR / "claude_local_env.ps1"
        model = self.selected_model_var.get().strip()
        ps_content = (
            f"# Automatisch generiertes Bridge-Profil für Claude Code + Lokales Ollama Modell\n"
            f"$env:ANTHROPIC_BASE_URL = '{OLLAMA_HOST}'\n"
            f"$env:ANTHROPIC_AUTH_TOKEN = 'ollama'\n"
            f"$env:ANTHROPIC_API_KEY = ''\n"
            f"$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = '1'\n"
            f"Write-Host 'SHOXX Local Bridge aktiv -> Modell: {model}' -ForegroundColor Cyan\n"
        )
        bridge_script.write_text(ps_content, encoding="utf-8")
        if "bridge" in self.comp_cards:
            self.comp_cards["bridge"].configure(text="● KONFIGURIERT", fg=COLORS["accent_emerald"])
        self.log_message(f"[OK] Anthropic-Ollama Bridge-Profil gespeichert ({bridge_script.name}).")

    def setup_step_agents_and_mmp(self):
        self.save_agents_md()
        self.generate_mmp_template("all")
        if "mmp_agents" in self.comp_cards:
            self.comp_cards["mmp_agents"].configure(text="● SYNCHRONISIERT", fg=COLORS["accent_emerald"])

    def run_one_click_setup(self):
        self.start_progress("ONE-CLICK VOLL-SETUP LÄUFT")
        self.log_message("=================================================================")
        self.log_message("[ONE-CLICK SETUP] Starte vollständige Einrichtung (inkl. Ollama Setup)...")

        def worker():
            try:
                self.log_message("[1/5] Prüfe Ollama Installation & Server...")
                if not self._resolve_ollama_bin():
                    self.log_message("[1/5] Ollama noch nicht installiert — führe Winget/Installer Setup aus...")
                    winget_bin = shutil.which("winget")
                    if winget_bin:
                        subprocess.run(
                            [
                                winget_bin,
                                "install",
                                "-e",
                                "--id",
                                "Ollama.Ollama",
                                "--accept-package-agreements",
                                "--accept-source-agreements",
                            ],
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                        )
                self._start_ollama_daemon()

                self.log_message("[2/5] Aktiviere Ollama Performance-Tuning (Flash-Attention & 32k Kontext)...")
                self.configure_ollama_performance()

                self.log_message("[3/5] Konfiguriere Anthropic-to-Ollama Bridge...")
                self.after(0, self.setup_step_bridge)

                self.log_message("[4/5] Erzeuge AGENTS.md, CLAUDE.md und Senior MMP Templates (AppsFlyer, Singular, Adjust)...")
                self.after(0, self.setup_step_agents_and_mmp)

                target_model = self.selected_model_var.get().strip()
                ollama_bin = self._resolve_ollama_bin()
                self.log_message(f"[5/5] Stelle sicher, dass Modell '{target_model}' lokal verfügbar ist...")
                if ollama_bin:
                    proc = subprocess.Popen(
                        [ollama_bin, "pull", target_model],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                    )
                    for line in proc.stdout:
                        if line.strip():
                            self.log_message(f"[pull] {line.strip()}")
                    proc.wait()

                self.log_message("[SUCCESS] One-Click Setup komplett abgeschlossen! Du kannst Claude Code jetzt auf der Hauptseite starten.")
            except Exception as e:
                self.log_message(f"[ERROR] One-Click Setup Fehler: {e}")
            finally:
                self.stop_progress()
                self.refresh_all_status()

        threading.Thread(target=worker, daemon=True).start()

    # -----------------------------------------------------------------------
    # AGENTS.MD & SENIOR MMP TEMPLATES GENERATOR
    # -----------------------------------------------------------------------
    def save_agents_md(self):
        content = self.agents_editor.get("1.0", "end").strip() + "\n"
        AGENTS_FILE.write_text(content, encoding="utf-8")
        CLAUDE_MD_FILE.write_text(content, encoding="utf-8")

        ws = Path(self.workspace_var.get().strip())
        ws.mkdir(parents=True, exist_ok=True)
        if ws.resolve() != BASE_DIR.resolve():
            (ws / "AGENTS.md").write_text(content, encoding="utf-8")
            (ws / "CLAUDE.md").write_text(content, encoding="utf-8")

        self.log_message(f"[OK] AGENTS.md und CLAUDE.md gespeichert & im Projektordner '{ws}' synchronisiert.")

    def generate_mmp_template(self, provider: str):
        ws = Path(self.workspace_var.get().strip())
        self._ensure_project_env_file(ws)
        out_dir = ws / "mmp_senior_scripts"
        out_dir.mkdir(parents=True, exist_ok=True)

        created = []

        if provider in ("appsflyer", "all"):
            af_path = out_dir / "appsflyer_s2s_senior.py"
            af_path.write_text(
                '''#!/usr/bin/env python3
"""
Senior AppsFlyer S2S Events API v3 & OneLink Attribution Handler
Reads APPSFLYER_APP_ID & APPSFLYER_DEV_KEY automatically from project environment (.env).
"""
import os
import json
import time
import uuid
import logging
import urllib.request
import urllib.error
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AppsFlyerS2S")


class AppsFlyerS2SClient:
    BASE_URL = "https://api2.appsflyer.com/inappevent"

    def __init__(self, app_id: Optional[str] = None, dev_key: Optional[str] = None, timeout: int = 10):
        self.app_id = app_id or os.environ.get("APPSFLYER_APP_ID", "id123456789")
        self.dev_key = dev_key or os.environ.get("APPSFLYER_DEV_KEY", "YOUR_AF_DEV_KEY")
        self.timeout = timeout

    def send_inapp_event(
        self,
        appsflyer_id: str,
        event_name: str,
        event_value: Dict[str, Any],
        customer_user_id: Optional[str] = None,
        advertising_id: Optional[str] = None,
        ip: Optional[str] = None,
        event_currency: str = "EUR",
    ) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/{self.app_id}"
        payload: Dict[str, Any] = {
            "appsflyer_id": appsflyer_id,
            "eventName": event_name,
            "eventValue": json.dumps(event_value, separators=(",", ":")),
            "eventCurrency": event_currency,
            "eventTime": time.strftime("%Y-%m-%d %H:%M:%S.000", time.gmtime()),
        }
        if customer_user_id:
            payload["customer_user_id"] = customer_user_id
        if advertising_id:
            payload["advertising_id"] = advertising_id
        if ip:
            payload["ip"] = ip

        data = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "authentication": self.dev_key,
            "Accept": "application/json",
        }

        for attempt in range(1, 4):
            try:
                req = urllib.request.Request(url, data=data, headers=headers, method="POST")
                with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                    body = resp.read().decode("utf-8")
                    logger.info("AppsFlyer S2S Event '%s' delivered (HTTP %s): %s", event_name, resp.status, body)
                    return {"status": resp.status, "response": body}
            except urllib.error.HTTPError as e:
                err_body = e.read().decode("utf-8", errors="replace")
                logger.warning("Attempt %d HTTP %d: %s", attempt, e.code, err_body)
                if e.code in (429, 500, 502, 503, 504) and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
                return {"status": e.code, "error": err_body}
            except Exception as ex:
                logger.error("Attempt %d network error: %s", attempt, ex)
                if attempt < 3:
                    time.sleep(2 ** attempt)
                else:
                    raise
        return {"status": 500, "error": "Max retries exceeded"}


if __name__ == "__main__":
    client = AppsFlyerS2SClient()
    sample_id = f"{int(time.time() * 1000)}-{uuid.uuid4().int % (10**19)}"
    logger.info("AppsFlyer Client ready (App-ID: %s | Sample AF-ID: %s)", client.app_id, sample_id)
''',
                encoding="utf-8",
            )
            created.append(af_path.name)

        if provider in ("singular", "all"):
            sg_path = out_dir / "singular_s2s_senior.py"
            sg_path.write_text(
                '''#!/usr/bin/env python3
"""
Senior Singular S2S Session & Custom Event Attribution Client
Reads SINGULAR_API_KEY & SINGULAR_BUNDLE_ID automatically from project environment (.env).
"""
import os
import json
import urllib.parse
import urllib.request
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SingularS2S")


class SingularS2SClient:
    LAUNCH_URL = "https://sdk-api-v1.singular.net/api/v1/launch"
    EVENT_URL = "https://sdk-api-v1.singular.net/api/v1/evt"

    def __init__(self, api_key: Optional[str] = None, bundle_id: Optional[str] = None, platform: str = "Android"):
        self.api_key = api_key or os.environ.get("SINGULAR_API_KEY", "YOUR_SINGULAR_KEY")
        self.bundle_id = bundle_id or os.environ.get("SINGULAR_BUNDLE_ID", "com.shoxx.app")
        self.platform = platform

    def track_event(
        self,
        event_name: str,
        device_ids: Dict[str, str],
        ip: str,
        revenue: Optional[float] = None,
        currency: str = "EUR",
        extra_attributes: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        params: Dict[str, str] = {
            "a": self.api_key,
            "i": self.bundle_id,
            "p": self.platform,
            "n": event_name,
            "ip": ip,
            **device_ids,
        }
        if revenue is not None:
            params["is_revenue_event"] = "true"
            params["amt"] = f"{revenue:.2f}"
            params["cur"] = currency
        if extra_attributes:
            params["e"] = json.dumps(extra_attributes, separators=(",", ":"))

        query = urllib.parse.urlencode(params)
        url = f"{self.EVENT_URL}?{query}"
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            logger.info("Singular S2S response: %s", data)
            return data


if __name__ == "__main__":
    client = SingularS2SClient()
    logger.info("Singular S2S Senior Client ready (Bundle-ID: %s)", client.bundle_id)
''',
                encoding="utf-8",
            )
            created.append(sg_path.name)

        if provider in ("adjust", "all"):
            adj_path = out_dir / "adjust_s2s_senior.py"
            adj_path.write_text(
                '''#!/usr/bin/env python3
"""
Senior Adjust S2S Event & Session Pipeline
Reads ADJUST_APP_TOKEN, ADJUST_BEARER_TOKEN & ADJUST_ENVIRONMENT from project environment (.env).
"""
import os
import json
import time
import logging
import urllib.parse
import urllib.request
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AdjustS2S")


class AdjustS2SClient:
    EVENT_ENDPOINT = "https://s2s.adjust.com/event"
    SESSION_ENDPOINT = "https://s2s.adjust.com/session"

    def __init__(
        self,
        app_token: Optional[str] = None,
        bearer_token: Optional[str] = None,
        environment: Optional[str] = None,
    ):
        self.app_token = app_token or os.environ.get("ADJUST_APP_TOKEN", "YOUR_APP_TOKEN")
        self.bearer_token = bearer_token or os.environ.get("ADJUST_BEARER_TOKEN", "")
        self.environment = environment or os.environ.get("ADJUST_ENVIRONMENT", "production")

    def send_event(
        self,
        event_token: str,
        device_identifiers: Dict[str, str],
        callback_params: Optional[Dict[str, str]] = None,
        partner_params: Optional[Dict[str, str]] = None,
        revenue: Optional[float] = None,
        currency: str = "EUR",
    ) -> Dict[str, Any]:
        payload: Dict[str, str] = {
            "s2s": "1",
            "app_token": self.app_token,
            "event_token": event_token,
            "environment": self.environment,
            "created_at_unix": str(int(time.time())),
            **device_identifiers,
        }
        if revenue is not None:
            payload["revenue"] = f"{revenue:.2f}"
            payload["currency"] = currency
        if callback_params:
            payload["callback_params"] = json.dumps(callback_params, separators=(",", ":"))
        if partner_params:
            payload["partner_params"] = json.dumps(partner_params, separators=(",", ":"))

        encoded_body = urllib.parse.urlencode(payload).encode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"

        req = urllib.request.Request(self.EVENT_ENDPOINT, data=encoded_body, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            logger.info("Adjust S2S HTTP %d: %s", resp.status, body)
            return {"status": resp.status, "body": body}


if __name__ == "__main__":
    client = AdjustS2SClient()
    logger.info("Adjust S2S Senior Client ready (App-Token: %s | Env: %s)", client.app_token, client.environment)
''',
                encoding="utf-8",
            )
            created.append(adj_path.name)

        self._refresh_project_files_tree()
        self.log_message(f"[MMP GENERATOR] Erstellt in '{out_dir}': {', '.join(created)}")

    # -----------------------------------------------------------------------
    # LAUNCH CLAUDE CODE DIRECTLY IN SELECTED PROJECT FOLDER
    # -----------------------------------------------------------------------
    def launch_claude_code(self):
        self.start_progress("Bereite Projekt-Session vor & starte Claude Code")
        self.save_config()
        self.save_agents_md()

        model = self.selected_model_var.get().strip()
        proj_name = self.active_project_name_var.get().strip()
        workspace = Path(self.workspace_var.get().strip())
        if not workspace.exists():
            workspace.mkdir(parents=True, exist_ok=True)

        proj_env = self._read_project_env(workspace)

        for proj in self.projects_list:
            if Path(proj.get("path", "")) == workspace or proj.get("name") == proj_name:
                proj["last_used"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                proj["preferred_model"] = model
        self.save_projects()
        self._refresh_projects_ui()

        mode = self.launch_mode_var.get()
        init_prompt = self.initial_prompt_var.get().strip()
        mmp_focus = self.mmp_preset_var.get()

        self.log_message(
            f"[LAUNCH] Starte Claude Code im Projekt '{proj_name}' ({workspace}) mit Modell '{model}' (inkl. .env Keys)..."
        )

        launcher_ps1 = workspace / ".shoxx_launch_claude.ps1"

        prompt_arg = ""
        if init_prompt:
            escaped_prompt = init_prompt.replace('"', '\\"')
            prompt_arg = f' "{escaped_prompt}"'

        if mode == "ollama_launch":
            exec_line = f'ollama launch claude --model "{model}"'
        else:
            exec_line = f'claude --model "{model}"{prompt_arg}'

        env_export_lines = "\n".join([f'$env:{k} = "{v}"' for k, v in proj_env.items()])

        ps1_content = f"""$Host.UI.RawUI.WindowTitle = "SHOXX // {proj_name} [{model}]"
$env:ANTHROPIC_BASE_URL = "{OLLAMA_HOST}"
$env:ANTHROPIC_AUTH_TOKEN = "ollama"
$env:ANTHROPIC_API_KEY = ""
$env:CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
{env_export_lines}

Clear-Host
Write-Host "==========================================================================" -ForegroundColor DarkCyan
Write-Host "  SHOXX // CLAUDE CODE LOCAL STUDIO — PROJEKT-SESSION" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor DarkCyan
Write-Host "  Aktives Projekt  : {proj_name}" -ForegroundColor Yellow
Write-Host "  Projekt-Ordner   : {workspace}" -ForegroundColor White
Write-Host "  Aktives Modell   : {model} (Local Ollama)" -ForegroundColor Green
Write-Host "  Anthropic Bridge : {OLLAMA_HOST}" -ForegroundColor Gray
Write-Host "  Projekt .env     : Geladen (AppsFlyer / Singular / Adjust Keys aktiv)" -ForegroundColor Green
Write-Host "  MMP Senior Fokus : {mmp_focus}" -ForegroundColor Cyan
Write-Host "==========================================================================" -ForegroundColor DarkCyan
Write-Host ""

Set-Location -LiteralPath "{workspace}"
{exec_line}
"""
        launcher_ps1.write_text(ps1_content, encoding="utf-8")

        try:
            subprocess.Popen(
                [
                    "cmd.exe",
                    "/c",
                    "start",
                    f"SHOXX [{proj_name}] - {model}",
                    "powershell.exe",
                    "-NoExit",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(launcher_ps1),
                ],
                cwd=str(workspace),
            )
            self.log_message(f"[SUCCESS] Claude Code wurde direkt im Projektordner '{workspace}' gestartet!")
        except Exception as e:
            self.log_message(f"[ERROR] Konnte Claude Code Terminal nicht starten: {e}")
            messagebox.showerror("Startfehler", f"Fehler beim Starten von Claude Code:\n{e}")
        finally:
            self.after(900, self.stop_progress)


if __name__ == "__main__":
    app = ShoxxClaudeStudio()
    app.mainloop()
