"""
3Go — YouTube Video & Playlist Downloader
Built with PySide6 + yt-dlp + ffmpeg
"""

import ctypes
import os
import re
import sys
from pathlib import Path

from PySide6.QtCore import (
    Qt,
    Signal,
    QThread,
    QPropertyAnimation,
    QEasingCurve,
)
from PySide6.QtGui import QFont, QColor, QIcon, QPixmap, QPainter, QLinearGradient
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QProgressBar,
    QScrollArea,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QFileDialog,
    QMessageBox,
    QFrame,
    QStackedWidget,
    QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect,
)

import yt_dlp


# ─── Paths ──────────────────────────────────────────────────

def _resource_path(relative: str) -> str:
    """Resolve path for both dev and PyInstaller frozen mode."""
    if getattr(sys, "frozen", False):
        base = sys._MEIPASS
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative)


NODE_PATH = r"C:\Program Files\nodejs\node.exe"
LOGO_PATH = _resource_path("logo.png")

# Resilient download settings
YDL_RESILIENCE = {
    "retries": 10,
    "fragment_retries": 10,
    "file_access_retries": 5,
    "extractor_retries": 5,
    "socket_timeout": 30,
}

QUALITY_FORMATS = [
    "bestvideo+bestaudio/best",
    "bestvideo[height<=2160]+bestaudio/best",
    "bestvideo[height<=1080]+bestaudio/best",
    "bestvideo[height<=720]+bestaudio/best",
    "bestvideo[height<=480]+bestaudio/best",
    "bestvideo[height<=360]+bestaudio/best",
    "bestaudio[ext=m4a]/bestaudio",
]


# ─── Translations ───────────────────────────────────────────

TR = {
    "uk": {
        "subtitle": "Video & Playlist Downloader",
        "url_placeholder": "Посилання на вiдео або плейлист...",
        "btn_paste": "Вставити",
        "btn_fetch": "Отримати",
        "btn_folder": "Папка",
        "quality_label": "Якiсть:",
        "quality_options": [
            "Найкраща", "2160p (4K)", "1080p (Full HD)",
            "720p (HD)", "480p (SD)", "360p", "Аудiо (m4a)",
        ],
        "section_format": "Формати:",
        "btn_select_all": "Все",
        "btn_deselect_all": "Зняти",
        "btn_download": "Завантажити",
        "status_ready": "Готовий",
        "status_fetching": "Отримання...",
        "status_fetching_fmt": "Формати...",
        "status_downloading": "Завантаження...",
        "status_done": "Завантажено!",
        "status_pl_done": "Плейлист завантажено!",
        "status_starting": "Початок...",
        "status_error_prefix": "Помилка",
        "placeholder_hint": "Вставте URL та натиснiть Отримати",
        "msg_error": "Помилка",
        "msg_warning": "Увага",
        "msg_success": "Успiх",
        "msg_select_format": "Оберiть формат!",
        "msg_select_video": "Оберiть хоча б одне вiдео!",
        "msg_format_404": "Формат не знайдено",
        "msg_file_done": "Файл завантажено!",
        "msg_pl_done_tpl": "Плейлист \"{title}\" завантажено!",
        "lbl_formats_found": "{n} форматiв",
        "lbl_playlist_info": "{title}  ({n} вiдео)",
        "lbl_video_of": "{cur} / {tot}",
        "audio_tag": "audio",
        "video_tag": "video",
    },
    "en": {
        "subtitle": "Video & Playlist Downloader",
        "url_placeholder": "Video or playlist link...",
        "btn_paste": "Paste",
        "btn_fetch": "Fetch",
        "btn_folder": "Folder",
        "quality_label": "Quality:",
        "quality_options": [
            "Best", "2160p (4K)", "1080p (Full HD)",
            "720p (HD)", "480p (SD)", "360p", "Audio (m4a)",
        ],
        "section_format": "Formats:",
        "btn_select_all": "All",
        "btn_deselect_all": "None",
        "btn_download": "Download",
        "status_ready": "Ready",
        "status_fetching": "Fetching...",
        "status_fetching_fmt": "Formats...",
        "status_downloading": "Downloading...",
        "status_done": "Done!",
        "status_pl_done": "Playlist downloaded!",
        "status_starting": "Starting...",
        "status_error_prefix": "Error",
        "placeholder_hint": "Paste URL and click Fetch",
        "msg_error": "Error",
        "msg_warning": "Warning",
        "msg_success": "Success",
        "msg_select_format": "Select a format!",
        "msg_select_video": "Select at least one video!",
        "msg_format_404": "Format not found",
        "msg_file_done": "File downloaded!",
        "msg_pl_done_tpl": "Playlist \"{title}\" downloaded!",
        "lbl_formats_found": "{n} formats",
        "lbl_playlist_info": "{title}  ({n} videos)",
        "lbl_video_of": "{cur} / {tot}",
        "audio_tag": "audio",
        "video_tag": "video",
    },
}


# ─── Glassmorphism Dark Stylesheet ──────────────────────────

STYLESHEET = """
/* ── Global ── */
QMainWindow {
    background: transparent;
}
QWidget#centralBg {
    background-color: rgba(10, 10, 10, 180);
}
QWidget {
    background: transparent;
    color: #e8e8e8;
    font-family: "Segoe UI", "Inter", "SF Pro Display", sans-serif;
    font-size: 13px;
}

/* ── Glass Cards ── */
QFrame#card {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.10);
    border-radius: 16px;
    padding: 14px;
}
QFrame#cardGlow {
    background-color: rgba(255, 100, 50, 0.04);
    border: 1px solid rgba(255, 120, 60, 0.14);
    border-radius: 16px;
    padding: 14px;
}

/* ── Labels ── */
QLabel {
    background: transparent;
    color: #e8e8e8;
}
QLabel#title {
    font-size: 26px;
    font-weight: 800;
    color: #FF6B35;
    letter-spacing: 2px;
}
QLabel#subtitle {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.35);
    letter-spacing: 1px;
}
QLabel#sectionTitle {
    font-size: 13px;
    font-weight: 600;
    color: #FF6B35;
}
QLabel#statusLabel {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.45);
}
QLabel#overallProgress {
    font-size: 13px;
    font-weight: 700;
    color: #FF6B35;
}
QLabel#logoLabel {
    background: transparent;
}

/* ── Line Edits ── */
QLineEdit {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 10px 14px;
    color: #e8e8e8;
    font-size: 13px;
    selection-background-color: #FF6B35;
}
QLineEdit:focus {
    border: 1px solid rgba(255, 107, 53, 0.5);
    background-color: rgba(255, 255, 255, 0.08);
}

/* ── Buttons ── */
QPushButton {
    background-color: rgba(255, 107, 53, 0.85);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: 600;
    font-size: 13px;
    min-width: 70px;
}
QPushButton:hover {
    background-color: rgba(255, 130, 80, 0.95);
}
QPushButton:pressed {
    background-color: rgba(200, 75, 30, 0.9);
}
QPushButton:disabled {
    background-color: rgba(255, 255, 255, 0.06);
    color: rgba(255, 255, 255, 0.2);
}

QPushButton#glassBtn {
    background-color: rgba(255, 255, 255, 0.07);
    color: #ccc;
    border: 1px solid rgba(255, 255, 255, 0.1);
    min-width: 60px;
}
QPushButton#glassBtn:hover {
    background-color: rgba(255, 255, 255, 0.12);
    color: #fff;
    border: 1px solid rgba(255, 255, 255, 0.18);
}

QPushButton#smallBtn {
    padding: 5px 12px;
    font-size: 11px;
    border-radius: 8px;
    background-color: rgba(255, 255, 255, 0.06);
    color: #aaa;
    border: 1px solid rgba(255, 255, 255, 0.08);
    min-width: 40px;
}
QPushButton#smallBtn:hover {
    background-color: rgba(255, 255, 255, 0.1);
    color: #fff;
}

QPushButton#langBtn {
    background: transparent;
    color: rgba(255, 255, 255, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
    min-width: 36px;
    letter-spacing: 1px;
}
QPushButton#langBtn:hover {
    color: rgba(255, 255, 255, 0.6);
    border-color: rgba(255, 255, 255, 0.15);
}
QPushButton#langBtnActive {
    background: rgba(255, 107, 53, 0.15);
    color: #FF6B35;
    border: 1px solid rgba(255, 107, 53, 0.3);
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 11px;
    font-weight: 700;
    min-width: 36px;
    letter-spacing: 1px;
}

QPushButton#downloadBtn {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #FF6B35, stop:1 #FF8F5E
    );
    color: #fff;
    border: none;
    border-radius: 14px;
    padding: 14px 28px;
    font-weight: 700;
    font-size: 15px;
    letter-spacing: 1px;
}
QPushButton#downloadBtn:hover {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #FF8F5E, stop:1 #FFA878
    );
}
QPushButton#downloadBtn:pressed {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #cc5528, stop:1 #e0734a
    );
}
QPushButton#downloadBtn:disabled {
    background: rgba(255, 255, 255, 0.05);
    color: rgba(255, 255, 255, 0.15);
}

/* ── ComboBox ── */
QComboBox {
    background-color: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 12px;
    padding: 10px 14px;
    color: #e8e8e8;
    min-width: 160px;
}
QComboBox:hover {
    border: 1px solid rgba(255, 107, 53, 0.3);
}
QComboBox::drop-down {
    border: none;
    width: 28px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #FF6B35;
    margin-right: 10px;
}
QComboBox QAbstractItemView {
    background-color: #1a1a1a;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    color: #e8e8e8;
    selection-background-color: rgba(255, 107, 53, 0.3);
    selection-color: #fff;
    outline: none;
    padding: 4px;
}

/* ── Progress Bar ── */
QProgressBar {
    background-color: rgba(255, 255, 255, 0.05);
    border: none;
    border-radius: 7px;
    text-align: center;
    color: #e8e8e8;
    font-size: 10px;
    min-height: 14px;
    max-height: 14px;
}
QProgressBar::chunk {
    background: qlineargradient(
        x1:0, y1:0, x2:1, y2:0,
        stop:0 #FF6B35, stop:1 #FF8F5E
    );
    border-radius: 7px;
}

/* ── Scroll Area ── */
QScrollArea {
    background: transparent;
    border: none;
}
QScrollArea > QWidget > QWidget {
    background: transparent;
}
QScrollBar:vertical {
    background: rgba(255, 255, 255, 0.03);
    width: 6px;
    border-radius: 3px;
    margin: 2px;
}
QScrollBar::handle:vertical {
    background: rgba(255, 107, 53, 0.4);
    border-radius: 3px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: rgba(255, 107, 53, 0.6);
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* ── Checkboxes & Radio Buttons ── */
QCheckBox, QRadioButton {
    color: rgba(255, 255, 255, 0.75);
    spacing: 10px;
    padding: 5px 0;
    background: transparent;
    font-size: 13px;
}
QCheckBox:hover, QRadioButton:hover {
    color: #fff;
}
QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.04);
}
QRadioButton::indicator {
    border-radius: 10px;
}
QCheckBox::indicator:checked, QRadioButton::indicator:checked {
    background-color: #FF6B35;
    border-color: #FF6B35;
}
QCheckBox::indicator:hover, QRadioButton::indicator:hover {
    border-color: rgba(255, 107, 53, 0.5);
}

/* ── Message Box ── */
QMessageBox {
    background-color: #1a1a1a;
}
QMessageBox QLabel {
    color: #e8e8e8;
}
QMessageBox QPushButton {
    min-width: 80px;
}
"""


# ─── Worker Threads ─────────────────────────────────────────

class FetchWorker(QThread):
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            opts = {
                **YDL_RESILIENCE,
                "quiet": True, "no_warnings": True,
                "extract_flat": "in_playlist",
                "js_runtime": NODE_PATH,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
            self.finished.emit(info)
        except Exception as exc:
            self.error.emit(str(exc))


class FetchFormatsWorker(QThread):
    finished = Signal(list)
    error = Signal(str)

    def __init__(self, url: str):
        super().__init__()
        self.url = url

    def run(self):
        try:
            opts = {
                **YDL_RESILIENCE,
                "quiet": True, "no_warnings": True,
                "js_runtime": NODE_PATH,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
            self.finished.emit(info.get("formats", []))
        except Exception as exc:
            self.error.emit(str(exc))


class DownloadWorker(QThread):
    progress = Signal(float, str)
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, url: str, opts: dict):
        super().__init__()
        self.url = url
        self.opts = opts

    def _hook(self, d):
        if d["status"] == "downloading":
            raw = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                pct = float(raw)
            except ValueError:
                pct = 0.0
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            self.progress.emit(pct, f"{pct:.1f}%  |  {speed}  |  ETA {eta}")
        elif d["status"] == "finished":
            self.progress.emit(100.0, "...")

    def run(self):
        self.opts["progress_hooks"] = [self._hook]
        try:
            with yt_dlp.YoutubeDL(self.opts) as ydl:
                ydl.download([self.url])
            self.finished.emit("OK")
        except Exception as exc:
            self.error.emit(str(exc))


class PlaylistDownloadWorker(QThread):
    video_progress = Signal(float, str)
    overall_progress = Signal(int, int, str)
    finished = Signal()
    error = Signal(str, str)

    def __init__(self, entries, quality_fmt, save_path, playlist_title, lang):
        super().__init__()
        self.entries = entries
        self.quality_fmt = quality_fmt
        self.save_path = save_path
        self.playlist_title = playlist_title
        self.lang = lang
        self._cancel = False

    def cancel(self):
        self._cancel = True

    def _hook(self, d):
        if self._cancel:
            raise Exception("Cancelled")
        if d["status"] == "downloading":
            raw = d.get("_percent_str", "0%").replace("%", "").strip()
            try:
                pct = float(raw)
            except ValueError:
                pct = 0.0
            speed = d.get("_speed_str", "")
            eta = d.get("_eta_str", "")
            self.video_progress.emit(pct, f"{pct:.1f}%  |  {speed}  |  ETA {eta}")
        elif d["status"] == "finished":
            self.video_progress.emit(100.0, "...")

    def run(self):
        safe_title = _safe_filename(self.playlist_title or "Playlist")
        out_dir = os.path.join(self.save_path, safe_title)
        os.makedirs(out_dir, exist_ok=True)

        total = len(self.entries)
        pad = len(str(total))

        for idx, entry in enumerate(self.entries):
            if self._cancel:
                break

            title = entry.get("title", f"Video {idx + 1}")
            url = entry.get("url") or entry.get("webpage_url", "")
            if not url:
                self.error.emit(title, "URL not found")
                continue

            self.overall_progress.emit(idx + 1, total, title)
            self.video_progress.emit(0.0, TR[self.lang]["status_starting"])

            num_prefix = str(idx + 1).zfill(pad)
            outtmpl = os.path.join(out_dir, f"{num_prefix} - %(title)s.%(ext)s")

            is_audio_only = (
                "bestaudio" in self.quality_fmt
                and "bestvideo" not in self.quality_fmt
            )

            opts = {
                **YDL_RESILIENCE,
                "format": self.quality_fmt,
                "outtmpl": outtmpl,
                "progress_hooks": [self._hook],
                "quiet": True, "no_warnings": True,
                "js_runtime": NODE_PATH,
                "ignoreerrors": True,
                "restrictfilenames": False,
            }
            if not is_audio_only:
                opts["merge_output_format"] = "mp4"

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([url])
            except Exception as exc:
                if "Cancel" in str(exc):
                    break
                self.error.emit(title, str(exc))

        self.finished.emit()


# ─── Helpers ────────────────────────────────────────────────

def _safe_filename(s: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', '', s).strip()


def _glow(widget, blur=30, color=QColor(255, 107, 53, 50)):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setColor(color)
    eff.setOffset(0, 6)
    widget.setGraphicsEffect(eff)


def _enable_acrylic_blur(hwnd):
    """Enable Windows 11 Acrylic blur behind the window."""
    try:
        dwmapi = ctypes.windll.dwmapi

        # Dark title bar
        val = ctypes.c_int(1)
        dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(val), ctypes.sizeof(val))

        # Acrylic backdrop
        backdrop = ctypes.c_int(3)  # DWMSBT_TRANSIENTWINDOW = Acrylic
        dwmapi.DwmSetWindowAttribute(hwnd, 38, ctypes.byref(backdrop), ctypes.sizeof(backdrop))

        # Extend frame into client area for full blur
        margins = (ctypes.c_int * 4)(-1, -1, -1, -1)
        dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(margins))
    except Exception:
        pass  # Fallback: no blur on older Windows


# ─── Main Window ────────────────────────────────────────────

class MainWindow(QMainWindow):
    MODE_NONE = "none"
    MODE_SINGLE = "single"
    MODE_PLAYLIST = "playlist"

    def __init__(self):
        super().__init__()
        self.lang = "uk"
        self.mode = self.MODE_NONE
        self.formats = []
        self.playlist_entries = []
        self.playlist_title = ""
        self.save_path = os.path.expanduser("~/Downloads")
        self._worker = None

        self.setWindowTitle("3Go")
        self.setMinimumSize(760, 660)
        self.resize(800, 720)

        # Acrylic blur transparency
        self.setAttribute(Qt.WA_TranslucentBackground)

        # Window icon
        if os.path.exists(LOGO_PATH):
            self.setWindowIcon(QIcon(LOGO_PATH))

        central = QWidget()
        central.setObjectName("centralBg")
        self.setCentralWidget(central)
        self._root = QVBoxLayout(central)
        self._root.setContentsMargins(24, 20, 24, 20)
        self._root.setSpacing(14)

        self._build_header()
        self._build_url_section()
        self._build_path_section()
        self._build_quality_section()
        self._build_content_area()
        self._build_progress_section()
        self._build_download_button()

        self._blur_applied = False

    def showEvent(self, event):
        super().showEvent(event)
        if not self._blur_applied:
            self._blur_applied = True
            _enable_acrylic_blur(int(self.winId()))

    # ── Translate helper ─────────────────────────

    def t(self, key, **kw):
        val = TR[self.lang].get(key, key)
        return val.format(**kw) if kw else val

    # ── UI builders ──────────────────────────────

    def _build_header(self):
        header = QHBoxLayout()
        header.setSpacing(12)

        self.title_label = QLabel("3Go")
        self.title_label.setObjectName("title")
        header.addWidget(self.title_label)

        header.addSpacing(6)

        self.subtitle_label = QLabel()
        self.subtitle_label.setObjectName("subtitle")
        header.addWidget(self.subtitle_label)

        header.addStretch()

        self.btn_lang_uk = QPushButton("UKR")
        self.btn_lang_uk.setObjectName("langBtnActive")
        self.btn_lang_uk.setCursor(Qt.PointingHandCursor)
        self.btn_lang_uk.clicked.connect(lambda: self._set_language("uk"))
        header.addWidget(self.btn_lang_uk)

        self.btn_lang_en = QPushButton("ENG")
        self.btn_lang_en.setObjectName("langBtn")
        self.btn_lang_en.setCursor(Qt.PointingHandCursor)
        self.btn_lang_en.clicked.connect(lambda: self._set_language("en"))
        header.addWidget(self.btn_lang_en)

        self._root.addLayout(header)

    def _build_url_section(self):
        card = self._card()
        lay = QHBoxLayout(card)
        lay.setSpacing(10)

        self.url_input = QLineEdit()
        self.url_input.returnPressed.connect(self._on_fetch)
        lay.addWidget(self.url_input)

        self.btn_paste = QPushButton()
        self.btn_paste.setObjectName("glassBtn")
        self.btn_paste.setCursor(Qt.PointingHandCursor)
        self.btn_paste.clicked.connect(self._paste_and_fetch)
        lay.addWidget(self.btn_paste)

        self.btn_fetch = QPushButton()
        self.btn_fetch.setCursor(Qt.PointingHandCursor)
        self.btn_fetch.clicked.connect(self._on_fetch)
        lay.addWidget(self.btn_fetch)

        self._root.addWidget(card)

    def _build_path_section(self):
        card = self._card()
        lay = QHBoxLayout(card)

        self.path_label = QLabel(self.save_path)
        self.path_label.setObjectName("statusLabel")
        lay.addWidget(self.path_label, 1)

        self.btn_folder = QPushButton()
        self.btn_folder.setObjectName("glassBtn")
        self.btn_folder.setCursor(Qt.PointingHandCursor)
        self.btn_folder.clicked.connect(self._choose_dir)
        lay.addWidget(self.btn_folder)

        self._root.addWidget(card)

    def _build_quality_section(self):
        card = self._card()
        lay = QHBoxLayout(card)

        self.quality_lbl = QLabel()
        lay.addWidget(self.quality_lbl)

        self.quality_combo = QComboBox()
        self.quality_combo.setCursor(Qt.PointingHandCursor)
        lay.addWidget(self.quality_combo, 1)

        self._root.addWidget(card)

    def _build_content_area(self):
        self.stack = QStackedWidget()

        # Page 0 — Placeholder
        self.placeholder_label = QLabel()
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.placeholder_label.setObjectName("subtitle")
        self.placeholder_label.setMinimumHeight(120)
        self.stack.addWidget(self.placeholder_label)

        # Page 1 — Single video
        self._single_page = QWidget()
        sp_lay = QVBoxLayout(self._single_page)
        sp_lay.setContentsMargins(0, 0, 0, 0)
        self.single_section_lbl = QLabel()
        self.single_section_lbl.setObjectName("sectionTitle")
        sp_lay.addWidget(self.single_section_lbl)

        scroll_s = QScrollArea()
        scroll_s.setWidgetResizable(True)
        scroll_s.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._single_scroll_content = QWidget()
        self._single_scroll_layout = QVBoxLayout(self._single_scroll_content)
        self._single_scroll_layout.setAlignment(Qt.AlignTop)
        self._single_scroll_layout.setSpacing(2)
        scroll_s.setWidget(self._single_scroll_content)
        sp_lay.addWidget(scroll_s)
        self._radio_group = QButtonGroup(self)
        self.stack.addWidget(self._single_page)

        # Page 2 — Playlist
        self._playlist_page = QWidget()
        pp_lay = QVBoxLayout(self._playlist_page)
        pp_lay.setContentsMargins(0, 0, 0, 0)

        top_row = QHBoxLayout()
        self._pl_title_label = QLabel()
        self._pl_title_label.setObjectName("sectionTitle")
        top_row.addWidget(self._pl_title_label)
        top_row.addStretch()
        self.btn_select_all = QPushButton()
        self.btn_select_all.setObjectName("smallBtn")
        self.btn_select_all.setCursor(Qt.PointingHandCursor)
        self.btn_select_all.clicked.connect(self._select_all)
        top_row.addWidget(self.btn_select_all)
        self.btn_deselect_all = QPushButton()
        self.btn_deselect_all.setObjectName("smallBtn")
        self.btn_deselect_all.setCursor(Qt.PointingHandCursor)
        self.btn_deselect_all.clicked.connect(self._deselect_all)
        top_row.addWidget(self.btn_deselect_all)
        pp_lay.addLayout(top_row)

        scroll_p = QScrollArea()
        scroll_p.setWidgetResizable(True)
        scroll_p.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._playlist_scroll_content = QWidget()
        self._playlist_scroll_layout = QVBoxLayout(self._playlist_scroll_content)
        self._playlist_scroll_layout.setAlignment(Qt.AlignTop)
        self._playlist_scroll_layout.setSpacing(2)
        scroll_p.setWidget(self._playlist_scroll_content)
        pp_lay.addWidget(scroll_p)
        self.stack.addWidget(self._playlist_page)

        self._root.addWidget(self.stack, 1)

    def _build_progress_section(self):
        card = self._card("cardGlow")
        lay = QVBoxLayout(card)

        row = QHBoxLayout()
        self.status_label = QLabel()
        self.status_label.setObjectName("statusLabel")
        row.addWidget(self.status_label, 1)
        self.overall_label = QLabel("")
        self.overall_label.setObjectName("overallProgress")
        row.addWidget(self.overall_label)
        lay.addLayout(row)

        self.progressbar = QProgressBar()
        self.progressbar.setRange(0, 1000)
        self.progressbar.setValue(0)
        self.progressbar.setTextVisible(False)
        lay.addWidget(self.progressbar)

        self._root.addWidget(card)

    def _build_download_button(self):
        self.dl_button = QPushButton()
        self.dl_button.setObjectName("downloadBtn")
        self.dl_button.setCursor(Qt.PointingHandCursor)
        self.dl_button.setFixedHeight(50)
        self.dl_button.clicked.connect(self._start_download)
        _glow(self.dl_button, 40, QColor(255, 107, 53, 70))
        self._root.addWidget(self.dl_button)

        self._apply_texts()

    # ── Helpers ──────────────────────────────────

    def _card(self, name="card") -> QFrame:
        f = QFrame()
        f.setObjectName(name)
        return f

    def _clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    # ── Language ─────────────────────────────────

    def _set_language(self, lang):
        self.lang = lang
        if lang == "uk":
            self.btn_lang_uk.setObjectName("langBtnActive")
            self.btn_lang_en.setObjectName("langBtn")
        else:
            self.btn_lang_uk.setObjectName("langBtn")
            self.btn_lang_en.setObjectName("langBtnActive")
        self.btn_lang_uk.setStyleSheet(self.btn_lang_uk.styleSheet())
        self.btn_lang_en.setStyleSheet(self.btn_lang_en.styleSheet())
        self._apply_texts()

    def _apply_texts(self):
        self.subtitle_label.setText(self.t("subtitle"))
        self.url_input.setPlaceholderText(self.t("url_placeholder"))
        self.btn_paste.setText(self.t("btn_paste"))
        self.btn_fetch.setText(self.t("btn_fetch"))
        self.btn_folder.setText(self.t("btn_folder"))
        self.quality_lbl.setText(self.t("quality_label"))
        self.single_section_lbl.setText(self.t("section_format"))
        self.btn_select_all.setText(self.t("btn_select_all"))
        self.btn_deselect_all.setText(self.t("btn_deselect_all"))
        self.dl_button.setText(self.t("btn_download"))
        self.placeholder_label.setText(self.t("placeholder_hint"))
        self.status_label.setText(self.t("status_ready"))

        cur = self.quality_combo.currentIndex()
        if cur < 0:
            cur = 2
        self.quality_combo.blockSignals(True)
        self.quality_combo.clear()
        for name in self.t("quality_options"):
            self.quality_combo.addItem(name)
        self.quality_combo.setCurrentIndex(cur)
        self.quality_combo.blockSignals(False)

    # ── Actions ──────────────────────────────────

    def _paste_and_fetch(self):
        txt = QApplication.clipboard().text()
        if txt:
            self.url_input.setText(txt.strip())
            self._on_fetch()

    def _choose_dir(self):
        d = QFileDialog.getExistingDirectory(self, "...", self.save_path)
        if d:
            self.save_path = d
            self.path_label.setText(d)

    def _on_fetch(self):
        url = self.url_input.text().strip()
        if not url:
            return
        self.status_label.setText(self.t("status_fetching"))
        self.progressbar.setValue(0)
        self.overall_label.setText("")
        self.dl_button.setEnabled(False)
        self._fetch_worker = FetchWorker(url)
        self._fetch_worker.finished.connect(self._on_info_fetched)
        self._fetch_worker.error.connect(self._on_fetch_error)
        self._fetch_worker.start()

    def _on_fetch_error(self, msg):
        self.status_label.setText(f"{self.t('status_error_prefix')}: {msg[:80]}")
        self.dl_button.setEnabled(True)
        QMessageBox.critical(self, self.t("msg_error"), msg)

    def _on_info_fetched(self, info):
        entries = info.get("entries")
        if entries is not None:
            self.mode = self.MODE_PLAYLIST
            self.playlist_title = info.get("title", "Playlist")
            self.playlist_entries = [e for e in entries if e is not None]
            self._show_playlist_mode()
        else:
            self.mode = self.MODE_SINGLE
            self.status_label.setText(self.t("status_fetching_fmt"))
            self._fmt_worker = FetchFormatsWorker(self.url_input.text().strip())
            self._fmt_worker.finished.connect(self._on_formats_fetched)
            self._fmt_worker.error.connect(self._on_fetch_error)
            self._fmt_worker.start()

    def _on_formats_fetched(self, fmts):
        self.formats = fmts
        self._show_single_mode()

    def _show_single_mode(self):
        self._clear_layout(self._single_scroll_layout)
        for btn in self._radio_group.buttons():
            self._radio_group.removeButton(btn)

        at = self.t("audio_tag")
        vt = self.t("video_tag")

        for fmt in self.formats:
            itag = fmt.get("format_id", "?")
            ext = fmt.get("ext", "?")
            vc = fmt.get("vcodec", "none")
            ac = fmt.get("acodec", "none")
            res = fmt.get("resolution", "N/A")
            sz = fmt.get("filesize")
            st = f"{sz/1024/1024:.1f} MB" if isinstance(sz, (int, float)) else "N/A"

            show = False
            label = ""

            if vc == "none" and ac != "none" and ext == "m4a":
                abr = fmt.get("abr") or 0
                if abr >= 128:
                    label = f"{itag}  |  {abr:.0f}kbps  |  {st}  ({at})"
                    show = True
            elif ac == "none" and vc != "none" and ext == "mp4":
                try:
                    h = int(str(res).split("x")[-1])
                except (ValueError, IndexError):
                    h = 0
                if h in (144, 240, 360, 480, 720, 1080, 1440, 2160):
                    label = f"{itag}  |  {res}  |  {st}  ({vt})"
                    show = True

            if show:
                rb = QRadioButton(label)
                rb.setProperty("itag", itag)
                self._radio_group.addButton(rb)
                self._single_scroll_layout.addWidget(rb)

        self.stack.setCurrentIndex(1)
        self.status_label.setText(self.t("lbl_formats_found", n=len(self._radio_group.buttons())))
        self.dl_button.setEnabled(True)

    def _show_playlist_mode(self):
        self._clear_layout(self._playlist_scroll_layout)
        self._pl_checkboxes = []
        self._pl_title_label.setText(
            self.t("lbl_playlist_info", title=self.playlist_title, n=len(self.playlist_entries))
        )
        for i, entry in enumerate(self.playlist_entries):
            title = entry.get("title", f"Video {i+1}")
            dur = entry.get("duration")
            ds = ""
            if dur:
                m, s = divmod(int(dur), 60)
                ds = f"  ({m}:{s:02d})"
            cb = QCheckBox(f"{i+1}.  {title}{ds}")
            cb.setChecked(True)
            cb.setProperty("entry_idx", i)
            self._pl_checkboxes.append(cb)
            self._playlist_scroll_layout.addWidget(cb)

        self.stack.setCurrentIndex(2)
        self.status_label.setText(self.t("lbl_playlist_info", title=self.playlist_title, n=len(self.playlist_entries)))
        self.dl_button.setEnabled(True)

    def _select_all(self):
        for cb in self._pl_checkboxes:
            cb.setChecked(True)

    def _deselect_all(self):
        for cb in self._pl_checkboxes:
            cb.setChecked(False)

    # ── Download ─────────────────────────────────

    def _start_download(self):
        if self.mode == self.MODE_SINGLE:
            self._download_single()
        elif self.mode == self.MODE_PLAYLIST:
            self._download_playlist()

    def _download_single(self):
        sel = self._radio_group.checkedButton()
        if not sel:
            QMessageBox.warning(self, self.t("msg_warning"), self.t("msg_select_format"))
            return

        itag = sel.property("itag")
        url = self.url_input.text().strip()
        chosen = next((f for f in self.formats if str(f.get("format_id")) == str(itag)), None)
        if not chosen:
            QMessageBox.critical(self, self.t("msg_error"), self.t("msg_format_404"))
            return

        if chosen.get("vcodec") == "none":
            fs = str(itag)
        else:
            aus = [f for f in self.formats if f.get("vcodec") == "none" and f.get("acodec") != "none"]
            ba = max(aus, key=lambda f: f.get("abr") or 0) if aus else None
            ai = ba["format_id"] if ba else "bestaudio"
            fs = f"{itag}+{ai}"

        opts = {
            **YDL_RESILIENCE,
            "format": fs,
            "merge_output_format": "mp4",
            "outtmpl": os.path.join(self.save_path, "%(title)s.%(ext)s"),
            "js_runtime": NODE_PATH,
        }

        self.dl_button.setEnabled(False)
        self.status_label.setText(self.t("status_downloading"))
        self.progressbar.setValue(0)
        self._worker = DownloadWorker(url, opts)
        self._worker.progress.connect(self._on_dl_progress)
        self._worker.finished.connect(self._on_dl_finished)
        self._worker.error.connect(self._on_dl_error)
        self._worker.start()

    def _download_playlist(self):
        selected = []
        for cb in self._pl_checkboxes:
            if cb.isChecked():
                selected.append(self.playlist_entries[cb.property("entry_idx")])
        if not selected:
            QMessageBox.warning(self, self.t("msg_warning"), self.t("msg_select_video"))
            return

        qf = QUALITY_FORMATS[self.quality_combo.currentIndex()]
        self.dl_button.setEnabled(False)
        self.status_label.setText(self.t("status_downloading"))
        self.progressbar.setValue(0)
        self._worker = PlaylistDownloadWorker(
            selected, qf, self.save_path, self.playlist_title, self.lang
        )
        self._worker.video_progress.connect(self._on_dl_progress)
        self._worker.overall_progress.connect(self._on_pl_overall)
        self._worker.finished.connect(self._on_pl_finished)
        self._worker.error.connect(self._on_pl_error)
        self._worker.start()

    # ── Slots ────────────────────────────────────

    def _on_dl_progress(self, pct, text):
        self.progressbar.setValue(int(pct * 10))
        self.status_label.setText(text)

    def _on_dl_finished(self, _):
        self.progressbar.setValue(1000)
        self.status_label.setText(self.t("status_done"))
        self.dl_button.setEnabled(True)
        QMessageBox.information(self, self.t("msg_success"), self.t("msg_file_done"))

    def _on_dl_error(self, msg):
        self.status_label.setText(self.t("status_error_prefix"))
        self.dl_button.setEnabled(True)
        QMessageBox.critical(self, self.t("msg_error"), msg)

    def _on_pl_overall(self, cur, tot, title):
        self.overall_label.setText(self.t("lbl_video_of", cur=cur, tot=tot))
        self.status_label.setText(title)

    def _on_pl_finished(self):
        self.progressbar.setValue(1000)
        self.status_label.setText(self.t("status_pl_done"))
        self.overall_label.setText("")
        self.dl_button.setEnabled(True)
        QMessageBox.information(
            self, self.t("msg_success"),
            self.t("msg_pl_done_tpl", title=self.playlist_title)
        )

    def _on_pl_error(self, title, msg):
        self.status_label.setText(f"{self.t('status_error_prefix')}: {title}")


# ─── Entry Point ────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)
    app.setStyle("Fusion")

    if os.path.exists(LOGO_PATH):
        app.setWindowIcon(QIcon(LOGO_PATH))

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()