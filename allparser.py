import sys
import os
import time
import random
import math
import re
import json
import socket
import smtplib
import ssl as _ssl_mod
import threading
import queue
import sqlite3
import csv
import traceback
import webbrowser
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid
import datetime as _dt

MISSING_DEPS = []
try:
    from PyQt6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QProgressBar, QTextEdit, QLineEdit,
        QPlainTextEdit, QComboBox, QCheckBox, QFrame, QGraphicsDropShadowEffect,
        QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
        QListWidget, QListWidgetItem, QMessageBox, QDialog, QSlider,
        QScrollArea, QFileDialog, QSpinBox
    )
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QObject, QRectF, QPointF, QUrl, QPoint, QRect, QSize
    from PyQt6.QtGui import (
        QPainter, QColor, QFont, QLinearGradient, QBrush, QPen,
        QRadialGradient, QCursor, QIcon, QPixmap, QImage, QPainterPath
    )
    QT_BINDING = "PyQt6"
except ImportError:
    try:
        from PySide6.QtWidgets import (
            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
            QPushButton, QLabel, QProgressBar, QTextEdit, QLineEdit,
            QPlainTextEdit, QComboBox, QCheckBox, QFrame, QGraphicsDropShadowEffect,
            QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView,
            QListWidget, QListWidgetItem, QMessageBox, QDialog, QSlider,
            QScrollArea, QFileDialog, QSpinBox
        )
        from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal as pyqtSignal, QObject, QRectF, QPointF, QUrl, QPoint, QRect, QSize
        from PySide6.QtGui import (
            QPainter, QColor, QFont, QLinearGradient, QBrush, QPen,
            QRadialGradient, QCursor, QIcon, QPixmap, QImage, QPainterPath
        )
        QT_BINDING = "PySide6"
    except ImportError:
        MISSING_DEPS.append("PyQt6")
        QT_BINDING = None
        class QObject: pass
        class QWidget: pass
        class QFrame: pass
        class QMainWindow: pass
        def pyqtSignal(*args, **kwargs): return None
try:
    import requests
except ImportError:
    requests = None
    MISSING_DEPS.append("requests")
try:
    import dns.resolver
except ImportError:
    dns = None
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    curl_requests = None

HAS_MULTIMEDIA = False
try:
    if QT_BINDING == "PyQt6":
        from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
        HAS_MULTIMEDIA = True
    elif QT_BINDING == "PySide6":
        from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
        HAS_MULTIMEDIA = True
except Exception:
    HAS_MULTIMEDIA = False

# =====================================================================
# АНТИ-КРАШ: ЛОГИРОВАНИЕ ЛЮБОГО ПАДЕНИЯ В crash_log.txt
# =====================================================================
CRASH_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "crash_log.txt")
def _write_crash(text):
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"=== {time.strftime('%Y-%m-%d %H:%M:%S')} ===\n{text}\n\n")
    except Exception:
        pass
def _crash_hook(exc_type, exc, tb):
    _write_crash("".join(traceback.format_exception(exc_type, exc, tb)))
    sys.__excepthook__(exc_type, exc, tb)
def _thread_crash_hook(args):
    _write_crash("".join(traceback.format_exception(args.exc_type, args.exc_value, args.exc_traceback)))
sys.excepthook = _crash_hook
threading.excepthook = _thread_crash_hook

COUNTRY_TLD_MAP = {
    'ru': ('Россия', ''), 'su': ('Россия / СНГ', ''), 'рф': ('Россия', ''),
    'ua': ('Украина', ''), 'by': ('Беларусь', ''), 'kz': ('Казахстан', ''),
    'de': ('Германия', ''), 'uk': ('Великобритания', ''), 'fr': ('Франция', ''),
    'it': ('Италия', ''), 'es': ('Испания', ''), 'pl': ('Польша', ''),
    'nl': ('Нидерланды', ''), 'ch': ('Швейцария', ''), 'at': ('Австрия', ''),
    'cz': ('Чехия', ''), 'se': ('Швеция', ''), 'no': ('Норвегия', ''),
    'fi': ('Финляндия', ''), 'dk': ('Дания', ''), 'jp': ('Япония', ''),
    'cn': ('Китай', ''), 'kr': ('Южная Корея', ''), 'in': ('Индия', ''),
    'br': ('Бразилия', ''), 'ca': ('Канада', ''), 'au': ('Австралия', ''),
    'us': ('США', ''), 'tr': ('Турция', ''), 'il': ('Израиль', ''),
    'ae': ('ОАЭ', ''), 'sg': ('Сингапур', ''), 'za': ('ЮАР', ''),
    'pt': ('Португалия', ''), 'gr': ('Греция', ''), 'be': ('Бельгия', ''),
    'ro': ('Румыния', ''), 'hu': ('Венгрия', ''), 'bg': ('Болгария', ''),
    'rs': ('Сербия', ''), 'am': ('Армения', ''), 'ge': ('Грузия', ''),
    'uz': ('Узбекистан', ''), 'az': ('Азербайджан', ''), 'mx': ('Мексика', ''),
    'io': ('Global / Tech', ''), 'ai': ('Global / AI', ''),
    'dev': ('Global / Dev', ''), 'org': ('Международный Org', ''),
    'net': ('Международный Net', ''), 'com': ('Международный Com', '')
}
POPULAR_DOMAINS_MAP = {
    'yandex.ru': ('Россия', ''), 'mail.ru': ('Россия', ''), 'bk.ru': ('Россия', ''),
    'inbox.ru': ('Россия', ''), 'list.ru': ('Россия', ''), 'rambler.ru': ('Россия', ''),
    'ya.ru': ('Россия', ''), 'internet.ru': ('Россия', ''),
    'ukr.net': ('Украина', ''), 'i.ua': ('Украина', ''),
    'seznam.cz': ('Чехия', ''),
    'gmx.de': ('Германия', ''), 'web.de': ('Германия', ''), 't-online.de': ('Германия', ''),
    'qq.com': ('Китай', ''), '163.com': ('Китай', ''),
    'naver.com': ('Южная Корея', ''),
    'orange.fr': ('Франция', ''), 'free.fr': ('Франция', ''),
    'gmail.com': ('США / Global', ''), 'googlemail.com': ('США / Global', ''),
    'outlook.com': ('США / Global', ''), 'hotmail.com': ('США / Global', ''),
    'yahoo.com': ('США / Global', ''), 'icloud.com': ('США / Global', ''),
    'proton.me': ('Швейцария / Global', ''), 'protonmail.com': ('Швейцария / Global', ''),
    'aol.com': ('США', '')
}
PERSONAL_PROVIDERS = {'gmail.com', 'googlemail.com', 'yandex.ru', 'ya.ru', 'mail.ru', 'bk.ru',
                      'inbox.ru', 'list.ru', 'yahoo.com', 'outlook.com', 'hotmail.com',
                      'icloud.com', 'proton.me', 'protonmail.com', 'aol.com', 'gmx.de', 'web.de'}
DEV_DOMAINS = {'github.com', 'gitlab.com', 'bitbucket.org', 'kernel.org', 'apache.org',
               'mozilla.org', 'gnome.org', 'kde.org', 'python.org', 'rust-lang.org',
               'golang.org', 'gnu.org', 'savannah.org', 'sourceforge.net'}

def detect_country(email: str) -> str:
    if '@' not in email:
        return "Международный"
    domain = email.split('@')[-1].lower().strip()
    if domain in POPULAR_DOMAINS_MAP:
        return POPULAR_DOMAINS_MAP[domain][0]
    parts = domain.split('.')
    tld = parts[-1] if parts else ''
    if tld in COUNTRY_TLD_MAP:
        return COUNTRY_TLD_MAP[tld][0]
    return "Международный"

def estimate_last_active(email: str, source_url: str = "") -> str:
    now = _dt.datetime.now()
    src_lower = source_url.lower()
    if any(k in src_lower for k in ("commit", "pull", "maintainer", "author", "mailmap")):
        days_ago = random.randint(0, 4)
        return (now - _dt.timedelta(days=days_ago, hours=random.randint(1, 12))).strftime("%Y-%m-%d %H:%M")
    elif any(k in src_lower for k in ("trending", "news", "forum", "live")):
        return (now - _dt.timedelta(hours=random.randint(1, 16))).strftime("%Y-%m-%d %H:%M")
    else:
        days_ago = random.randint(2, 30)
        return (now - _dt.timedelta(days=days_ago)).strftime("%Y-%m-%d")

def normalize_url(url: str):
    try:
        p = urlsplit(url.strip())
        if p.scheme not in ("http", "https"):
            return None
        netloc = p.netloc.lower().split("@")[-1].split(":")[0]
        if not netloc:
            return None
        path = p.path.rstrip("/") or "/"
        qs = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
              if not k.lower().startswith(("utm_", "ref", "fbclid", "gclid"))]
        return urlunsplit((p.scheme, netloc, path, urlencode(qs), ""))
    except Exception:
        return None

class EmailDatabase:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "allparser_database.sqlite")
    CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPocht.csv")
    TXT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPochtRassilka.txt")
    _lock = threading.Lock()
    @classmethod
    def _conn(cls):
        conn = sqlite3.connect(cls.DB_PATH, timeout=10)
        try:
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=NORMAL;")
        except Exception:
            pass
        return conn
    @classmethod
    def init_db(cls):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE,
                    domain TEXT,
                    country TEXT,
                    last_active TEXT,
                    category TEXT,
                    target_source TEXT,
                    status TEXT,
                    score INTEGER,
                    discovered_at TEXT
                )
            """)
            c.execute("CREATE INDEX IF NOT EXISTS idx_emails_domain ON emails(domain);")
            c.execute("CREATE INDEX IF NOT EXISTS idx_emails_status ON emails(status);")
            conn.commit(); conn.close()
    @classmethod
    def insert_email(cls, email: str, category: str, source: str, status: str = "SAFE", score: int = 90):
        email = email.strip().lower()
        domain = email.split('@')[-1]
        country = detect_country(email)
        last_active = estimate_last_active(email, source)
        now_str = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with cls._lock:
            conn = cls._conn(); c = conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO emails
                (email, domain, country, last_active, category, target_source, status, score, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email, domain, country, last_active, category, source, status, score, now_str))
            conn.commit(); conn.close()
        cls.append_to_csv(email, domain, country, last_active, category, source, status, score, now_str)
        try:
            with open(cls.TXT_PATH, "a", encoding="utf-8") as f:
                f.write(f"{email}\n")
        except Exception:
            pass
        return country, last_active
    @classmethod
    def update_status(cls, email, status, score):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor()
            c.execute("UPDATE emails SET status=?, score=? WHERE email=?", (status, score, email))
            conn.commit(); conn.close()
    @classmethod
    def append_to_csv(cls, email, domain, country, last_active, category, source, status, score, now_str):
        write_header = not os.path.exists(cls.CSV_PATH) or os.path.getsize(cls.CSV_PATH) == 0
        try:
            with open(cls.CSV_PATH, "a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                if write_header:
                    writer.writerow(["EMAIL", "DOMAIN", "COUNTRY", "LAST_ACTIVE", "CATEGORY", "SOURCE", "STATUS", "SCORE", "DISCOVERED_AT"])
                writer.writerow([email, domain, country, last_active, category, source, status, score, now_str])
        except Exception:
            pass
    @classmethod
    def get_all_records(cls):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor()
            c.execute("SELECT id, email, country, last_active, category, target_source, status, score, discovered_at FROM emails ORDER BY id DESC")
            rows = c.fetchall(); conn.close()
            return rows
    @classmethod
    def get_count(cls):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor(); c.execute("SELECT COUNT(*) FROM emails")
            count = c.fetchone()[0]; conn.close()
            return count
    @classmethod
    def get_stats(cls):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor()
            c.execute("SELECT COUNT(*), SUM(status='SAFE'), SUM(status='TRAP'), SUM(status='RISKY'), SUM(status='INVALID'), SUM(category LIKE '%HUMAN%') FROM emails")
            row = c.fetchone(); conn.close()
            return {"total": row[0] or 0, "safe": row[1] or 0, "trap": row[2] or 0,
                    "risky": row[3] or 0, "invalid": row[4] or 0, "personal": row[5] or 0}
    @classmethod
    def clear_database(cls):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor(); c.execute("DELETE FROM emails")
            conn.commit(); conn.close()
        for p in (cls.CSV_PATH, cls.TXT_PATH):
            try:
                if os.path.exists(p): os.remove(p)
            except Exception:
                pass
    @classmethod
    def purge_invalids_and_traps(cls):
        with cls._lock:
            conn = cls._conn(); c = conn.cursor()
            c.execute("DELETE FROM emails WHERE status IN ('TRAP', 'INVALID')")
            deleted = c.rowcount
            conn.commit(); conn.close()
            return deleted
EmailDatabase.init_db()

if QT_BINDING:
    class ParserSignals(QObject):
        log_signal = pyqtSignal(str, str, object)
        account_signal = pyqtSignal(str, str, str, str)
        progress_signal = pyqtSignal(int)
        status_signal = pyqtSignal(str, bool)
        domain_signal = pyqtSignal(str)
        auto_iter_signal = pyqtSignal(str)
        val_row_signal = pyqtSignal(str, str, int, str, str, str)
        val_done_signal = pyqtSignal()
        val_progress_signal = pyqtSignal(int, int)
        mail_log_signal = pyqtSignal(str, str)
        mail_sent_signal = pyqtSignal(str, str)
        mail_status_signal = pyqtSignal(str, str)
        radio_status_signal = pyqtSignal(str, bool)
else:
    class ParserSignals:
        pass

# =====================================================================
# ТЕМЫ
# =====================================================================
LIGHT_QSS = """
QMainWindow { background-color: #f5f4f2; }
QLabel { background: transparent; color: #222226; }
QWidget#sidebar { background: transparent; }
QStackedWidget { background: transparent; }
QPushButton#navBtn { font-family:"Segoe UI",sans-serif; font-size:13px; font-weight:600; color:#6b6b70; background:transparent; border:none; border-radius:14px; padding:11px 14px; text-align:left; min-height:42px; }
QPushButton#navBtn:hover { color:#111114; background:rgba(0,0,0,0.05); }
QPushButton#navBtn[class="active"] { background:#111114; color:#ffffff; font-weight:700; }
QLabel#badge { background:#efedea; color:#6b6b70; border:none; border-radius:6px; font-size:8px; font-weight:800; padding:3px 6px; }
QLabel#h1 { color:#111114; font-family:"Segoe UI",sans-serif; font-size:30px; font-weight:800; }
QLabel#tTitle { color:#111114; font-family:"Segoe UI",sans-serif; font-size:14px; font-weight:700; }
QLabel#tText { color:#222226; font-family:"Segoe UI",sans-serif; font-size:12px; }
QLabel#tDim { color:#8a8a8e; font-family:"Segoe UI",sans-serif; font-size:12px; }
QLabel#tMono { color:#8a8a8e; font-family:Consolas,monospace; font-size:11px; }
QLabel#cText { color:#ffffff; }
QLabel#cDim { color:#9a9aa2; }
QLabel#cBig { color:#ffffff; font-family:"Segoe UI",sans-serif; font-size:40px; font-weight:800; }
QFrame#cTile { background:#232327; border-radius:14px; }
QLabel#tOk { color:#2f7d4f; }
QLabel#tErr { color:#c22f3d; }
QLabel#tWarn { color:#b7791f; }
QLabel#statValue { font-family:"Segoe UI",sans-serif; font-size:30px; font-weight:800; color:#111114; }
QLabel#statLabel { font-family:"Segoe UI",sans-serif; font-size:10px; color:#8a8a8e; letter-spacing:1px; }
QLabel#statusText { font-family:Consolas,monospace; font-size:11px; color:#8a8a8e; letter-spacing:2px; }
QPushButton#actionBtn { font-family:"Segoe UI",sans-serif; font-size:12px; font-weight:700; color:#111114; background:#ffffff; border:1px solid #e4e2de; border-radius:999px; padding:11px 20px; min-height:42px; }
QPushButton#actionBtn:hover { background:#f4f2ef; border-color:#d6d4d0; }
QPushButton#actionBtn:pressed { background:#e9e7e3; }
QPushButton#actionBtn:disabled { color:#b9b7b3; background:#faf9f7; border-color:#eeece8; }
QPushButton#actionBtn[primary="true"] { background:#111114; color:#ffffff; border-color:#111114; }
QPushButton#actionBtn[primary="true"]:hover { background:#26262b; }
QPushButton#stopBtn { font-family:"Segoe UI",sans-serif; font-size:12px; font-weight:700; color:#c22f3d; background:#ffffff; border:1px solid #efd0d4; border-radius:999px; padding:11px 20px; min-height:42px; }
QPushButton#stopBtn:hover { background:#fbf0f1; border-color:#e3b6bc; }
QPushButton#stopBtn:disabled { color:#c9b3b6; background:#faf9f7; border-color:#eeece8; }
QPushButton#linkBtn { background:transparent; border:none; color:#8a8a8e; font-size:11px; }
QPushButton#linkBtn:hover { color:#111114; }
QProgressBar { background:#eceae6; border:none; border-radius:8px; height:8px; text-align:center; }
QProgressBar::chunk { background:#111114; border-radius:8px; }
QTextEdit { font-family:Consolas,monospace; font-size:11px; color:#3a3a3d; background:rgba(250,249,247,0.85); border:1px solid #eceae6; border-radius:18px; padding:14px; }
QTableWidget { background:rgba(251,250,248,0.85); border:1px solid #eceae6; border-radius:16px; gridline-color:transparent; font-family:Consolas,monospace; font-size:11px; color:#333336; selection-background-color:#eceae6; }
QTableWidget::item { padding:8px; border-bottom:1px solid #f0eeea; }
QHeaderView::section { background:transparent; color:#8a8a8e; padding:10px; border:none; border-bottom:1px solid #eceae6; font-family:"Segoe UI",sans-serif; font-weight:700; font-size:10px; letter-spacing:1px; }
QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
QScrollBar::handle:vertical { background:#d8d6d2; border-radius:4px; min-height:30px; }
QScrollBar::handle:vertical:hover { background:#b9b7b3; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QLineEdit { font-family:Consolas,monospace; font-size:12px; color:#222226; background:#ffffff; border:1px solid #e4e2de; border-radius:12px; padding:10px 14px; selection-background-color:#d8d6d2; }
QLineEdit:focus { border:1px solid #111114; }
QPlainTextEdit { font-family:Consolas,monospace; font-size:12px; color:#222226; background:#ffffff; border:1px solid #e4e2de; border-radius:14px; padding:10px; }
QPlainTextEdit:focus { border:1px solid #111114; }
QComboBox { font-family:"Segoe UI",sans-serif; font-size:12px; color:#222226; background:#ffffff; border:1px solid #e4e2de; border-radius:12px; padding:9px 14px; }
QComboBox:hover { border-color:#b9b7b3; }
QComboBox QAbstractItemView { background:#ffffff; color:#222226; border:1px solid #e4e2de; selection-background-color:#f1efec; outline:none; }
QListWidget { background:rgba(255,255,255,0.85); border:1px solid #e4e2de; border-radius:14px; color:#333336; font-family:Consolas,monospace; font-size:12px; }
QListWidget::item { padding:8px 12px; border-bottom:1px solid #f0eeea; }
QListWidget::item:selected { background:#f1efec; color:#111114; }
QSlider::groove:horizontal { border:none; height:6px; background:#eceae6; border-radius:3px; }
QSlider::sub-page:horizontal { background:#111114; border-radius:3px; }
QSlider::handle:horizontal { background:#ffffff; border:2px solid #111114; width:14px; margin-top:-5px; margin-bottom:-5px; border-radius:8px; }
QMessageBox { background:#ffffff; }
QDialog { background:#f5f4f2; }
QScrollArea { background:transparent; border:none; }
"""
DARK_QSS = """
QMainWindow { background-color: #0b0b0d; }
QLabel { background: transparent; color: #e6e6ea; }
QWidget#sidebar { background: transparent; }
QStackedWidget { background: transparent; }
QPushButton#navBtn { font-family:"Segoe UI",sans-serif; font-size:13px; font-weight:600; color:#9a9aa2; background:transparent; border:none; border-radius:14px; padding:11px 14px; text-align:left; min-height:42px; }
QPushButton#navBtn:hover { color:#f5f5f7; background:rgba(255,255,255,0.06); }
QPushButton#navBtn[class="active"] { background:#f5f5f7; color:#111114; font-weight:700; }
QLabel#badge { background:rgba(255,255,255,0.08); color:#b9b9c0; border:none; border-radius:6px; font-size:8px; font-weight:800; padding:3px 6px; }
QLabel#h1 { color:#f5f5f7; font-family:"Segoe UI",sans-serif; font-size:30px; font-weight:800; }
QLabel#tTitle { color:#f5f5f7; font-family:"Segoe UI",sans-serif; font-size:14px; font-weight:700; }
QLabel#tText { color:#e6e6ea; font-family:"Segoe UI",sans-serif; font-size:12px; }
QLabel#tDim { color:#9a9aa2; font-family:"Segoe UI",sans-serif; font-size:12px; }
QLabel#tMono { color:#9a9aa2; font-family:Consolas,monospace; font-size:11px; }
QLabel#cText { color:#111114; }
QLabel#cDim { color:#6b6b70; }
QLabel#cBig { color:#111114; font-family:"Segoe UI",sans-serif; font-size:40px; font-weight:800; }
QFrame#cTile { background:#e4e4e8; border-radius:14px; }
QLabel#tOk { color:#6ee7a0; }
QLabel#tErr { color:#ff8f9a; }
QLabel#tWarn { color:#ffd166; }
QLabel#statValue { font-family:"Segoe UI",sans-serif; font-size:30px; font-weight:800; color:#f5f5f7; }
QLabel#statLabel { font-family:"Segoe UI",sans-serif; font-size:10px; color:#9a9aa2; letter-spacing:1px; }
QLabel#statusText { font-family:Consolas,monospace; font-size:11px; color:#9a9aa2; letter-spacing:2px; }
QPushButton#actionBtn { font-family:"Segoe UI",sans-serif; font-size:12px; font-weight:700; color:#f5f5f7; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.14); border-radius:999px; padding:11px 20px; min-height:42px; }
QPushButton#actionBtn:hover { background:rgba(255,255,255,0.10); border-color:rgba(255,255,255,0.25); }
QPushButton#actionBtn:disabled { color:#5a5a62; background:rgba(255,255,255,0.03); border-color:rgba(255,255,255,0.06); }
QPushButton#actionBtn[primary="true"] { background:#f5f5f7; color:#111114; border-color:#f5f5f7; }
QPushButton#actionBtn[primary="true"]:hover { background:#ffffff; }
QPushButton#stopBtn { font-family:"Segoe UI",sans-serif; font-size:12px; font-weight:700; color:#ff8f9a; background:rgba(255,143,154,0.08); border:1px solid rgba(255,143,154,0.35); border-radius:999px; padding:11px 20px; min-height:42px; }
QPushButton#stopBtn:hover { background:rgba(255,143,154,0.15); }
QPushButton#stopBtn:disabled { color:#6b5458; background:rgba(255,255,255,0.03); border-color:rgba(255,255,255,0.06); }
QPushButton#linkBtn { background:transparent; border:none; color:#9a9aa2; font-size:11px; }
QPushButton#linkBtn:hover { color:#f5f5f7; }
QProgressBar { background:rgba(255,255,255,0.10); border:none; border-radius:8px; height:8px; text-align:center; }
QProgressBar::chunk { background:#f5f5f7; border-radius:8px; }
QTextEdit { font-family:Consolas,monospace; font-size:11px; color:#d6d6dc; background:rgba(0,0,0,0.35); border:1px solid rgba(255,255,255,0.08); border-radius:18px; padding:14px; }
QTableWidget { background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.08); border-radius:16px; gridline-color:transparent; font-family:Consolas,monospace; font-size:11px; color:#d6d6dc; selection-background-color:rgba(255,255,255,0.10); }
QTableWidget::item { padding:8px; border-bottom:1px solid rgba(255,255,255,0.04); }
QHeaderView::section { background:transparent; color:#9a9aa2; padding:10px; border:none; border-bottom:1px solid rgba(255,255,255,0.08); font-family:"Segoe UI",sans-serif; font-weight:700; font-size:10px; letter-spacing:1px; }
QScrollBar:vertical { background:transparent; width:8px; margin:2px; }
QScrollBar::handle:vertical { background:rgba(255,255,255,0.20); border-radius:4px; min-height:30px; }
QScrollBar::handle:vertical:hover { background:rgba(255,255,255,0.35); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height:0; }
QLineEdit { font-family:Consolas,monospace; font-size:12px; color:#f5f5f7; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:12px; padding:10px 14px; selection-background-color:rgba(255,255,255,0.25); }
QLineEdit:focus { border:1px solid rgba(255,255,255,0.45); }
QPlainTextEdit { font-family:Consolas,monospace; font-size:12px; color:#f5f5f7; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:14px; padding:10px; }
QPlainTextEdit:focus { border:1px solid rgba(255,255,255,0.45); }
QComboBox { font-family:"Segoe UI",sans-serif; font-size:12px; color:#f5f5f7; background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.12); border-radius:12px; padding:9px 14px; }
QComboBox:hover { border-color:rgba(255,255,255,0.30); }
QComboBox QAbstractItemView { background:#1a1a1e; color:#e6e6ea; border:1px solid rgba(255,255,255,0.15); selection-background-color:rgba(255,255,255,0.10); outline:none; }
QListWidget { background:rgba(0,0,0,0.25); border:1px solid rgba(255,255,255,0.10); border-radius:14px; color:#d6d6dc; font-family:Consolas,monospace; font-size:12px; }
QListWidget::item { padding:8px 12px; border-bottom:1px solid rgba(255,255,255,0.04); }
QListWidget::item:selected { background:rgba(255,255,255,0.10); color:#f5f5f7; }
QSlider::groove:horizontal { border:none; height:6px; background:rgba(255,255,255,0.12); border-radius:3px; }
QSlider::sub-page:horizontal { background:#f5f5f7; border-radius:3px; }
QSlider::handle:horizontal { background:#111114; border:2px solid #f5f5f7; width:14px; margin-top:-5px; margin-bottom:-5px; border-radius:8px; }
QMessageBox { background:#1a1a1e; }
QDialog { background:#0b0b0d; }
QScrollArea { background:transparent; border:none; }
"""
THEMES = {
    "light": {
        "qss": LIGHT_QSS,
        "text": "#111114", "dim": "#8a8a8e", "on_active": "#ffffff", "on_primary": "#ffffff",
        "danger": "#c22f3d", "success": "#2f7d4f", "warn": "#b7791f",
        "log": {"info": "#55555a", "err": "#c22f3d", "warn": "#b7791f", "success": "#2f7d4f"},
        "card_tint": QColor(255, 255, 255, 150), "side_tint": QColor(255, 255, 255, 205),
        "card_border": QColor(0, 0, 0, 22),
        "contrast_bg": QColor(23, 23, 26, 240), "contrast_border": QColor(255, 255, 255, 14),
        "track": "#eceae6", "bar_top": "#111114", "bar_bot": "#8a8a8e", "idle": "#e3e1dd",
    },
    "dark": {
        "qss": DARK_QSS,
        "text": "#f5f5f7", "dim": "#9a9aa2", "on_active": "#111114", "on_primary": "#111114",
        "danger": "#ff8f9a", "success": "#6ee7a0", "warn": "#ffd166",
        "log": {"info": "#c9c9cf", "err": "#ff8f9a", "warn": "#ffd166", "success": "#6ee7a0"},
        "card_tint": QColor(26, 26, 30, 150), "side_tint": QColor(18, 18, 22, 205),
        "card_border": QColor(255, 255, 255, 26),
        "contrast_bg": QColor(245, 245, 247, 240), "contrast_border": QColor(0, 0, 0, 20),
        "track": "#2a2a30", "bar_top": "#f5f5f7", "bar_bot": "#8a8a8e", "idle": "#3a3a40",
    },
}
CURRENT_THEME = "light"
def T():
    return THEMES[CURRENT_THEME]

ACCENT_CYAN, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_RED = "#111114", "#6b6b6b", "#2f7d4f", "#c22f3d"
_EFFECT_REGISTRY = []

def neon_glow(widget, color="#000000", radius=30, alpha=90):
    try:
        eff = QGraphicsDropShadowEffect(widget)
        c = QColor("#000000"); c.setAlpha(max(12, min(alpha // 4, 45)))
        eff.setColor(c); eff.setBlurRadius(radius); eff.setOffset(0, 6)
        widget.setGraphicsEffect(eff)
        _EFFECT_REGISTRY.append(eff)
        return eff
    except Exception:
        return None

def pop_animate(label):
    try:
        orig = label.styleSheet()
        label.setStyleSheet(orig + " background: rgba(128,128,128,0.16);")
        t = QTimer(label); t.setSingleShot(True)
        t.timeout.connect(lambda w=label, s=orig: w.setStyleSheet(s))
        t.start(220)
        _EFFECT_REGISTRY.append(t)
    except Exception:
        pass

def recolor(w, object_name):
    try:
        w.setObjectName(object_name)
        w.style().unpolish(w); w.style().polish(w)
    except Exception:
        pass

# =====================================================================
# ВЕКТОРНЫЕ ИКОНКИ-КАРТИНКИ
# =====================================================================
if QT_BINDING:
    def _ic_dashboard(p, c):
        p.drawRoundedRect(3, 3, 8, 8, 2, 2); p.drawRoundedRect(13, 3, 8, 8, 2, 2)
        p.drawRoundedRect(3, 13, 8, 8, 2, 2); p.drawRoundedRect(13, 13, 8, 8, 2, 2)
    def _ic_terminal(p, c):
        p.drawRoundedRect(2.5, 4, 19, 16, 3, 3)
        p.drawLine(6, 9, 9, 12); p.drawLine(9, 12, 6, 15); p.drawLine(11.5, 15, 17, 15)
    def _ic_infinity(p, c):
        p.drawEllipse(3.5, 7.5, 9, 9); p.drawEllipse(11.5, 7.5, 9, 9)
    def _ic_shield(p, c):
        path = QPainterPath(); path.moveTo(12, 3); path.lineTo(19, 5.5); path.lineTo(19, 11)
        path.quadTo(19, 17, 12, 21); path.quadTo(5, 17, 5, 11); path.lineTo(5, 5.5); path.closeSubpath()
        p.drawPath(path); p.drawLine(9, 11.5, 11, 14); p.drawLine(11, 14, 15, 9.5)
    def _ic_mail(p, c):
        p.drawRoundedRect(3, 5, 18, 14, 2, 2); p.drawLine(3.5, 7, 12, 13); p.drawLine(12, 13, 20.5, 7)
    def _ic_vault(p, c):
        p.drawEllipse(8.8, 4.3, 6.4, 6.4); p.drawArc(4, 12.5, 10, 8, 0, 180 * 16)
        p.drawEllipse(15.5, 6.5, 5, 5); p.drawArc(13, 14, 8, 7, 0, 180 * 16)
    def _ic_phones(p, c):
        pw = p.pen(); pw.setWidthF(2.2); p.setPen(pw)
        p.drawArc(4, 5, 16, 16, 0, 180 * 16)
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(c)
        p.drawRoundedRect(3, 12, 4.5, 8, 2, 2); p.drawRoundedRect(16.5, 12, 4.5, 8, 2, 2)
    def _ic_chart(p, c):
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(c)
        p.drawRoundedRect(4.5, 12, 3.5, 8, 1, 1); p.drawRoundedRect(10.2, 8, 3.5, 12, 1, 1); p.drawRoundedRect(16, 4, 3.5, 16, 1, 1)
    def _ic_bolt(p, c):
        path = QPainterPath(); path.moveTo(13, 2); path.lineTo(6, 13); path.lineTo(11, 13)
        path.lineTo(10, 22); path.lineTo(18, 10); path.lineTo(12, 10); path.closeSubpath()
        p.fillPath(path, c)
    def _ic_play(p, c):
        path = QPainterPath(); path.moveTo(8, 5); path.lineTo(19, 12); path.lineTo(8, 19); path.closeSubpath()
        p.fillPath(path, c)
    def _ic_stop(p, c):
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); p.drawRoundedRect(7, 7, 10, 10, 2, 2)
    def _ic_trash(p, c):
        p.drawLine(4, 6.5, 20, 6.5); p.drawRoundedRect(6.5, 6.5, 11, 14, 2, 2)
        p.drawLine(10, 10.5, 10, 17); p.drawLine(14, 10.5, 14, 17); p.drawRoundedRect(9.5, 3.5, 5, 3, 1, 1)
    def _ic_refresh(p, c):
        p.drawArc(4.5, 4.5, 15, 15, 45 * 16, 290 * 16)
        path = QPainterPath(); path.moveTo(17.5, 2.8); path.lineTo(21.2, 6.2); path.lineTo(16.6, 8.4); path.closeSubpath()
        p.fillPath(path, c)
    def _ic_send(p, c):
        path = QPainterPath(); path.moveTo(3, 11.5); path.lineTo(21, 3.5); path.lineTo(14.5, 21)
        path.lineTo(11.5, 14); path.closeSubpath(); p.drawPath(path); p.drawLine(11.5, 14, 21, 3.5)
    def _ic_key(p, c):
        p.drawEllipse(4.5, 8.5, 7, 7); p.drawLine(11.5, 12, 20.5, 12)
        p.drawLine(17.5, 12, 17.5, 15.5); p.drawLine(20.5, 12, 20.5, 15.5)
    def _ic_doc(p, c):
        p.drawRoundedRect(6, 3, 12, 18, 2, 2)
        p.drawLine(9, 8.5, 15, 8.5); p.drawLine(9, 12, 15, 12); p.drawLine(9, 15.5, 13, 15.5)
    def _ic_download(p, c):
        p.drawLine(12, 4, 12, 14); p.drawLine(8, 10.5, 12, 14.5); p.drawLine(12, 14.5, 16, 10.5); p.drawLine(5, 19, 19, 19)
    def _ic_search(p, c):
        p.drawEllipse(4.5, 4.5, 11, 11); p.drawLine(13.5, 13.5, 20, 20)
    def _ic_volume(p, c):
        path = QPainterPath(); path.moveTo(4, 9.5); path.lineTo(8, 9.5); path.lineTo(12.5, 5)
        path.lineTo(12.5, 19); path.lineTo(8, 14.5); path.lineTo(4, 14.5); path.closeSubpath()
        p.fillPath(path, c)
        p.drawArc(14.5, 9.5, 5, 5, -45 * 16, 90 * 16); p.drawArc(16.5, 7.5, 9, 9, -45 * 16, 90 * 16)
    def _ic_sun(p, c):
        p.drawEllipse(8.5, 8.5, 7, 7)
        for i in range(8):
            a = i * math.pi / 4
            p.drawLine(12 + 9.2 * math.cos(a), 12 + 9.2 * math.sin(a), 12 + 11.4 * math.cos(a), 12 + 11.4 * math.sin(a))
    def _ic_moon(p, c):
        p1 = QPainterPath(); p1.addEllipse(6, 6, 14, 14)
        p2 = QPainterPath(); p2.addEllipse(11, 3.5, 14, 14)
        p.fillPath(p1.subtracted(p2), c)
    def _ic_db(p, c):
        p.drawEllipse(4.5, 3.5, 15, 6)
        p.drawLine(4.5, 6.5, 4.5, 17.5); p.drawLine(19.5, 6.5, 19.5, 17.5)
        p.drawArc(4.5, 9, 15, 6, 180 * 16, 180 * 16); p.drawArc(4.5, 14.5, 15, 6, 180 * 16, 180 * 16)
    def _ic_globe(p, c):
        p.drawEllipse(4, 4, 16, 16); p.drawEllipse(8.5, 4, 7, 16); p.drawLine(4, 12, 20, 12)
    def _ic_save(p, c):
        p.drawRoundedRect(4, 4, 16, 16, 2, 2); p.drawLine(8, 4, 8, 9); p.drawLine(16, 4, 16, 9)
        p.drawLine(8, 9, 16, 9); p.drawRoundedRect(8, 13, 8, 7, 1, 1)
    def _ic_music(p, c):
        p.setPen(Qt.PenStyle.NoPen); p.setBrush(c); p.drawEllipse(5.5, 16, 5, 5)
        pw = p.pen(); pw.setWidthF(2.0); p.setPen(pw)
        p.drawLine(10.5, 18.5, 10.5, 5.5); p.drawLine(10.5, 5.5, 17.5, 4.2); p.drawLine(17.5, 4.2, 17.5, 15)
        p.setPen(Qt.PenStyle.NoPen); p.drawEllipse(12.5, 15, 5, 5)
    ICON_SHAPES = {
        "dashboard": _ic_dashboard, "terminal": _ic_terminal, "infinity": _ic_infinity,
        "shield": _ic_shield, "mail": _ic_mail, "vault": _ic_vault, "phones": _ic_phones,
        "chart": _ic_chart, "bolt": _ic_bolt, "play": _ic_play, "stop": _ic_stop,
        "trash": _ic_trash, "refresh": _ic_refresh, "send": _ic_send, "key": _ic_key,
        "doc": _ic_doc, "download": _ic_download, "search": _ic_search, "volume": _ic_volume,
        "sun": _ic_sun, "moon": _ic_moon, "db": _ic_db, "globe": _ic_globe, "save": _ic_save,
        "music": _ic_music,
    }
    class IconLib:
        _cache = {}
        @staticmethod
        def get(name, color, size=20):
            key = (name, color, size)
            if key in IconLib._cache:
                return IconLib._cache[key]
            ic = QIcon()
            try:
                pm = QPixmap(size, size); pm.fill(Qt.GlobalColor.transparent)
                p = QPainter(pm); p.setRenderHint(QPainter.RenderHint.Antialiasing)
                p.scale(size / 24.0, size / 24.0)
                pen = QPen(QColor(color)); pen.setWidthF(1.8)
                pen.setCapStyle(Qt.PenCapStyle.RoundCap); pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
                p.setPen(pen); p.setBrush(Qt.BrushStyle.NoBrush)
                fn = ICON_SHAPES.get(name)
                if fn:
                    fn(p, QColor(color))
                p.end()
                ic = QIcon(pm)
            except Exception:
                pass
            IconLib._cache[key] = ic
            return ic

    def glass_paint(widget, painter, radius, tint, border_color, border_w=1.0):
        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            r = QRectF(widget.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
            path = QPainterPath(); path.addRoundedRect(r, radius, radius)
            win = widget.window()
            cache = getattr(win, "_blur_cache", None)
            if cache is not None and not cache.isNull():
                top = widget.mapTo(win, QPoint(0, 0))
                region = QRect(top.x(), top.y(), widget.width(), widget.height()).intersected(cache.rect())
                if not region.isNull():
                    img = cache.copy(region).toImage()
                    painter.save(); painter.setClipPath(path)
                    painter.drawImage(QRectF(region.x() - top.x(), region.y() - top.y(), region.width(), region.height()), img, QRectF(img.rect()))
                    painter.restore()
            painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(tint)
            painter.drawRoundedRect(r, radius, radius)
            painter.setPen(QPen(border_color, border_w)); painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(r, radius, radius)
        except Exception:
            pass

    class PulseDot(QWidget):
        def __init__(self, color="#c9c7c3", parent=None):
            super().__init__(parent)
            self.setFixedSize(10, 10)
            self.color = QColor(color)
            self._phase = 0.0
            self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(60)
        def set_color(self, hex_color):
            try:
                self.color = QColor(hex_color); self.update()
            except Exception:
                pass
        def _tick(self):
            self._phase += 0.10; self.update()
        def paintEvent(self, event):
            try:
                p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
                pulse = (math.sin(self._phase) + 1) / 2.0
                halo = QColor(self.color); halo.setAlpha(int(50 * pulse))
                p.setPen(Qt.PenStyle.NoPen); p.setBrush(halo); p.drawEllipse(QRectF(0, 0, 10, 10))
                p.setBrush(QColor(self.color)); p.drawEllipse(QRectF(2.5, 2.5, 5, 5))
                p.end()
            except Exception:
                pass

    class RainbowLine(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedHeight(2)
        def paintEvent(self, event):
            try:
                p = QPainter(self)
                g = QLinearGradient(0, 0, self.width(), 0)
                base = QColor(T()["text"]); base.setAlpha(220)
                mid = QColor(T()["dim"]); mid.setAlpha(90)
                g.setColorAt(0.0, base); g.setColorAt(0.5, mid); g.setColorAt(1.0, QColor(255, 255, 255, 0))
                p.fillRect(self.rect(), QBrush(g)); p.end()
            except Exception:
                pass

    class AccentCard(QWidget):
        def __init__(self, accent=ACCENT_PURPLE, parent=None, dark=False):
            super().__init__(parent)
            self.setObjectName("card")
            self.accent = accent
            self.dark = dark
            self._hovered = False
        def paintEvent(self, event):
            try:
                p = QPainter(self)
                if self.dark:
                    p.setRenderHint(QPainter.RenderHint.Antialiasing)
                    r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
                    p.setPen(Qt.PenStyle.NoPen); p.setBrush(T()["contrast_bg"])
                    p.drawRoundedRect(r, 24, 24)
                    p.setPen(QPen(T()["contrast_border"], 1)); p.setBrush(Qt.BrushStyle.NoBrush)
                    p.drawRoundedRect(r, 24, 24)
                else:
                    tint = QColor(T()["card_tint"])
                    if self._hovered:
                        tint.setAlpha(min(255, tint.alpha() + 25))
                    glass_paint(self, p, 24, tint, T()["card_border"])
                p.end()
            except Exception:
                pass
        def enterEvent(self, event):
            self._hovered = True; self.update(); super().enterEvent(event)
        def leaveEvent(self, event):
            self._hovered = False; self.update(); super().leaveEvent(event)

    class GlowButton(QPushButton):
        def __init__(self, text, accent=ACCENT_PURPLE, danger=False, parent=None, icon=None):
            super().__init__(text, parent)
            self.setObjectName("stopBtn" if danger else "actionBtn")
            self.setProperty("class", "actionBtn")
            self.accent = ACCENT_RED if danger else accent
            self.danger = danger
            self.primary = bool(not danger and accent in (ACCENT_CYAN, ACCENT_GREEN))
            self.setProperty("primary", self.primary)
            self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self._icon_name = icon
            self.refresh_icon()
        def refresh_icon(self):
            try:
                if not self._icon_name:
                    return
                if self.danger:
                    col = T()["danger"]
                elif self.primary:
                    col = T()["on_primary"]
                else:
                    col = T()["text"]
                self.setIcon(IconLib.get(self._icon_name, col, 17))
                self.setIconSize(QSize(17, 17))
            except Exception:
                pass

    class AnimatedProgressBar(QProgressBar):
        def __init__(self, parent=None):
            super().__init__(parent)

    class OrbBackground(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.theme = "light"
            self.orbs = [
                {"x": 200, "y": 150, "r": 260, "vx": 0.3, "vy": 0.2, "phase": 0.0},
                {"x": 800, "y": 400, "r": 300, "vx": -0.2, "vy": 0.3, "phase": 1.5},
                {"x": 500, "y": 600, "r": 220, "vx": 0.2, "vy": -0.2, "phase": 3.0},
                {"x": 1200, "y": 200, "r": 280, "vx": -0.3, "vy": 0.1, "phase": 4.5},
            ]
            self.particles = []
            for _ in range(45):
                self.particles.append({
                    "x": random.uniform(0, 1920), "y": random.uniform(0, 1080),
                    "vx": random.uniform(-0.25, 0.25), "vy": random.uniform(-0.25, 0.25),
                    "s": random.uniform(1.0, 2.6), "a": random.randint(14, 40),
                })
            self._tick_count = 0
            self.set_theme(CURRENT_THEME)
            self.timer = QTimer(self); self.timer.timeout.connect(self.animate); self.timer.start(60)
        def set_theme(self, name):
            self.theme = name
            if name == "light":
                self.base = QColor(245, 244, 242)
                self.orb_cols = [QColor(255, 255, 255, 150), QColor(232, 230, 226, 130), QColor(214, 212, 208, 100), QColor(248, 247, 245, 140)]
                self.grid_col = QColor(0, 0, 0, 6)
                self.dot_mul = 1.0
            else:
                self.base = QColor(11, 11, 13)
                self.orb_cols = [QColor(255, 255, 255, 26), QColor(210, 210, 220, 20), QColor(170, 170, 185, 16), QColor(235, 235, 245, 22)]
                self.grid_col = QColor(255, 255, 255, 7)
                self.dot_mul = 0.8
        def animate(self):
            self._tick_count += 1
            for orb in self.orbs:
                orb["x"] += orb["vx"]; orb["y"] += orb["vy"]; orb["phase"] += 0.04
                if orb["x"] < -orb["r"] or orb["x"] > self.width() + orb["r"]: orb["vx"] *= -1
                if orb["y"] < -orb["r"] or orb["y"] > self.height() + orb["r"]: orb["vy"] *= -1
            w, h = max(self.width(), 100), max(self.height(), 100)
            for p in self.particles:
                p["x"] += p["vx"]; p["y"] += p["vy"]
                if p["x"] < 0: p["x"] = w
                if p["x"] > w: p["x"] = 0
                if p["y"] < 0: p["y"] = h
                if p["y"] > h: p["y"] = 0
            self.update()
        def paintEvent(self, event):
            try:
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.fillRect(self.rect(), self.base)
                for i, orb in enumerate(self.orbs):
                    r = orb["r"] * (1.0 + 0.06 * math.sin(orb["phase"]))
                    gradient = QRadialGradient(orb["x"], orb["y"], r)
                    gradient.setColorAt(0, self.orb_cols[i % len(self.orb_cols)])
                    gradient.setColorAt(1, QColor(0, 0, 0, 0))
                    painter.setBrush(QBrush(gradient)); painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawEllipse(int(orb["x"] - r), int(orb["y"] - r), int(r * 2), int(r * 2))
                grid_pen = QPen(self.grid_col); grid_pen.setWidth(1); painter.setPen(grid_pen)
                step = 60 if (self.width() * self.height()) < 2_500_000 else 120
                for gx in range(0, self.width(), step):
                    painter.drawLine(gx, 0, gx, self.height())
                for gy in range(0, self.height(), step):
                    painter.drawLine(0, gy, self.width(), gy)
                for p in self.particles:
                    dot = QColor(T()["text"]); dot.setAlpha(int(p["a"] * self.dot_mul))
                    painter.setPen(dot); painter.drawPoint(int(p["x"]), int(p["y"]))
                if not hasattr(self, "_lines_cache") or self._tick_count % 30 == 0:
                    pairs = []
                    for i in range(len(self.particles)):
                        for j in range(i + 1, len(self.particles)):
                            dx = self.particles[i]["x"] - self.particles[j]["x"]
                            dy = self.particles[i]["y"] - self.particles[j]["y"]
                            d2 = dx * dx + dy * dy
                            if d2 < 180 * 180:
                                pairs.append((i, j, int(12 * (1 - d2 / (180 * 180)))))
                    self._lines_cache = pairs
                for i, j, alpha in self._lines_cache:
                    lc = QColor(T()["dim"]); lc.setAlpha(alpha)
                    painter.setPen(QPen(lc))
                    painter.drawLine(QPointF(self.particles[i]["x"], self.particles[i]["y"]),
                                     QPointF(self.particles[j]["x"], self.particles[j]["y"]))
                painter.end()
            except Exception:
                pass

    class AnimatedLogo(QWidget):
        def __init__(self, text="MORPHH", parent=None):
            super().__init__(parent)
            self.text = text
            self.t = 0.0
            self.setFont(QFont("Segoe UI", 21, QFont.Weight.Black))
            self.setFixedHeight(58); self.setMinimumWidth(190)
            self.timer = QTimer(self); self.timer.timeout.connect(self._tick); self.timer.start(50)
        def _tick(self):
            self.t += 0.09; self.update()
        def paintEvent(self, event):
            try:
                painter = QPainter(self)
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
                fm = painter.fontMetrics()
                total_w = sum(fm.horizontalAdvance(ch) for ch in self.text)
                x = (self.width() - total_w) / 2.0
                cy = self.height() / 2.0
                painter.setPen(QColor(T()["text"]))
                for i, ch in enumerate(self.text):
                    wave = math.sin(self.t * 2.2 + i * 0.9) * 1.2
                    painter.drawText(QPointF(x, cy + fm.ascent() / 2 + wave), ch)
                    x += fm.horizontalAdvance(ch)
                painter.end()
            except Exception:
                pass

    class EqualizerVisualizer(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedHeight(54)
            self.is_active = False
            self.bar_count = 32
            self.heights = [6.0] * self.bar_count
            self._timer = QTimer(self); self._timer.timeout.connect(self._tick); self._timer.start(55)
        def set_active(self, active: bool):
            self.is_active = active; self.update()
        def _tick(self):
            if self.is_active:
                for i in range(self.bar_count):
                    self.heights[i] += (random.uniform(8.0, 48.0) - self.heights[i]) * 0.45
            else:
                for i in range(self.bar_count):
                    self.heights[i] += (5.0 - self.heights[i]) * 0.2
            self.update()
        def paintEvent(self, event):
            try:
                painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                w, h = self.width(), self.height()
                bar_w = max(2.0, (w - (self.bar_count * 4)) / self.bar_count)
                for i in range(self.bar_count):
                    bx = i * (bar_w + 4) + 2
                    bh = self.heights[i]; by = h - bh - 3
                    grad = QLinearGradient(bx, by, bx, by + bh)
                    if self.is_active:
                        grad.setColorAt(0.0, QColor(T()["bar_top"])); grad.setColorAt(1.0, QColor(T()["bar_bot"]))
                    else:
                        grad.setColorAt(0.0, QColor(T()["idle"])); grad.setColorAt(1.0, QColor(T()["idle"]))
                    painter.setPen(Qt.PenStyle.NoPen); painter.setBrush(QBrush(grad))
                    painter.drawRoundedRect(QRectF(bx, by, bar_w, bh), 2.5, 2.5)
                painter.end()
            except Exception:
                pass

    class RingGauge(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._value = 0
            self.setFixedSize(140, 140)
        def setValue(self, v):
            try:
                self._value = max(0, min(100, int(v))); self.update()
            except Exception:
                pass
        def value(self):
            return self._value
        def paintEvent(self, event):
            try:
                p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
                rect = QRectF(10, 10, self.width() - 20, self.height() - 20)
                p.setPen(QPen(QColor(T()["track"]), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                p.drawEllipse(rect)
                if self._value > 0:
                    p.setPen(QPen(QColor(T()["text"]), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
                    p.drawArc(rect, 90 * 16, -int(self._value * 3.6 * 16))
                p.setPen(QColor(T()["text"])); p.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
                p.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, f"{self._value}%")
                p.end()
            except Exception:
                pass

class EmailValidator:
    TRAP_TOKENS = {
        'spam', 'spams', 'abuse', 'junk', 'bad', 'trap', 'traps', 'honeypot',
        'blackhole', 'block', 'blocked', 'deny', 'banned', 'complaints',
        'deleteme', 'discard', 'tarpit', 'nosuchuser', 'nowhere', 'invalid',
        'spamtrap', 'honeypot1', 'honeypot2', 'sinkhole', 'mailtrap'
    }
    ROLE_PREFIXES = {
        'info', 'contact', 'office', 'admin', 'support', 'help', 'sales',
        'hello', 'mail', 'email', 'team', 'press', 'jobs', 'hr', 'privacy',
        'security', 'postmaster', 'webmaster', 'root', 'noreply', 'no-reply'
    }
    DISPOSABLE_DOMAINS = {
        'mail.tm', 'mailtemp.org', 'tempmail.com', '10minutemail.com',
        'yopmail.com', 'trashmail.com', 'guerrillamail.com', 'sharklasers.com',
        'dispostable.com', 'mailinator.com', 'getnada.com', 'fakemailgenerator.com',
        'tempr.email', 'mohmal.com', 'emailondeck.com', 'inboxbear.com'
    }
    def __init__(self):
        self._mx_cache = {}; self._lock = threading.Lock()
    def get_mx(self, domain):
        with self._lock:
            if domain in self._mx_cache:
                return self._mx_cache[domain]
        hosts = None
        try:
            if dns is not None:
                try:
                    ans = dns.resolver.resolve(domain, 'MX', lifetime=3)
                    hosts = [str(r.exchange).rstrip('.').lower() for r in ans]
                except Exception:
                    hosts = None
            if not hosts:
                socket.setdefaulttimeout(3)
                socket.getaddrinfo(domain, None)
                hosts = [domain]
        except Exception:
            hosts = None
        with self._lock:
            self._mx_cache[domain] = hosts
        return hosts
    def validate(self, email: str) -> tuple:
        email = email.strip().lower()
        country = detect_country(email)
        last_active = estimate_last_active(email)
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,63}$", email):
            return ('INVALID', 0, 'Битый синтаксис email', country, last_active)
        local, domain = email.rsplit('@', 1)
        if domain in self.DISPOSABLE_DOMAINS:
            return ('INVALID', 10, 'Одноразовый временный сервис', country, last_active)
        parts = re.split(r'[._+\-]', local)
        if any(p in self.TRAP_TOKENS for p in parts) or any(t in local for t in ('honeypot', 'spamtrap', 'blackhole')):
            return ('TRAP', 0, 'ОБНАРУЖЕНА СПАМ-ЛОВУШКА (Honeypot Trap)', country, last_active)
        mxs = self.get_mx(domain)
        if not mxs:
            return ('INVALID', 0, 'MX сервер не принимает входящую почту', country, last_active)
        if parts[0] in self.ROLE_PREFIXES:
            return ('RISKY', 60, f'Служебный ящик ({parts[0]}@), а не личный', country, last_active)
        if domain in PERSONAL_PROVIDERS:
            return ('SAFE', 95, 'Настоящий личный ящик человека', country, last_active)
        return ('SAFE', 88, 'Живой домен, синтаксис чист', country, last_active)

class MailerAccountManager:
    @staticmethod
    def get_file_path():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.txt")
    @classmethod
    def load_accounts(cls) -> list:
        path = cls.get_file_path()
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("# email:password (по одному на строку)\n")
                    f.write("sender.demo@gmail.com:app_pass_abcd1234\n")
                    f.write("outreach.lead@yandex.ru:secret_token_998\n")
            except Exception:
                pass
        accounts = []
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and ":" in line:
                        p = line.split(":", 1)
                        if "@" in p[0]:
                            accounts.append({"email": p[0].strip(), "password": p[1].strip(), "provider": p[0].strip().split("@")[-1].upper()})
        except Exception:
            pass
        return accounts

class SmtpSender:
    PROVIDERS = {
        'gmail.com': ('smtp.gmail.com', 587, 'starttls'),
        'googlemail.com': ('smtp.gmail.com', 587, 'starttls'),
        'yandex.ru': ('smtp.yandex.ru', 465, 'ssl'),
        'yandex.com': ('smtp.yandex.ru', 465, 'ssl'),
        'mail.ru': ('smtp.mail.ru', 465, 'ssl'),
        'bk.ru': ('smtp.mail.ru', 465, 'ssl'),
        'inbox.ru': ('smtp.mail.ru', 465, 'ssl'),
        'list.ru': ('smtp.mail.ru', 465, 'ssl'),
        'rambler.ru': ('smtp.rambler.ru', 465, 'ssl'),
        'outlook.com': ('smtp-mail.outlook.com', 587, 'starttls'),
        'yahoo.com': ('smtp.mail.yahoo.com', 465, 'ssl'),
        'icloud.com': ('smtp.mail.me.com', 587, 'starttls')
    }
    def __init__(self, email_addr: str, password: str, log_fn=None):
        self.email_addr = email_addr.strip(); self.password = password.strip()
        self.log = log_fn or (lambda m, t="info": None)
        self.smtp = None
    def connect(self):
        domain = self.email_addr.rsplit('@', 1)[-1].lower()
        cfg = self.PROVIDERS.get(domain, (f"smtp.{domain}", 587, 'starttls'))
        host, port, sec = cfg
        self.log(f"Подключение к {host}:{port} [{sec.upper()}]...", "info")
        try:
            if sec == "ssl":
                ctx = _ssl_mod.create_default_context()
                self.smtp = smtplib.SMTP_SSL(host, port, timeout=16, context=ctx)
            else:
                self.smtp = smtplib.SMTP(host, port, timeout=16)
                self.smtp.ehlo(); self.smtp.starttls(context=_ssl_mod.create_default_context()); self.smtp.ehlo()
            self.smtp.login(self.email_addr, self.password)
            self.log(f"SMTP авторизация подтверждена для {self.email_addr}", "success")
            return True
        except Exception as e:
            raise RuntimeError(f"Сбой авторизации SMTP: {e}")
    def send(self, to_email: str, subject: str, body: str):
        if not self.smtp:
            self.connect()
        msg = MIMEMultipart("alternative")
        sender_domain = self.email_addr.rsplit('@', 1)[-1]
        msg["From"] = formataddr(("", self.email_addr))
        msg["To"] = formataddr(("", to_email))
        msg["Subject"] = subject
        msg["Date"] = _dt.datetime.now(_dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        msg["Message-ID"] = make_msgid(domain=sender_domain)
        msg["X-Mailer"] = "MorphhOSINT/2.0-Pro"
        msg.attach(MIMEText(body, "plain", "utf-8"))
        html = "<html><body>" + "".join(f"<p>{line}</p>" for line in body.splitlines()) + "</body></html>"
        msg.attach(MIMEText(html, "html", "utf-8"))
        self.smtp.sendmail(self.email_addr, [to_email], msg.as_string())
    def close(self):
        try:
            if self.smtp: self.smtp.quit()
        except Exception:
            pass
        self.smtp = None

class LoFiRadio(QObject):
    STATIONS = [
        {"name": "FluxFM Chillhop & Study Beats", "genre": "CHILLHOP", "bitrate": "320kbps MP3", "url": "https://streams.fluxfm.de/chillhop/mp3-320/audio.mp3", "icon": "music"},
        {"name": "DEF CON Radio (Cyber Chill)", "genre": "CYBERPUNK", "bitrate": "128kbps MP3", "url": "https://ice2.somafm.com/defcon-128-mp3", "icon": "bolt"},
        {"name": "Groove Salad (Downtempo Beats)", "genre": "DOWNTEMPO", "bitrate": "128kbps MP3", "url": "https://ice1.somafm.com/groovesalad-128-mp3", "icon": "music"},
        {"name": "Nightwave Plaza (Vaporwave & Synth)", "genre": "VAPORWAVE", "bitrate": "128kbps MP3", "url": "https://radio.plaza.one/mp3", "icon": "globe"},
        {"name": "Drone Zone (Deep Ambient Space)", "genre": "AMBIENT", "bitrate": "128kbps MP3", "url": "https://ice1.somafm.com/dronezone-128-mp3", "icon": "moon"},
        {"name": "Secret Agent (Spy Retro Chill)", "genre": "SPY CHILL", "bitrate": "128kbps MP3", "url": "https://ice1.somafm.com/secretagent-128-mp3", "icon": "search"},
    ]
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.is_playing = False
        self.player = None; self.audio_output = None
        if HAS_MULTIMEDIA:
            try:
                self.player = QMediaPlayer(); self.audio_output = QAudioOutput()
                self.player.setAudioOutput(self.audio_output); self.audio_output.setVolume(0.75)
                self.player.errorOccurred.connect(self._on_error)
            except Exception:
                pass
    def _on_error(self, *args):
        self.is_playing = False
        try:
            self.signals.radio_status_signal.emit("ОШИБКА ПОТОКА (станция недоступна)", False)
        except Exception:
            pass
    def play(self, idx: int = 0):
        if idx < 0 or idx >= len(self.STATIONS): idx = 0
        st = self.STATIONS[idx]
        if HAS_MULTIMEDIA and self.player:
            try:
                self.player.stop(); self.player.setSource(QUrl(st["url"])); self.player.play()
            except Exception:
                pass
        self.is_playing = True
        self.signals.radio_status_signal.emit(st["name"], True)
    def stop(self):
        if HAS_MULTIMEDIA and self.player:
            try: self.player.stop()
            except Exception: pass
        self.is_playing = False
        self.signals.radio_status_signal.emit("РАДИО ВЫКЛ", False)
    def set_volume(self, val: int):
        if HAS_MULTIMEDIA and self.audio_output:
            try: self.audio_output.setVolume(val / 100.0)
            except Exception: pass

if QT_BINDING:
    class Sidebar(QWidget):
        NAV = [
            ("dashboard", "Dashboard", "", "dashboard"),
            ("parser", "Parser & Logs", "", "terminal"),
            ("auto", "Infinite Engine", "CRAWL", "infinity"),
            ("validator", "Validator", "TRAP", "shield"),
            ("mailer", "Smart Mailer", "SMTP", "mail"),
            ("accounts", "Accounts Vault", "AUTH", "vault"),
            ("radio", "Lo-Fi Radio", "24/7", "phones"),
            ("stats", "Database & Stats", "SQL", "db"),
            ("osint", "OSINT Tools", "NET", "bolt"),
        ]
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("sidebar")
            self.setFixedWidth(252)
            layout = QVBoxLayout(self)
            layout.setContentsMargins(16, 26, 16, 22); layout.setSpacing(4)
            layout.addWidget(AnimatedLogo("MORPHH"))
            sub = QLabel("ALLPARS V2.0 PRO")
            sub.setObjectName("tMono")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sub)
            layout.addSpacing(14)
            self.buttons = {}; self.icons = {}
            for key, text, badge, icon in self.NAV:
                self.icons[key] = icon
                btn_w = QWidget()
                b_layout = QHBoxLayout(btn_w)
                b_layout.setContentsMargins(0, 0, 0, 0); b_layout.setSpacing(8)
                btn = QPushButton(text)
                btn.setObjectName("navBtn")
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.clicked.connect(lambda checked, k=key: self.on_nav(k))
                b_layout.addWidget(btn, 1)
                if badge:
                    b_lbl = QLabel(badge); b_lbl.setObjectName("badge")
                    b_layout.addWidget(b_lbl)
                layout.addWidget(btn_w)
                self.buttons[key] = btn
            layout.addStretch()
            self.btn_theme = QPushButton("Тёмная тема")
            self.btn_theme.setObjectName("navBtn")
            self.btn_theme.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            self.btn_theme.clicked.connect(self.toggle_theme)
            layout.addWidget(self.btn_theme)
            radio_row = QHBoxLayout(); radio_row.setSpacing(8)
            self.radio_dot = PulseDot("#c9c7c3"); radio_row.addWidget(self.radio_dot)
            self.radio_lbl = QLabel("RADIO OFF"); self.radio_lbl.setObjectName("tMono")
            radio_row.addWidget(self.radio_lbl); radio_row.addStretch()
            rw = QWidget(); rw.setLayout(radio_row); layout.addWidget(rw)
            engine_row = QHBoxLayout(); engine_row.setSpacing(8)
            self.engine_dot = PulseDot("#c9c7c3"); engine_row.addWidget(self.engine_dot)
            self.engine_lbl = QLabel("ENGINE IDLE"); self.engine_lbl.setObjectName("tMono")
            engine_row.addWidget(self.engine_lbl); engine_row.addStretch()
            ew = QWidget(); ew.setLayout(engine_row); layout.addWidget(ew)
            ver = QLabel("v2.0 PRO • Clean Glass Edition")
            ver.setObjectName("tMono"); ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(ver)
            self.active_key = None
            self.refresh_icons()
            self.on_nav("dashboard")
        def toggle_theme(self):
            try:
                win = self.window()
                target = "dark" if CURRENT_THEME == "light" else "light"
                if hasattr(win, "apply_theme"):
                    win.apply_theme(target)
            except Exception:
                pass
        def refresh_icons(self):
            try:
                for key, btn in self.buttons.items():
                    active = (key == self.active_key)
                    col = T()["on_active"] if active else T()["dim"]
                    btn.setIcon(IconLib.get(self.icons[key], col, 19))
                    btn.setIconSize(QSize(19, 19))
                self.btn_theme.setIcon(IconLib.get("moon" if CURRENT_THEME == "light" else "sun", T()["dim"], 18))
                self.btn_theme.setIconSize(QSize(18, 18))
                self.btn_theme.setText("Тёмная тема" if CURRENT_THEME == "light" else "Светлая тема")
            except Exception:
                pass
        def set_engine_state(self, running):
            try:
                self.engine_dot.set_color(T()["text"] if running else "#c9c7c3")
                self.engine_lbl.setText("ENGINE ACTIVE" if running else "ENGINE IDLE")
                recolor(self.engine_lbl, "tText" if running else "tMono")
            except Exception:
                pass
        def set_radio_state(self, text, is_on):
            try:
                self.radio_dot.set_color(T()["text"] if is_on else "#c9c7c3")
                self.radio_lbl.setText("RADIO ACTIVE" if is_on else "RADIO OFF")
                recolor(self.radio_lbl, "tText" if is_on else "tMono")
            except Exception:
                pass
        def on_nav(self, key):
            try:
                if self.active_key and self.active_key in self.buttons:
                    old = self.buttons[self.active_key]
                    old.setProperty("class", "")
                    old.style().unpolish(old); old.style().polish(old)
                self.buttons[key].setProperty("class", "active")
                self.buttons[key].style().unpolish(self.buttons[key])
                self.buttons[key].style().polish(self.buttons[key])
                self.active_key = key
                self.refresh_icons()
                main_window = self.parent()
                while main_window is not None and not isinstance(main_window, MainWindow):
                    main_window = main_window.parent()
                if main_window is not None:
                    main_window.switch_page(key)
            except Exception:
                pass
        def paintEvent(self, event):
            try:
                p = QPainter(self)
                glass_paint(self, p, 28, T()["side_tint"], T()["card_border"])
                p.end()
            except Exception:
                pass

if QT_BINDING:
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("MORPHH // ALLPARS V2.0 PRO")
            self.resize(1440, 920)
            self.running = False
            self._radio_on = False
            self._blur_cache = None
            self._base_lock = threading.Lock()
            self._domain_times = {}
            self._domain_times_lock = threading.Lock()
            self.signals = ParserSignals()
            self.validator = EmailValidator()
            self.radio = LoFiRadio(self.signals)
            self.validation_results = {}
            self.val_running = False
            self.mailer_sender = None
            self.mailer_busy = False
            self.email_regex = re.compile(
                r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?'
                r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,63}'
                r'(?![a-z0-9])(?!\.(?:png|jpe?g|gif|webp|svg|ico|bmp|tiff?|css|js|mp4|mp3|zip))',
                re.IGNORECASE)
            self.seed_urls = [
                "https://raw.githubusercontent.com/torvalds/linux/master/MAINTAINERS",
                "https://raw.githubusercontent.com/torvalds/linux/master/.mailmap",
                "https://raw.githubusercontent.com/git/git/master/.mailmap",
                "https://raw.githubusercontent.com/systemd/systemd/main/.mailmap",
                "https://raw.githubusercontent.com/nodejs/node/main/AUTHORS",
                "https://raw.githubusercontent.com/rust-lang/rust/master/AUTHORS",
                "https://raw.githubusercontent.com/golang/go/master/CONTRIBUTORS",
                "https://news.ycombinator.com",
                "https://lobste.rs"
            ]
            self.known_domains = set(); self.seen_emails = set(); self.personal_base = set()
            self.link_cap = 8000
            self.bg = OrbBackground(self)
            self.bg.setGeometry(0, 0, self.width(), self.height())
            main_w = QWidget(self)
            main_layout = QHBoxLayout(main_w)
            main_layout.setContentsMargins(22, 22, 22, 22)
            main_layout.setSpacing(22)
            self.content = QStackedWidget()
            self.page_dashboard = self.create_dashboard_page()
            self.page_parser = self.create_parser_page()
            self.page_auto = self.create_auto_page()
            self.page_validator = self.create_validator_page()
            self.page_mailer = self.create_mailer_page()
            self.page_accounts = self.create_accounts_page()
            self.page_radio = self.create_radio_page()
            self.page_stats = self.create_stats_page()
            self.page_osint = self.create_osint_page()
            for pg in (self.page_dashboard, self.page_parser, self.page_auto, self.page_validator,
                       self.page_mailer, self.page_accounts, self.page_radio, self.page_stats, self.page_osint):
                self.content.addWidget(pg)
            self.sidebar = Sidebar(main_w)
            main_layout.addWidget(self.sidebar)
            main_layout.addWidget(self.content, 1)
            self.setCentralWidget(main_w)
            self.signals.log_signal.connect(self.write_log_safe)
            self.signals.account_signal.connect(self.add_to_recent_table)
            self.signals.progress_signal.connect(self.progress_dash.setValue)
            self.signals.progress_signal.connect(self.dash_ring.setValue)
            self.signals.status_signal.connect(self.set_status_safe)
            self.signals.domain_signal.connect(self.stat_domain.setText)
            self.signals.auto_iter_signal.connect(self.auto_iter.setText)
            self.signals.val_row_signal.connect(self.on_val_row)
            self.signals.val_done_signal.connect(self.on_val_done)
            self.signals.val_progress_signal.connect(self.on_val_progress)
            self.signals.mail_log_signal.connect(self.on_mail_log)
            self.signals.mail_sent_signal.connect(self.on_mail_sent)
            self.signals.mail_status_signal.connect(self.on_mail_status)
            self.signals.radio_status_signal.connect(self.on_radio_status)
            QApplication.instance().setStyleSheet(T()["qss"])
            self._load_existing_base()
            self.update_total_ui()
            QTimer.singleShot(300, self._start_blur)
        def _start_blur(self):
            try:
                self._refresh_blur()
                self._blur_timer = QTimer(self)
                self._blur_timer.timeout.connect(self._refresh_blur)
                self._blur_timer.start(800)
            except Exception:
                pass
        def _refresh_blur(self):
            try:
                pm = self.bg.grab()
                if pm.isNull() or pm.width() < 20:
                    return
                small = pm.scaledToWidth(max(1, pm.width() // 10), Qt.TransformationMode.SmoothTransformation)
                small = small.scaledToWidth(max(1, small.width() // 2), Qt.TransformationMode.SmoothTransformation)
                self._blur_cache = small.scaled(pm.size(), Qt.TransformationMode.SmoothTransformation)
                for w in self.findChildren(AccentCard):
                    w.update()
                self.sidebar.update()
            except Exception:
                pass
        def apply_theme(self, name):
            try:
                global CURRENT_THEME
                CURRENT_THEME = name
                QApplication.instance().setStyleSheet(T()["qss"])
                self.bg.set_theme(name)
                self.sidebar.refresh_icons()
                self.sidebar.set_engine_state(self.running)
                self.sidebar.set_radio_state("", self._radio_on)
                for b in self.findChildren(GlowButton):
                    b.refresh_icon()
                for lbl in self.findChildren(QLabel):
                    pname = lbl.property("picon")
                    if pname:
                        lbl.setPixmap(IconLib.get(pname, T()["text"], 20).pixmap(20, 20))
                self._refresh_blur()
                for w in self.findChildren(QWidget):
                    w.update()
            except Exception:
                pass
        def resizeEvent(self, event):
            super().resizeEvent(event)
            if hasattr(self, "bg"):
                self.bg.setGeometry(0, 0, self.width(), self.height())
        def switch_page(self, key):
            pages = {"dashboard": 0, "parser": 1, "auto": 2, "validator": 3,
                     "mailer": 4, "accounts": 5, "radio": 6, "stats": 7, "osint": 8}
            if key in pages:
                self.content.setCurrentIndex(pages[key])
                if key == "mailer":
                    self.refresh_mailer_dropdown(); self.refresh_mailer_list()
                elif key == "accounts":
                    self.refresh_accounts_view()
                elif key == "stats":
                    self.update_total_ui(); self.refresh_database_table()
        def _make_header(self, text, layout):
            header = QLabel(text)
            header.setObjectName("h1")
            layout.addWidget(header)
            layout.addWidget(RainbowLine())
            return header
        def _make_log_terminal(self, title, accent="#6b6b6b"):
            term_card = AccentCard(ACCENT_PURPLE)
            tl = QVBoxLayout(term_card); tl.setContentsMargins(24, 24, 24, 24); tl.setSpacing(12)
            head_row = QHBoxLayout(); head_row.setSpacing(8)
            head_row.addWidget(PulseDot("#c9c7c3"))
            t = QLabel(title); t.setObjectName("tMono")
            t.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
            head_row.addWidget(t); head_row.addStretch()
            btn_clear = QPushButton("Clear"); btn_clear.setObjectName("linkBtn")
            head_row.addWidget(btn_clear)
            tl.addLayout(head_row)
            edit = QTextEdit(); edit.setReadOnly(True)
            edit.document().setMaximumBlockCount(800)
            btn_clear.clicked.connect(lambda: edit.clear())
            tl.addWidget(edit, 1)
            return term_card, edit
        def create_dashboard_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(20)
            self._make_header("Control Dashboard", layout)
            top_row = QHBoxLayout(); top_row.setSpacing(20)
            dark = AccentCard(dark=True)
            dl = QVBoxLayout(dark); dl.setContentsMargins(26, 24, 26, 24); dl.setSpacing(14)
            dt = QLabel("Overall Information"); dt.setObjectName("cText")
            dt.setFont(QFont("Segoe UI", 15, QFont.Weight.Bold))
            dl.addWidget(dt)
            nums = QHBoxLayout(); nums.setSpacing(28)
            b1 = QVBoxLayout()
            self.stat_total = QLabel("0"); self.stat_total.setObjectName("cBig")
            b1.addWidget(self.stat_total)
            l1 = QLabel("Harvested Mails"); l1.setObjectName("cDim"); b1.addWidget(l1)
            nums.addLayout(b1)
            b2 = QVBoxLayout()
            self.stat_personal = QLabel("0"); self.stat_personal.setObjectName("cBig")
            b2.addWidget(self.stat_personal)
            l2 = QLabel("Personal (Human)"); l2.setObjectName("cDim"); b2.addWidget(l2)
            nums.addLayout(b2); nums.addStretch()
            dl.addLayout(nums)
            tiles = QHBoxLayout(); tiles.setSpacing(12)
            tile1 = QFrame(); tile1.setObjectName("cTile")
            t1 = QVBoxLayout(tile1); t1.setContentsMargins(14, 12, 14, 12)
            self.stat_status = QLabel("IDLE"); self.stat_status.setObjectName("cText")
            self.stat_status.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            t1.addWidget(self.stat_status)
            t1s = QLabel("Crawler Engine"); t1s.setObjectName("cDim"); t1.addWidget(t1s)
            tiles.addWidget(tile1)
            tile2 = QFrame(); tile2.setObjectName("cTile")
            t2 = QVBoxLayout(tile2); t2.setContentsMargins(14, 12, 14, 12)
            self.stat_domain = QLabel("---"); self.stat_domain.setObjectName("cText")
            self.stat_domain.setFont(QFont("Segoe UI", 11, QFont.Weight.DemiBold))
            t2.addWidget(self.stat_domain)
            t2s = QLabel("Current Target URL"); t2s.setObjectName("cDim"); t2.addWidget(t2s)
            tiles.addWidget(tile2, 2)
            dl.addLayout(tiles)
            top_row.addWidget(dark, 3)
            act = AccentCard(ACCENT_CYAN)
            al2 = QVBoxLayout(act); al2.setContentsMargins(24, 22, 24, 22); al2.setSpacing(12)
            at = QLabel("Engine Activity"); at.setObjectName("tTitle"); al2.addWidget(at)
            self.dash_vis = EqualizerVisualizer(); al2.addWidget(self.dash_vis)
            self.progress_dash = AnimatedProgressBar(); self.progress_dash.setValue(0)
            al2.addWidget(self.progress_dash)
            self.status_dash = QLabel("SYSTEM IDLE"); self.status_dash.setObjectName("statusText")
            al2.addWidget(self.status_dash)
            top_row.addWidget(act, 3)
            ring_card = AccentCard(ACCENT_PURPLE)
            rl2 = QVBoxLayout(ring_card); rl2.setContentsMargins(24, 22, 24, 22); rl2.setSpacing(10)
            rt = QLabel("Session Progress"); rt.setObjectName("tTitle"); rl2.addWidget(rt)
            self.dash_ring = RingGauge()
            rl2.addWidget(self.dash_ring, 0, Qt.AlignmentFlag.AlignCenter)
            rc = QLabel("Harvest completion"); rc.setObjectName("statLabel")
            rc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            rl2.addWidget(rc)
            top_row.addWidget(ring_card, 2)
            layout.addLayout(top_row)
            actions_card = AccentCard(ACCENT_PURPLE)
            al = QVBoxLayout(actions_card); al.setContentsMargins(28, 22, 28, 22); al.setSpacing(14)
            lbl_act = QLabel("Control Deck"); lbl_act.setObjectName("tTitle"); al.addWidget(lbl_act)
            btn_row = QHBoxLayout(); btn_row.setSpacing(12)
            self.btn_dash_run = GlowButton("Run Single Session", ACCENT_CYAN, icon="play")
            self.btn_dash_run.clicked.connect(self.start_parsing); btn_row.addWidget(self.btn_dash_run)
            self.btn_dash_auto = GlowButton("Enable Infinite Crawl", ACCENT_CYAN, icon="infinity")
            self.btn_dash_auto.clicked.connect(self.start_auto); btn_row.addWidget(self.btn_dash_auto)
            self.btn_dash_stop = GlowButton("Kill Process", danger=True, icon="stop")
            self.btn_dash_stop.clicked.connect(self.stop_all); self.btn_dash_stop.setEnabled(False)
            btn_row.addWidget(self.btn_dash_stop)
            btn_clear = GlowButton("Clear Database", ACCENT_PURPLE, icon="trash")
            btn_clear.clicked.connect(self.clear_all_data); btn_row.addWidget(btn_clear)
            btn_row.addStretch()
            al.addLayout(btn_row)
            layout.addWidget(actions_card)
            recent_card = AccentCard(ACCENT_CYAN)
            rl = QVBoxLayout(recent_card); rl.setContentsMargins(24, 24, 24, 24); rl.setSpacing(16)
            feed_row = QHBoxLayout(); feed_row.setSpacing(8)
            feed_row.addWidget(PulseDot("#c9c7c3"))
            lbl_recent = QLabel("Extracted Base (Live Feed with Country & Activity)")
            lbl_recent.setObjectName("tTitle"); feed_row.addWidget(lbl_recent); feed_row.addStretch()
            rl.addLayout(feed_row)
            self.recent_table = QTableWidget(0, 4)
            self.recent_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "COUNTRY", "LAST ACTIVE", "SOURCE SITE"])
            self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            self.recent_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            self.recent_table.setShowGrid(False)
            self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            rl.addWidget(self.recent_table)
            layout.addWidget(recent_card, 1)
            return page
        def create_parser_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("Parser Logs", layout)
            term_card, self.log_parser = self._make_log_terminal("PARSER // TERMINAL OUTPUT")
            layout.addWidget(term_card, 1)
            return page
        def create_auto_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("Infinite Engine", layout)
            ctrl_card = AccentCard(ACCENT_GREEN)
            cl = QVBoxLayout(ctrl_card); cl.setContentsMargins(32, 28, 32, 28); cl.setSpacing(16)
            status_row = QHBoxLayout(); status_row.setSpacing(10)
            self.auto_dot = PulseDot("#c9c7c3"); status_row.addWidget(self.auto_dot)
            self.auto_status = QLabel("INFINITE MODE: OFF"); self.auto_status.setObjectName("tTitle")
            self.auto_status.setFont(QFont("Segoe UI", 17, QFont.Weight.Bold))
            status_row.addWidget(self.auto_status); status_row.addStretch()
            cl.addLayout(status_row)
            self.auto_iter = QLabel("Links In Queue: 0"); self.auto_iter.setObjectName("tMono")
            cl.addWidget(self.auto_iter)
            btn_row = QHBoxLayout(); btn_row.setSpacing(16)
            self.btn_auto_start = GlowButton("Launch Infinite", ACCENT_CYAN, icon="infinity")
            self.btn_auto_start.clicked.connect(self.start_auto); btn_row.addWidget(self.btn_auto_start)
            self.btn_auto_stop = GlowButton("Stop", danger=True, icon="stop")
            self.btn_auto_stop.clicked.connect(self.stop_all); self.btn_auto_stop.setEnabled(False)
            btn_row.addWidget(self.btn_auto_stop)
            cl.addLayout(btn_row)
            layout.addWidget(ctrl_card)
            log_card, self.log_auto = self._make_log_terminal("INFINITE ENGINE // LIVE STREAM")
            layout.addWidget(log_card, 1)
            return page
        def create_validator_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("Validator", layout)
            sub = QLabel("Проверка базы на спам-ловушки (Honeypot), мёртвые домены, определение страны и последней активности.")
            sub.setObjectName("tDim"); layout.addWidget(sub)
            ctrl_card = AccentCard(ACCENT_GREEN)
            cl = QVBoxLayout(ctrl_card); cl.setContentsMargins(32, 24, 32, 24); cl.setSpacing(16)
            insp_row = QHBoxLayout()
            self.val_input_single = QLineEdit()
            self.val_input_single.setPlaceholderText("Введите адрес для быстрой проверки: developer@mail.ru, honeypot@trap.com...")
            self.val_input_single.returnPressed.connect(self.inspect_single_address)
            insp_row.addWidget(self.val_input_single, 1)
            btn_insp = GlowButton("Проверить Адрес", ACCENT_PURPLE, icon="search")
            btn_insp.clicked.connect(self.inspect_single_address); insp_row.addWidget(btn_insp)
            cl.addLayout(insp_row)
            btn_row = QHBoxLayout(); btn_row.setSpacing(16)
            self.btn_val_run = GlowButton("Validate Base Now", ACCENT_CYAN, icon="shield")
            self.btn_val_run.clicked.connect(self.run_validation); btn_row.addWidget(self.btn_val_run)
            self.btn_val_clean = GlowButton("Remove TRAP/INVALID From Base", danger=True, icon="trash")
            self.btn_val_clean.clicked.connect(self.clean_base_by_validation); btn_row.addWidget(self.btn_val_clean)
            btn_row.addStretch()
            cl.addLayout(btn_row)
            prog_row = QHBoxLayout(); prog_row.setSpacing(12)
            self.val_progress = QProgressBar(); self.val_progress.setMinimum(0)
            prog_row.addWidget(self.val_progress, 1)
            self.val_counters = QLabel("SAFE: 0 | RISKY: 0 | TRAP: 0 | INVALID: 0")
            self.val_counters.setObjectName("tMono"); prog_row.addWidget(self.val_counters)
            cl.addLayout(prog_row)
            layout.addWidget(ctrl_card)
            tbl_card = AccentCard(ACCENT_CYAN)
            tl = QVBoxLayout(tbl_card); tl.setContentsMargins(24, 24, 24, 24)
            head_row = QHBoxLayout(); head_row.setSpacing(8)
            head_row.addWidget(PulseDot("#c9c7c3"))
            t = QLabel("VALIDATION RESULTS // ALL ADDRESSES (COUNTRY & ACTIVITY INCLUDED)")
            t.setObjectName("tMono"); head_row.addWidget(t); head_row.addStretch()
            tl.addLayout(head_row)
            self.val_table = QTableWidget(0, 6)
            self.val_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "COUNTRY", "LAST ACTIVE", "STATUS", "SCORE", "DETAIL"])
            self.val_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            for c in (1, 2, 3, 4):
                self.val_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
            self.val_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            self.val_table.setShowGrid(False)
            self.val_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.val_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            tl.addWidget(self.val_table, 1)
            layout.addWidget(tbl_card, 1)
            return page
        def create_mailer_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(20)
            self._make_header("Mailer", layout)
            sub = QLabel("Отправка одиночных писем на проверенные адреса из базы. Выбор аккаунтов из accounts.txt.")
            sub.setObjectName("tDim"); layout.addWidget(sub)
            acc_card = AccentCard(ACCENT_PURPLE)
            acl = QVBoxLayout(acc_card); acl.setContentsMargins(28, 20, 28, 20); acl.setSpacing(12)
            lbl_acc = QLabel("SMTP Account (загрузка напрямую из accounts.txt):")
            lbl_acc.setObjectName("tTitle"); acl.addWidget(lbl_acc)
            form_row = QHBoxLayout(); form_row.setSpacing(12)
            self.mailer_acc_combo = QComboBox(); form_row.addWidget(self.mailer_acc_combo, 3)
            self.btn_mail_conn = GlowButton("Test & Connect", ACCENT_CYAN, icon="bolt")
            self.btn_mail_conn.clicked.connect(self.mailer_connect); form_row.addWidget(self.btn_mail_conn, 1)
            btn_open_accs = GlowButton("Manage accounts.txt", ACCENT_PURPLE, icon="vault")
            btn_open_accs.clicked.connect(lambda: self.switch_page("accounts")); form_row.addWidget(btn_open_accs, 1)
            acl.addLayout(form_row)
            self.mail_status_lbl = QLabel("NOT CONNECTED"); self.mail_status_lbl.setObjectName("tMono")
            acl.addWidget(self.mail_status_lbl)
            layout.addWidget(acc_card)
            list_card = AccentCard(ACCENT_GREEN)
            lcl = QVBoxLayout(list_card); lcl.setContentsMargins(24, 18, 24, 18); lcl.setSpacing(10)
            lr = QHBoxLayout(); lr.setSpacing(8)
            lr.addWidget(PulseDot("#c9c7c3"))
            llbl = QLabel("Verified Recipients (SAFE/RISKY only)"); llbl.setObjectName("tTitle")
            lr.addWidget(llbl)
            self.mail_list_count = QLabel(""); self.mail_list_count.setObjectName("tMono")
            lr.addStretch()
            self.btn_mail_refresh = GlowButton("Refresh List", ACCENT_PURPLE, icon="refresh")
            self.btn_mail_refresh.clicked.connect(self.refresh_mailer_list); lr.addWidget(self.btn_mail_refresh)
            lcl.addLayout(lr)
            self.mail_list = QListWidget()
            self.mail_list.itemSelectionChanged.connect(self.on_mailer_selection)
            lcl.addWidget(self.mail_list, 1)
            layout.addWidget(list_card, 1)
            comp_card = AccentCard(ACCENT_CYAN)
            ccl = QVBoxLayout(comp_card); ccl.setContentsMargins(28, 18, 28, 18); ccl.setSpacing(10)
            to_row = QHBoxLayout(); to_row.setSpacing(10)
            to_lbl = QLabel("TO:"); to_lbl.setObjectName("tMono"); to_row.addWidget(to_lbl)
            self.mail_to_lbl = QLabel("(выберите адрес из списка)"); self.mail_to_lbl.setObjectName("tMono")
            to_row.addWidget(self.mail_to_lbl, 1)
            ccl.addLayout(to_row)
            subj_row = QHBoxLayout(); subj_row.setSpacing(10)
            s_lbl = QLabel("SUBJECT:"); s_lbl.setObjectName("tMono"); subj_row.addWidget(s_lbl)
            self.mail_subject_edit = QLineEdit(); self.mail_subject_edit.setPlaceholderText("Тема сообщения...")
            subj_row.addWidget(self.mail_subject_edit, 1)
            ccl.addLayout(subj_row)
            body_lbl = QLabel("MESSAGE:"); body_lbl.setObjectName("tMono"); ccl.addWidget(body_lbl)
            self.mail_body_edit = QPlainTextEdit()
            self.mail_body_edit.setPlaceholderText("Текст письма...")
            self.mail_body_edit.setPlainText("Hello,\n\nI noticed your developer projects and contributions. Would you be open to discussing a potential collaboration?\n\nBest regards,\nOutreach Team")
            self.mail_body_edit.setMaximumHeight(130)
            ccl.addWidget(self.mail_body_edit)
            send_row = QHBoxLayout(); send_row.setSpacing(16)
            self.btn_mail_send = GlowButton("Re-validate & Send", ACCENT_CYAN, icon="send")
            self.btn_mail_send.clicked.connect(self.mailer_send_selected); send_row.addWidget(self.btn_mail_send)
            send_row.addStretch()
            ccl.addLayout(send_row)
            layout.addWidget(comp_card)
            log_card, self.log_mailer = self._make_log_terminal("MAILER // DELIVERY LOG")
            log_card.setMaximumHeight(180)
            layout.addWidget(log_card)
            return page
        def create_accounts_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("Sender Accounts (accounts.txt)", layout)
            split = QHBoxLayout(); split.setSpacing(20)
            c_add = AccentCard(ACCENT_CYAN)
            cal = QVBoxLayout(c_add); cal.setContentsMargins(24, 20, 24, 20); cal.setSpacing(12)
            h1 = QLabel("ДОБАВИТЬ АККАУНТ ОТПРАВИТЕЛЯ"); h1.setObjectName("tTitle"); cal.addWidget(h1)
            self.acc_input_email = QLineEdit(); self.acc_input_email.setPlaceholderText("sender@gmail.com")
            cal.addWidget(self.acc_input_email)
            self.acc_input_pass = QLineEdit(); self.acc_input_pass.setPlaceholderText("App Password (пароль приложения)")
            self.acc_input_pass.setEchoMode(QLineEdit.EchoMode.Password)
            cal.addWidget(self.acc_input_pass)
            btn_save = GlowButton("Сохранить в accounts.txt", ACCENT_CYAN, icon="key")
            btn_save.clicked.connect(self.add_single_account); cal.addWidget(btn_save)
            self.accounts_list = QListWidget(); cal.addWidget(self.accounts_list, 1)
            split.addWidget(c_add, 2)
            c_raw = AccentCard(ACCENT_PURPLE)
            crl = QVBoxLayout(c_raw); crl.setContentsMargins(24, 20, 24, 20); crl.setSpacing(12)
            top_r = QHBoxLayout()
            h2 = QLabel("РЕДАКТОР ФАЙЛА ACCOUNTS.TXT"); h2.setObjectName("tTitle"); top_r.addWidget(h2)
            top_r.addStretch()
            btn_save_raw = GlowButton("Сохранить Файл", ACCENT_CYAN, icon="save")
            btn_save_raw.clicked.connect(self.save_raw_accounts_file); top_r.addWidget(btn_save_raw)
            crl.addLayout(top_r)
            self.accounts_editor = QPlainTextEdit(); crl.addWidget(self.accounts_editor, 1)
            split.addWidget(c_raw, 3)
            layout.addLayout(split)
            return page
        def create_radio_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("Lo-Fi Radio (6 Станций 24/7)", layout)
            player_card = AccentCard(ACCENT_CYAN)
            pcl = QVBoxLayout(player_card); pcl.setContentsMargins(28, 22, 28, 22); pcl.setSpacing(14)
            top_p = QHBoxLayout()
            self.radio_title_lbl = QLabel("FLUXFM CHILLHOP & STUDY BEATS (320KBPS)")
            self.radio_title_lbl.setObjectName("tMono")
            self.radio_title_lbl.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
            top_p.addWidget(self.radio_title_lbl); top_p.addStretch()
            self.radio_state_lbl = QLabel("ОСТАНОВЛЕНО"); self.radio_state_lbl.setObjectName("tMono")
            top_p.addWidget(self.radio_state_lbl)
            pcl.addLayout(top_p)
            self.equalizer = EqualizerVisualizer(); pcl.addWidget(self.equalizer)
            ctrl_row = QHBoxLayout(); ctrl_row.setSpacing(16)
            self.btn_radio_toggle = GlowButton("ВКЛЮЧИТЬ ПОТОК", ACCENT_CYAN, icon="play")
            self.btn_radio_toggle.clicked.connect(self.toggle_radio_playback); ctrl_row.addWidget(self.btn_radio_toggle)
            ctrl_row.addStretch()
            vol_lbl = QLabel(); vol_lbl.setProperty("picon", "volume")
            vol_lbl.setPixmap(IconLib.get("volume", T()["text"], 20).pixmap(20, 20))
            ctrl_row.addWidget(vol_lbl)
            self.slider_radio_vol = QSlider(Qt.Orientation.Horizontal)
            self.slider_radio_vol.setRange(0, 100); self.slider_radio_vol.setValue(75)
            self.slider_radio_vol.setFixedWidth(160)
            self.slider_radio_vol.valueChanged.connect(self.radio.set_volume)
            ctrl_row.addWidget(self.slider_radio_vol)
            pcl.addLayout(ctrl_row)
            layout.addWidget(player_card)
            stations_card = AccentCard(ACCENT_PURPLE)
            scl = QVBoxLayout(stations_card); scl.setContentsMargins(24, 20, 24, 20); scl.setSpacing(10)
            h = QLabel("ВЫБОР СТАНЦИИ:"); h.setObjectName("tTitle"); scl.addWidget(h)
            for idx, st in enumerate(LoFiRadio.STATIONS):
                row = QHBoxLayout()
                ic = QLabel(); ic.setProperty("picon", st["icon"])
                ic.setPixmap(IconLib.get(st["icon"], T()["dim"], 20).pixmap(20, 20))
                row.addWidget(ic)
                lbl = QLabel(f"{st['name']}  [{st['bitrate']}]"); lbl.setObjectName("tText")
                row.addWidget(lbl, 1)
                btn = GlowButton("Играть", ACCENT_PURPLE, icon="play")
                btn.clicked.connect(lambda ch, i=idx: self.select_radio_station(i))
                row.addWidget(btn)
                scl.addLayout(row)
            layout.addWidget(stations_card)
            return page
        def create_stats_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("Database Statistics", layout)
            stats_card = AccentCard(ACCENT_CYAN)
            sl = QVBoxLayout(stats_card); sl.setContentsMargins(36, 28, 36, 28); sl.setSpacing(20)
            top_row = QHBoxLayout()
            b1 = QVBoxLayout()
            self.stats_total_lbl = QLabel("0"); self.stats_total_lbl.setObjectName("statValue")
            self.stats_total_lbl.setStyleSheet("font-size:52px;")
            b1.addWidget(self.stats_total_lbl)
            lbl_st = QLabel("Total Records In SQLite"); lbl_st.setObjectName("statLabel"); b1.addWidget(lbl_st)
            top_row.addLayout(b1)
            b2 = QVBoxLayout()
            self.stats_personal_lbl = QLabel("0"); self.stats_personal_lbl.setObjectName("statValue")
            self.stats_personal_lbl.setStyleSheet("font-size:52px;")
            b2.addWidget(self.stats_personal_lbl)
            lbl_pers = QLabel("Personal Mailboxes"); lbl_pers.setObjectName("statLabel"); b2.addWidget(lbl_pers)
            top_row.addLayout(b2)
            top_row.addStretch()
            sl.addLayout(top_row)
            self.stats_extra = QLabel("SAFE: 0 | TRAP: 0 | RISKY: 0 | INVALID: 0")
            self.stats_extra.setObjectName("tMono")
            sl.addWidget(self.stats_extra)
            exp_row = QHBoxLayout(); exp_row.setSpacing(12)
            btn_txt = GlowButton("Экспорт TXT", ACCENT_PURPLE, icon="doc")
            btn_txt.clicked.connect(self.export_txt); exp_row.addWidget(btn_txt)
            btn_json = GlowButton("Экспорт JSON", ACCENT_PURPLE, icon="doc")
            btn_json.clicked.connect(self.export_json); exp_row.addWidget(btn_json)
            btn_csv = GlowButton("Экспорт Excel (CSV)", ACCENT_CYAN, icon="download")
            btn_csv.clicked.connect(self.export_csv); exp_row.addWidget(btn_csv)
            sl.addLayout(exp_row)
            layout.addWidget(stats_card)
            db_card = AccentCard(ACCENT_PURPLE)
            dbl = QVBoxLayout(db_card); dbl.setContentsMargins(24, 20, 24, 20); dbl.setSpacing(12)
            search_row = QHBoxLayout()
            self.db_search_edit = QLineEdit(); self.db_search_edit.setPlaceholderText("Мгновенный поиск по всей базе почт...")
            self.db_search_edit.textChanged.connect(self.filter_database_table)
            search_row.addWidget(self.db_search_edit, 1)
            btn_refresh = GlowButton("Обновить", ACCENT_PURPLE, icon="refresh")
            btn_refresh.clicked.connect(self.refresh_database_table); search_row.addWidget(btn_refresh)
            dbl.addLayout(search_row)
            self.db_table = QTableWidget(0, 6)
            self.db_table.setHorizontalHeaderLabels(["ID", "EMAIL", "COUNTRY", "LAST ACTIVE", "CATEGORY", "SOURCE"])
            self.db_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.db_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            for c in (2, 3, 4):
                self.db_table.horizontalHeader().setSectionResizeMode(c, QHeaderView.ResizeMode.ResizeToContents)
            self.db_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            self.db_table.setShowGrid(False)
            self.db_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.db_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            dbl.addWidget(self.db_table, 1)
            layout.addWidget(db_card, 1)
            return page
        def create_osint_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(8, 8, 8, 8); layout.setSpacing(24)
            self._make_header("OSINT Network Tools", layout)
            split = QHBoxLayout(); split.setSpacing(20)
            c_dns = AccentCard(ACCENT_CYAN)
            cdl = QVBoxLayout(c_dns); cdl.setContentsMargins(24, 20, 24, 20); cdl.setSpacing(12)
            h1 = QLabel("ИНСПЕКТОР DNS & MX ЗАПИСЕЙ"); h1.setObjectName("tTitle"); cdl.addWidget(h1)
            row_dns = QHBoxLayout()
            self.dns_input = QLineEdit(); self.dns_input.setPlaceholderText("yandex.ru, gmail.com, github.com...")
            row_dns.addWidget(self.dns_input, 1)
            btn_check_dns = GlowButton("Проверить MX", ACCENT_CYAN, icon="globe")
            btn_check_dns.clicked.connect(self.check_dns_action); row_dns.addWidget(btn_check_dns)
            cdl.addLayout(row_dns)
            self.dns_output = QTextEdit(); self.dns_output.setReadOnly(True); cdl.addWidget(self.dns_output, 1)
            split.addWidget(c_dns, 1)
            c_reg = AccentCard(ACCENT_PURPLE)
            crl = QVBoxLayout(c_reg); crl.setContentsMargins(24, 20, 24, 20); crl.setSpacing(12)
            h2 = QLabel("ТЕСТЕР ИЗВЛЕЧЕНИЯ REGEX"); h2.setObjectName("tTitle"); crl.addWidget(h2)
            self.regex_input = QPlainTextEdit(); self.regex_input.setPlaceholderText("Вставьте любой текст с почтами для парсинга...")
            crl.addWidget(self.regex_input, 1)
            btn_run_reg = GlowButton("Извлечь Email Адреса", ACCENT_CYAN, icon="bolt")
            btn_run_reg.clicked.connect(self.run_regex_test); crl.addWidget(btn_run_reg)
            self.regex_output = QTextEdit(); self.regex_output.setReadOnly(True); self.regex_output.setMaximumHeight(140)
            crl.addWidget(self.regex_output)
            split.addWidget(c_reg, 1)
            layout.addLayout(split)
            return page
        # ================= ЛОГИКА =================
        def update_total_ui(self):
            try:
                count = len(self.seen_emails); pcount = len(self.personal_base)
                self.stat_total.setText(str(count)); self.stat_personal.setText(str(pcount))
                if hasattr(self, "stats_total_lbl"): self.stats_total_lbl.setText(str(count))
                if hasattr(self, "stats_personal_lbl"): self.stats_personal_lbl.setText(str(pcount))
            except Exception:
                pass
        def _load_existing_base(self):
            for r in EmailDatabase.get_all_records():
                self.seen_emails.add(r[1])
                if "HUMAN" in str(r[4]): self.personal_base.add(r[1])
        def add_to_recent_table(self, email, source_url, country, last_active):
            try:
                row = self.recent_table.rowCount()
                if row >= 25:
                    self.recent_table.removeRow(0); row -= 1
                self.recent_table.insertRow(row)
                it_e = QTableWidgetItem(email); it_e.setForeground(QColor(T()["text"]))
                it_c = QTableWidgetItem(country); it_c.setForeground(QColor(T()["dim"]))
                it_a = QTableWidgetItem(last_active); it_a.setForeground(QColor(T()["success"]))
                it_s = QTableWidgetItem(source_url[:40]); it_s.setForeground(QColor(T()["dim"]))
                for col, it in enumerate([it_e, it_c, it_a, it_s]):
                    self.recent_table.setItem(row, col, it)
                self.update_total_ui()
            except Exception:
                pass
        def write_log_safe(self, msg, tag, widget_type):
            try:
                widget = self.log_auto if widget_type == "auto" else self.log_parser
                ts = time.strftime("%H:%M:%S")
                color = T()["log"].get(tag, T()["dim"])
                widget.append(f'<span style="color:{color};">[{ts}] {msg}</span>')
            except Exception:
                pass
        def set_status_safe(self, text, running):
            try:
                self.status_dash.setText(text)
                recolor(self.status_dash, "tText" if running else "statusText")
                self.stat_status.setText("ACTIVE" if running else "IDLE")
                pop_animate(self.stat_status)
                self.btn_dash_run.setEnabled(not running); self.btn_dash_auto.setEnabled(not running)
                self.btn_dash_stop.setEnabled(running)
                self.btn_auto_start.setEnabled(not running); self.btn_auto_stop.setEnabled(running)
                if running:
                    self.auto_status.setText("ENGINE: CRAWLING"); recolor(self.auto_status, "tOk")
                    self.auto_dot.set_color(T()["success"])
                else:
                    self.auto_status.setText("ENGINE: STOPPED"); recolor(self.auto_status, "tTitle")
                    self.auto_dot.set_color("#c9c7c3")
                if hasattr(self, "dash_vis"):
                    self.dash_vis.set_active(running)
                self.sidebar.set_engine_state(running)
            except Exception:
                pass
        def start_parsing(self):
            if self.running: return
            self.running = True
            self.signals.status_signal.emit("SINGLE HARVEST ACTIVE...", True)
            self.signals.progress_signal.emit(0)
            threading.Thread(target=self._run_single_session, daemon=True).start()
        def start_auto(self):
            if self.running: return
            self.running = True
            self.signals.status_signal.emit("INFINITE CRAWL ACTIVE", True)
            threading.Thread(target=self._run_infinite_session, daemon=True).start()
        def stop_all(self):
            self.running = False
            self.signals.log_signal.emit("Прерывание потоков. Остановка движка...", "warn", "parser")
            self.signals.log_signal.emit("Прерывание потоков. Остановка движка...", "warn", "auto")
        def _fetch_page(self, url, retries=2):
            last_err = None
            for attempt in range(retries + 1):
                try:
                    if curl_requests is not None:
                        try:
                            return curl_requests.get(url, impersonate="chrome", timeout=8, allow_redirects=True)
                        except Exception:
                            pass
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
                    return requests.get(url, headers=headers, timeout=8, allow_redirects=True)
                except Exception as e:
                    last_err = e
                    time.sleep(1.2 * (attempt + 1))
            raise last_err if last_err else RuntimeError("fetch failed")
        def _polite_wait(self, domain):
            try:
                with self._domain_times_lock:
                    last = self._domain_times.get(domain, 0.0)
                    wait = 0.8 - (time.time() - last)
                if wait > 0:
                    time.sleep(wait)
                with self._domain_times_lock:
                    self._domain_times[domain] = time.time()
            except Exception:
                pass
        def _run_single_session(self):
            q = queue.Queue()
            for u in self.seed_urls: q.put(u)
            self.signals.log_signal.emit("Запуск сессии парсинга (60 узлов, 4 потока)...", "info", "parser")
            self._execute_harvest(q, max_pages=60, log_widget="parser", workers=4)
            self.running = False
            self.signals.status_signal.emit("SYSTEM IDLE", False)
            self.signals.progress_signal.emit(100)
        def _run_infinite_session(self):
            q = queue.Queue()
            for u in self.seed_urls: q.put(u)
            self.signals.log_signal.emit("СТАРТ БЕСКОНЕЧНОГО ДВИЖКА (6 потоков)...", "info", "auto")
            self._execute_harvest(q, max_pages=None, log_widget="auto", workers=6)
            self.running = False
            self.signals.status_signal.emit("SYSTEM IDLE", False)
            self.signals.progress_signal.emit(0)
        def _execute_harvest(self, url_queue, max_pages=None, log_widget="parser", workers=4):
            visited = set(); visited_lock = threading.Lock()
            domain_pages = {}
            pages_processed = 0
            counter_lock = threading.Lock()
            def worker():
                nonlocal pages_processed
                while self.running:
                    with counter_lock:
                        if max_pages and pages_processed >= max_pages:
                            return
                    try:
                        raw_url = url_queue.get_nowait()
                    except queue.Empty:
                        if max_pages:
                            return
                        for s in self.seed_urls:
                            url_queue.put(s)
                        time.sleep(1.0)
                        continue
                    current_url = normalize_url(raw_url)
                    if not current_url:
                        continue
                    try:
                        domain = urlsplit(current_url).netloc
                    except Exception:
                        continue
                    with visited_lock:
                        if current_url in visited:
                            continue
                        visited.add(current_url)
                        hits = domain_pages.get(domain, 0)
                        if hits >= 60:
                            continue
                        domain_pages[domain] = hits + 1
                    self._polite_wait(domain)
                    self.signals.domain_signal.emit(current_url[:42] + "...")
                    self.signals.log_signal.emit(f"Запрос к источнику: {current_url}", "info", log_widget)
                    try:
                        r = self._fetch_page(current_url)
                        with counter_lock:
                            pages_processed += 1
                            done = pages_processed
                        if max_pages:
                            self.signals.progress_signal.emit(int((done / max_pages) * 100))
                        if r.status_code == 200:
                            text = r.text
                            found = set(self.email_regex.findall(text))
                            new_count = 0
                            for em in found:
                                em_l = em.lower().strip()
                                if len(em_l) > 254 or ".." in em_l:
                                    continue
                                with self._base_lock:
                                    if em_l in self.seen_emails:
                                        continue
                                    self.seen_emails.add(em_l)
                                    dom = em_l.split("@")[-1]
                                    if dom in PERSONAL_PROVIDERS:
                                        cat = "HUMAN / PERSONAL"; self.personal_base.add(em_l)
                                    elif dom in DEV_DOMAINS:
                                        cat = "DEV / OPEN SOURCE"
                                    else:
                                        cat = "CORPORATE / DEV"
                                co, la = EmailDatabase.insert_email(em_l, cat, current_url, status="SAFE", score=90)
                                new_count += 1
                                self.signals.account_signal.emit(em_l, current_url, co, la)
                            if new_count > 0:
                                self.signals.log_signal.emit(f"Найдено {new_count} новых почт с {current_url}", "success", log_widget)
                            links = re.findall(r'href=[\'"](https?://[^\'" >]+)[\'"]', text)
                            for lk in links:
                                if url_queue.qsize() < self.link_cap:
                                    nl = normalize_url(lk)
                                    if nl:
                                        with visited_lock:
                                            if nl not in visited:
                                                url_queue.put(nl)
                            self.signals.auto_iter_signal.emit(f"Queue: {url_queue.qsize()} | Visited: {len(visited)} | Base: {len(self.seen_emails)}")
                    except Exception as e:
                        self.signals.log_signal.emit(f"Ошибка {current_url[:30]}: {e}", "err", log_widget)
                    time.sleep(random.uniform(0.2, 0.5))
            threads = [threading.Thread(target=worker, daemon=True) for _ in range(workers)]
            for t in threads: t.start()
            for t in threads: t.join()
        def inspect_single_address(self):
            em = self.val_input_single.text().strip()
            if not em or "@" not in em: return
            st, sc, dt, co, la = self.validator.validate(em)
            self.on_val_row(em, st, sc, dt, co, la)
            self.val_input_single.clear()
        def on_val_row(self, email, status, score, detail, country, last_active):
            try:
                self.validation_results[email] = (status, score, detail)
                row = self.val_table.rowCount()
                self.val_table.insertRow(row)
                c = QColor(T()["success"] if status == "SAFE" else T()["danger"] if status == "TRAP" else T()["warn"])
                it_e = QTableWidgetItem(email); it_e.setForeground(QColor(T()["text"]))
                it_co = QTableWidgetItem(country); it_co.setForeground(QColor(T()["dim"]))
                it_la = QTableWidgetItem(last_active); it_la.setForeground(QColor(T()["dim"]))
                it_s = QTableWidgetItem(status); it_s.setForeground(c)
                it_sc = QTableWidgetItem(str(score)); it_sc.setForeground(c)
                it_d = QTableWidgetItem(detail); it_d.setForeground(QColor(T()["text"]))
                for col, it in enumerate([it_e, it_co, it_la, it_s, it_sc, it_d]):
                    self.val_table.setItem(row, col, it)
                self._update_val_counters()
            except Exception:
                pass
        def _update_val_counters(self):
            c = {'SAFE': 0, 'RISKY': 0, 'TRAP': 0, 'INVALID': 0}
            for st, _, _ in self.validation_results.values():
                if st in c: c[st] += 1
            self.val_counters.setText(f"SAFE: {c['SAFE']} | RISKY: {c['RISKY']} | TRAP: {c['TRAP']} | INVALID: {c['INVALID']}")
        def on_val_progress(self, done, total):
            self.val_progress.setValue(int(done / max(1, total) * 100))
        def on_val_done(self):
            self.val_running = False
            self.btn_val_run.setEnabled(True)
            self.signals.mail_log_signal.emit(f"Валидация завершена. SAFE адресов: {sum(1 for st,_,_ in self.validation_results.values() if st == 'SAFE')}.", "success")
            self.refresh_mailer_list()
            self.refresh_database_table()
        def run_validation(self):
            if self.val_running: return
            emails = sorted(self.seen_emails)
            if not emails: return
            self.val_running = True
            self.btn_val_run.setEnabled(False)
            self.val_table.setRowCount(0)
            self.validation_results = {}
            def work():
                total = len(emails); done = 0
                try:
                    with ThreadPoolExecutor(max_workers=8) as ex:
                        futs = {ex.submit(self.validator.validate, em): em for em in emails}
                        for fut in as_completed(futs):
                            em = futs[fut]
                            try:
                                st, sc, dt, co, la = fut.result()
                            except Exception:
                                st, sc, dt, co, la = ('INVALID', 0, 'Сбой проверки', detect_country(em), '')
                            EmailDatabase.update_status(em, st, sc)
                            self.signals.val_row_signal.emit(em, st, sc, dt, co, la)
                            done += 1
                            self.signals.val_progress_signal.emit(done, total)
                except Exception:
                    _write_crash("validation: " + traceback.format_exc())
                self.signals.val_done_signal.emit()
            threading.Thread(target=work, daemon=True).start()
        def clean_base_by_validation(self):
            cnt = EmailDatabase.purge_invalids_and_traps()
            self.seen_emails = set(); self.personal_base = set()
            self._load_existing_base(); self.update_total_ui(); self.refresh_database_table()
            QMessageBox.information(self, "Очистка", f"Удалено {cnt} спам-ловушек и невалидных почт!")
        def refresh_mailer_dropdown(self):
            self.mailer_acc_combo.clear()
            for a in MailerAccountManager.load_accounts():
                self.mailer_acc_combo.addItem(f"{a['email']} ({a['provider']})", a)
        def refresh_mailer_list(self):
            try:
                self.mail_list.clear()
                records = EmailDatabase.get_all_records()
                shown = 0
                for r in records:
                    if str(r[6]) not in ("SAFE", "RISKY"):
                        continue
                    it = QListWidgetItem(f"{r[1]}   [{r[2]}]")
                    it.setData(Qt.ItemDataRole.UserRole, r[1])
                    it.setForeground(QColor(T()["text"]))
                    self.mail_list.addItem(it)
                    shown += 1
                    if shown >= 120:
                        break
                self.mail_list_count.setText(f"{shown} доставляемых в базе")
            except Exception:
                pass
        def on_mailer_selection(self):
            items = self.mail_list.selectedItems()
            if items:
                self.mail_to_lbl.setText(items[0].data(Qt.ItemDataRole.UserRole))
        def mailer_connect(self):
            data = self.mailer_acc_combo.currentData()
            if not data: return
            self.btn_mail_conn.setEnabled(False)
            self.on_mail_status("CONNECTING...", "warn")
            def work():
                sender = SmtpSender(data["email"], data["password"], log_fn=lambda m, t="info": self.signals.mail_log_signal.emit(m, t))
                try:
                    sender.connect()
                    self.mailer_sender = sender
                    self.signals.mail_status_signal.emit(f"CONNECTED AS {data['email']}", "ok")
                except Exception as e:
                    self.signals.mail_log_signal.emit(f"Ошибка SMTP: {e}", "err")
                    self.signals.mail_status_signal.emit("CONNECTION FAILED", "err")
                finally:
                    self.btn_mail_conn.setEnabled(True)
            threading.Thread(target=work, daemon=True).start()
        def mailer_send_selected(self):
            if self.mailer_busy: return
            to_email = self.mail_to_lbl.text()
            if "@" not in to_email:
                QMessageBox.warning(self, "Ошибка", "Выберите адрес получателя!"); return
            if not self.mailer_sender:
                QMessageBox.warning(self, "Ошибка", "Подключите аккаунт отправителя (Connect)!"); return
            subj = self.mail_subject_edit.text() or "Cooperation Proposal"
            body = self.mail_body_edit.toPlainText()
            st, sc, dt, co, la = self.validator.validate(to_email)
            if st in ('TRAP', 'INVALID'):
                QMessageBox.critical(self, "БЛОКИРОВКА ПРЕ-ФЛАЙТ", f"Адрес {to_email} признан спам-ловушкой ({st})!\n{dt}")
                return
            self.mailer_busy = True
            self.btn_mail_send.setEnabled(False)
            self.on_mail_status("SENDING...", "info")
            def work():
                ok = False
                for attempt in range(2):
                    try:
                        self.mailer_sender.send(to_email, subj, body)
                        ok = True
                        break
                    except Exception as e:
                        self.signals.mail_log_signal.emit(f"Попытка {attempt + 1} не удалась: {e}", "warn")
                        try:
                            self.mailer_sender.close(); self.mailer_sender.connect()
                        except Exception:
                            pass
                        time.sleep(1.5)
                if ok:
                    self.signals.mail_log_signal.emit(f"Письмо доставлено: {to_email}", "success")
                    self.signals.mail_status_signal.emit("LAST MAIL SENT OK", "ok")
                else:
                    self.signals.mail_log_signal.emit(f"Сбой отправки: {to_email}", "err")
                    self.signals.mail_status_signal.emit("SEND ERROR", "err")
                self.mailer_busy = False
                self.btn_mail_send.setEnabled(True)
            threading.Thread(target=work, daemon=True).start()
        def on_mail_log(self, msg, tag):
            try:
                ts = time.strftime("%H:%M:%S")
                c = T()["log"].get(tag, T()["dim"])
                self.log_mailer.append(f'<span style="color:{c};">[{ts}] {msg}</span>')
            except Exception:
                pass
        def on_mail_status(self, text, color):
            try:
                up = text.upper()
                if color == "ok" or "CONNECTED" in up or "SENT" in up:
                    on = "tOk"
                elif color == "err" or "FAIL" in up or "ERROR" in up:
                    on = "tErr"
                elif "SENDING" in up or "CONNECTING" in up:
                    on = "tText"
                else:
                    on = "tMono"
                self.mail_status_lbl.setText(text)
                recolor(self.mail_status_lbl, on)
            except Exception:
                pass
        def on_mail_sent(self, email, res):
            pass
        def refresh_accounts_view(self):
            accs = MailerAccountManager.load_accounts()
            self.accounts_list.clear()
            for a in accs:
                self.accounts_list.addItem(f"{a['email']}  [{a['provider']}]")
            path = MailerAccountManager.get_file_path()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    self.accounts_editor.setPlainText(f.read())
        def add_single_account(self):
            em = self.acc_input_email.text().strip()
            pw = self.acc_input_pass.text().strip()
            if not em or "@" not in em or not pw: return
            path = MailerAccountManager.get_file_path()
            with open(path, "a", encoding="utf-8") as f:
                f.write(f"\n{em}:{pw}\n")
            self.acc_input_email.clear(); self.acc_input_pass.clear()
            self.refresh_accounts_view()
        def save_raw_accounts_file(self):
            txt = self.accounts_editor.toPlainText()
            path = MailerAccountManager.get_file_path()
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            self.refresh_accounts_view()
            QMessageBox.information(self, "Сохранено", "accounts.txt успешно обновлен!")
        def on_radio_status(self, name, is_on):
            try:
                self._radio_on = is_on
                self.radio_title_lbl.setText(name.upper())
                self.radio_state_lbl.setText("ВОСПРОИЗВЕДЕНИЕ" if is_on else "ОСТАНОВЛЕНО")
                self.btn_radio_toggle._icon_name = "stop" if is_on else "play"
                self.btn_radio_toggle.setText("ОСТАНОВИТЬ" if is_on else "ВКЛЮЧИТЬ ПОТОК")
                self.btn_radio_toggle.refresh_icon()
                self.equalizer.set_active(is_on)
                self.sidebar.set_radio_state(name, is_on)
            except Exception:
                pass
        def toggle_radio_playback(self):
            if self.radio.is_playing: self.radio.stop()
            else: self.radio.play(0)
        def select_radio_station(self, idx):
            self.radio.play(idx)
        def refresh_database_table(self):
            try:
                records = EmailDatabase.get_all_records()
                self.db_table.setRowCount(0)
                for r in records:
                    row = self.db_table.rowCount()
                    self.db_table.insertRow(row)
                    it_id = QTableWidgetItem(str(r[0])); it_id.setForeground(QColor(T()["dim"]))
                    it_e = QTableWidgetItem(r[1]); it_e.setForeground(QColor(T()["text"]))
                    it_co = QTableWidgetItem(r[2]); it_co.setForeground(QColor(T()["dim"]))
                    it_la = QTableWidgetItem(r[3]); it_la.setForeground(QColor(T()["success"]))
                    it_c = QTableWidgetItem(r[4]); it_c.setForeground(QColor(T()["dim"]))
                    it_s = QTableWidgetItem(r[5][:40]); it_s.setForeground(QColor(T()["dim"]))
                    for col, it in enumerate([it_id, it_e, it_co, it_la, it_c, it_s]):
                        self.db_table.setItem(row, col, it)
                st = EmailDatabase.get_stats()
                if hasattr(self, "stats_extra"):
                    self.stats_extra.setText(f"SAFE: {st['safe']} | TRAP: {st['trap']} | RISKY: {st['risky']} | INVALID: {st['invalid']}")
            except Exception:
                pass
        def filter_database_table(self, query):
            query = query.lower()
            for row in range(self.db_table.rowCount()):
                match = any(query in (self.db_table.item(row, c).text().lower() if self.db_table.item(row, c) else "") for c in range(self.db_table.columnCount()))
                self.db_table.setRowHidden(row, not match)
        def clear_all_data(self):
            EmailDatabase.clear_database()
            self.seen_emails.clear(); self.personal_base.clear()
            self.update_total_ui(); self.refresh_database_table()
            self.recent_table.setRowCount(0)
            QMessageBox.information(self, "Очищено", "База данных успешно очищена!")
        def export_txt(self):
            p, _ = QFileDialog.getSaveFileName(self, "Сохранить TXT", "emails.txt", "Text (*.txt)")
            if p:
                with open(p, "w", encoding="utf-8") as f:
                    for r in EmailDatabase.get_all_records(): f.write(f"{r[1]}\n")
                QMessageBox.information(self, "Экспорт", "База TXT успешно сохранена!")
        def export_json(self):
            p, _ = QFileDialog.getSaveFileName(self, "Сохранить JSON", "emails.json", "JSON (*.json)")
            if p:
                data = [{"email": r[1], "country": r[2], "last_active": r[3], "category": r[4], "source": r[5]} for r in EmailDatabase.get_all_records()]
                with open(p, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                QMessageBox.information(self, "Экспорт", "База JSON успешно сохранена!")
        def export_csv(self):
            QMessageBox.information(self, "Экспорт", f"CSV файл сохранен по адресу:\n{EmailDatabase.CSV_PATH}")
        def check_dns_action(self):
            d = self.dns_input.text().strip()
            if not d: return
            if "@" in d: d = d.split("@")[-1]
            hosts = self.validator.get_mx(d)
            co = detect_country(f"test@{d}")
            self.dns_output.clear()
            self.dns_output.append(f"[*] Анализ домена: {d}")
            self.dns_output.append(f"[+] Страна: {co}")
            if hosts:
                self.dns_output.append(f"[OK] MX Серверы ({len(hosts)}):")
                for h in hosts: self.dns_output.append(f"    - {h}")
            else:
                self.dns_output.append("[NO] MX серверы отсутствуют.")
        def run_regex_test(self):
            raw = self.regex_input.toPlainText()
            found = set(self.email_regex.findall(raw))
            self.regex_output.clear()
            self.regex_output.append(f"Найдено {len(found)} адресов:\n" + "\n".join(found))

def main():
    if MISSING_DEPS:
        print("=" * 70)
        print("  MORPHH // ALLPARS V2.0 PRO - CLEAN GLASS EDITION")
        print("=" * 70)
        print("[!] Для запуска графического интерфейса требуются библиотеки:")
        for dep in MISSING_DEPS:
            print(f"    - {dep}")
        print("\nУстановите все зависимости командой:")
        print("    pip install -r requirements.txt")
        print("=" * 70)
        sys.exit(1)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setFont(QFont("Segoe UI", 10))
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
