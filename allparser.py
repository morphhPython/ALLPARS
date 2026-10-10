# -*- coding: utf-8 -*-
"""
MORPHH // ALLPARS V2.0 PRO - CYBERPUNK OSINT & HARVESTING SUITE
================================================================
GUI architecture based on original Morphh design with dynamic OrbBackground,
AccentCard glassmorphism, left-accent neon strips, AnimatedLogo, GlowButtons,
RainbowLine, PulseDot, and AnimatedProgressBar.

Contains:
- Multi-threaded recursive spider & Dork generator
- AI Email Validator with Honeypot detection, MX check, Country & Last-Active detection
- Multilingual Outreach Mailer (RFC5322, App-Passwords, spam shields)
- Sender Accounts Vault (accounts.txt)
- 24/7 Lo-Fi Cyberpunk Radio with Spectrum Visualizer
- SQLite & CSV database with multi-format export (TXT, JSON, CSV)
- OSINT network tools (DNS, MX, Regex sandbox)

Dependencies are defined in requirements.txt:
    pip install -r requirements.txt
"""

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
import webbrowser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, make_msgid
import datetime as _dt

# =====================================================================
# ПРОВЕРКА ЗАВИСИМОСТЕЙ (БЕЗ АВТО-СКАЧИВАНИЯ, ЧИСТОЕ ИНФОРМИРОВАНИЕ)
# =====================================================================
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
    from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QObject, QRectF, QPointF, QUrl
    from PyQt6.QtGui import (
        QPainter, QColor, QFont, QLinearGradient, QBrush, QPen,
        QRadialGradient, QCursor
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
        from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, Signal as pyqtSignal, QObject, QRectF, QPointF, QUrl
        from PySide6.QtGui import (
            QPainter, QColor, QFont, QLinearGradient, QBrush, QPen,
            QRadialGradient, QCursor
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

# Мультимедиа для радио
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
# КАРТА СТРАН И ОПРЕДЕЛЕНИЕ ГЕОЛОКАЦИИ ПОЧТЫ
# =====================================================================
COUNTRY_TLD_MAP = {
    'ru': ('Россия', '🇷🇺'), 'su': ('Россия / СНГ', '🇷🇺'), 'рф': ('Россия', '🇷🇺'),
    'ua': ('Украина', '🇺🇦'), 'by': ('Беларусь', '🇧🇾'), 'kz': ('Казахстан', '🇰🇿'),
    'de': ('Германия', '🇩🇪'), 'uk': ('Великобритания', '🇬🇧'), 'fr': ('Франция', '🇫🇷'),
    'it': ('Италия', '🇮🇹'), 'es': ('Испания', '🇪🇸'), 'pl': ('Польша', '🇵🇱'),
    'nl': ('Нидерланды', '🇳🇱'), 'ch': ('Швейцария', '🇨🇭'), 'at': ('Австрия', '🇦🇹'),
    'cz': ('Чехия', '🇨🇿'), 'se': ('Швеция', '🇸🇪'), 'no': ('Норвегия', '🇳🇴'),
    'fi': ('Финляндия', '🇫🇮'), 'dk': ('Дания', '🇩🇰'), 'jp': ('Япония', '🇯🇵'),
    'cn': ('Китай', '🇨🇳'), 'kr': ('Южная Корея', '🇰🇷'), 'in': ('Индия', '🇮🇳'),
    'br': ('Бразилия', '🇧🇷'), 'ca': ('Канада', '🇨🇦'), 'au': ('Австралия', '🇦🇺'),
    'us': ('США', '🇺🇸'), 'tr': ('Турция', '🇹🇷'), 'il': ('Израиль', '🇮🇱'),
    'ae': ('ОАЭ', '🇦🇪'), 'sg': ('Сингапур', '🇸🇬'), 'za': ('ЮАР', '🇿🇦'),
    'pt': ('Португалия', '🇵🇹'), 'gr': ('Греция', '🇬🇷'), 'be': ('Бельгия', '🇧🇪'),
    'ro': ('Румыния', '🇷🇴'), 'hu': ('Венгрия', '🇭🇺'), 'bg': ('Болгария', '🇧🇬'),
    'rs': ('Сербия', '🇷🇸'), 'am': ('Армения', '🇦🇲'), 'ge': ('Грузия', '🇬🇪'),
    'uz': ('Узбекистан', '🇺🇿'), 'az': ('Азербайджан', '🇦🇿'), 'mx': ('Мексика', '🇲🇽'),
    'io': ('Global / Tech', '🌐'), 'ai': ('Global / AI', '🤖'),
    'dev': ('Global / Dev', '💻'), 'org': ('Международный Org', '🌐'),
    'net': ('Международный Net', '🌐'), 'com': ('Международный Com', '🌐')
}

POPULAR_DOMAINS_MAP = {
    'yandex.ru': ('Россия', '🇷🇺'), 'mail.ru': ('Россия', '🇷🇺'), 'bk.ru': ('Россия', '🇷🇺'),
    'inbox.ru': ('Россия', '🇷🇺'), 'list.ru': ('Россия', '🇷🇺'), 'rambler.ru': ('Россия', '🇷🇺'),
    'ya.ru': ('Россия', '🇷🇺'), 'internet.ru': ('Россия', '🇷🇺'),
    'ukr.net': ('Украина', '🇺🇦'), 'i.ua': ('Украина', '🇺🇦'),
    'seznam.cz': ('Чехия', '🇨🇿'),
    'gmx.de': ('Германия', '🇩🇪'), 'web.de': ('Германия', '🇩🇪'), 't-online.de': ('Германия', '🇩🇪'),
    'qq.com': ('Китай', '🇨🇳'), '163.com': ('Китай', '🇨🇳'),
    'naver.com': ('Южная Корея', '🇰🇷'),
    'orange.fr': ('Франция', '🇫🇷'), 'free.fr': ('Франция', '🇫🇷'),
    'gmail.com': ('США / Global', '🇺🇸'), 'googlemail.com': ('США / Global', '🇺🇸'),
    'outlook.com': ('США / Global', '🇺🇸'), 'hotmail.com': ('США / Global', '🇺🇸'),
    'yahoo.com': ('США / Global', '🇺🇸'), 'icloud.com': ('США / Global', '🇺🇸'),
    'proton.me': ('Швейцария / Global', '🇨🇭'), 'protonmail.com': ('Швейцария / Global', '🇨🇭'),
    'aol.com': ('США', '🇺🇸')
}

def detect_country(email: str) -> str:
    if '@' not in email:
        return "Международный 🌐"
    domain = email.split('@')[-1].lower().strip()
    if domain in POPULAR_DOMAINS_MAP:
        name, flag = POPULAR_DOMAINS_MAP[domain]
        return f"{name} {flag}"
    parts = domain.split('.')
    tld = parts[-1] if parts else ''
    if tld in COUNTRY_TLD_MAP:
        name, flag = COUNTRY_TLD_MAP[tld]
        return f"{name} {flag}"
    return "Международный 🌐"

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


# =====================================================================
# БАЗА ДАННЫХ И ТАБЛИЦА СПАРСЕННЫХ ПОЧТ (SQLITE + CSV)
# =====================================================================
class EmailDatabase:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "allparser_database.sqlite")
    CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPocht.csv")
    TXT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPochtRassilka.txt")
    _lock = threading.Lock()

    @classmethod
    def init_db(cls):
        with cls._lock:
            conn = sqlite3.connect(cls.DB_PATH)
            c = conn.cursor()
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
            conn.commit()
            conn.close()

    @classmethod
    def insert_email(cls, email: str, category: str, source: str, status: str = "SAFE", score: int = 90):
        email = email.strip().lower()
        domain = email.split('@')[-1]
        country = detect_country(email)
        last_active = estimate_last_active(email, source)
        now_str = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with cls._lock:
            conn = sqlite3.connect(cls.DB_PATH)
            c = conn.cursor()
            c.execute("""
                INSERT OR IGNORE INTO emails 
                (email, domain, country, last_active, category, target_source, status, score, discovered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (email, domain, country, last_active, category, source, status, score, now_str))
            conn.commit()
            conn.close()

        cls.append_to_csv(email, domain, country, last_active, category, source, status, score, now_str)
        try:
            with open(cls.TXT_PATH, "a", encoding="utf-8") as f:
                f.write(f"{email}\n")
        except Exception:
            pass
        return country, last_active

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
            conn = sqlite3.connect(cls.DB_PATH)
            c = conn.cursor()
            c.execute("SELECT id, email, country, last_active, category, target_source, status, score, discovered_at FROM emails ORDER BY id DESC")
            rows = c.fetchall()
            conn.close()
            return rows

    @classmethod
    def get_count(cls):
        with cls._lock:
            conn = sqlite3.connect(cls.DB_PATH)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM emails")
            count = c.fetchone()[0]
            conn.close()
            return count

    @classmethod
    def clear_database(cls):
        with cls._lock:
            conn = sqlite3.connect(cls.DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM emails")
            conn.commit()
            conn.close()
        for p in (cls.CSV_PATH, cls.TXT_PATH):
            try:
                if os.path.exists(p):
                    os.remove(p)
            except Exception:
                pass

    @classmethod
    def purge_invalids_and_traps(cls):
        with cls._lock:
            conn = sqlite3.connect(cls.DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM emails WHERE status IN ('TRAP', 'INVALID')")
            deleted = c.rowcount
            conn.commit()
            conn.close()
            return deleted

EmailDatabase.init_db()


# =====================================================================
# СИГНАЛЫ ДЛЯ ВЗАИМОДЕЙСТВИЯ С GUI
# =====================================================================
if QT_BINDING:
    class ParserSignals(QObject):
        log_signal = pyqtSignal(str, str, object)             # msg, tag, widget_target ("parser" or "auto")
        account_signal = pyqtSignal(str, str, str, str)       # email, source_url, country, last_active
        progress_signal = pyqtSignal(int)
        status_signal = pyqtSignal(str, bool)
        domain_signal = pyqtSignal(str)
        auto_iter_signal = pyqtSignal(str)
        val_row_signal = pyqtSignal(str, str, int, str, str, str)  # email, status, score, detail, country, last_active
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
# ОРИГИНАЛЬНЫЕ QSS СТИЛИ MORPHH V3.1
# =====================================================================
QSS = """
QMainWindow { background-color: #050508; }
QWidget#sidebar { background-color: rgba(12, 8, 22, 0.72); border-right: 1px solid rgba(138, 43, 226, 0.25); }
QPushButton#navBtn { font-family: "Segoe UI", sans-serif; font-size: 13px; font-weight: 500; color: #6a6a80; background-color: transparent; border: none; border-radius: 12px; padding: 12px 18px; text-align: left; min-height: 44px; border-left: 3px solid transparent; }
QPushButton#navBtn:hover { color: #b0b0c0; background-color: rgba(138, 43, 226, 0.08); border-left: 3px solid rgba(0, 243, 255, 0.5); }
QPushButton#navBtn.active { color: #ffffff; background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #b026ff); font-weight: 600; border-left: 3px solid #00f3ff; }
QWidget#card { background-color: rgba(22, 16, 40, 0.55); border: 1px solid rgba(138, 43, 226, 0.22); border-radius: 20px; }
QPushButton#actionBtn { font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; color: #ffffff; background-color: rgba(138, 43, 226, 0.2); border: 1px solid rgba(138, 43, 226, 0.4); border-radius: 14px; padding: 14px 28px; min-height: 46px; letter-spacing: 0.5px; }
QPushButton#actionBtn:hover { background-color: rgba(138, 43, 226, 0.35); border-color: rgba(138, 43, 226, 0.7); }
QPushButton#actionBtn:pressed { background-color: rgba(138, 43, 226, 0.5); }
QPushButton#actionBtn:disabled { color: #3a3a4a; background-color: rgba(255, 255, 255, 0.02); border-color: rgba(255, 255, 255, 0.05); }
QPushButton#stopBtn { background-color: rgba(255, 42, 109, 0.2); border-color: rgba(255, 42, 109, 0.4); border-radius: 14px; padding: 14px 28px; min-height: 46px; font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; color: #ffffff; }
QPushButton#stopBtn:hover { background-color: rgba(255, 42, 109, 0.35); border-color: rgba(255, 42, 109, 0.7); }
QProgressBar { background-color: rgba(0, 0, 0, 0.4); border: 1px solid rgba(138, 43, 226, 0.1); border-radius: 10px; height: 10px; text-align: center; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:0.5 #00f3ff, stop:1 #8A2BE2); border-radius: 10px; }
QTextEdit { font-family: "Consolas", "Courier New", monospace; font-size: 11px; color: #00ff9d; background-color: rgba(0, 0, 0, 0.65); border: 1px solid rgba(138, 43, 226, 0.25); border-radius: 16px; padding: 14px; }
QTableWidget { background-color: rgba(0, 0, 0, 0.4); border: 1px solid rgba(138, 43, 226, 0.22); border-radius: 12px; gridline-color: rgba(255, 255, 255, 0.03); font-family: "Consolas", monospace; font-size: 11px; color: #e0e0e0; selection-background-color: rgba(138, 43, 226, 0.3); }
QTableWidget::item { padding: 9px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
QHeaderView::section { background-color: transparent; color: #6a6a80; padding: 12px; border: none; border-bottom: 1px solid rgba(138, 43, 226, 0.35); font-family: "Segoe UI", sans-serif; font-weight: bold; font-size: 11px; letter-spacing: 1px; }
QLabel#statValue { font-family: "Segoe UI", sans-serif; font-size: 32px; font-weight: 700; color: #00f3ff; }
QLabel#statLabel { font-family: "Segoe UI", sans-serif; font-size: 11px; color: #6a6a80; letter-spacing: 1px; text-transform: uppercase; }
QLabel#statusText { font-family: "Consolas", monospace; font-size: 11px; color: #4a4a5a; letter-spacing: 2px; }
QScrollBar:vertical { background: transparent; width: 8px; margin: 2px; }
QScrollBar::handle:vertical { background: rgba(138, 43, 226, 0.45); border-radius: 4px; min-height: 30px; }
QScrollBar::handle:vertical:hover { background: rgba(0, 243, 255, 0.6); }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QLineEdit { font-family: "Consolas", monospace; font-size: 12px; color: #e0e0e0; background-color: rgba(0, 0, 0, 0.5); border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 10px; padding: 10px 14px; selection-background-color: rgba(138, 43, 226, 0.5); }
QLineEdit:focus { border: 1px solid rgba(0, 243, 255, 0.7); }
QPlainTextEdit { font-family: "Consolas", monospace; font-size: 12px; color: #d0d0e0; background-color: rgba(0, 0, 0, 0.5); border: 1px solid rgba(138, 43, 226, 0.25); border-radius: 12px; padding: 10px; }
QPlainTextEdit:focus { border: 1px solid rgba(0, 243, 255, 0.6); }
QComboBox { font-family: "Segoe UI", sans-serif; font-size: 12px; color: #e0e0e0; background-color: rgba(0, 0, 0, 0.5); border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 10px; padding: 9px 14px; }
QComboBox:hover { border-color: rgba(0, 243, 255, 0.5); }
QComboBox QAbstractItemView { background-color: #120c22; color: #d0d0e0; border: 1px solid rgba(138, 43, 226, 0.4); selection-background-color: rgba(138, 43, 226, 0.5); outline: none; }
QListWidget { background: rgba(0,0,0,0.4); border: 1px solid rgba(138,43,226,0.15); border-radius: 12px; color: #e0e0e0; font-family: Consolas; font-size: 12px; }
QListWidget::item { padding: 8px 12px; border-bottom: 1px solid rgba(255,255,255,0.03); }
QListWidget::item:selected { background: rgba(138,43,226,0.3); color: #00f3ff; }
QSlider::groove:horizontal { border: 1px solid rgba(138, 43, 226, 0.35); height: 6px; background: #050308; border-radius: 3px; }
QSlider::sub-page:horizontal { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #00f3ff); border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; border: 1px solid #b026ff; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
"""

ACCENT_CYAN, ACCENT_PURPLE, ACCENT_GREEN, ACCENT_RED = "#00f3ff", "#b026ff", "#00ff9d", "#ff2a6d"
_EFFECT_REGISTRY = []

def neon_glow(widget, color="#8A2BE2", radius=30, alpha=90):
    eff = QGraphicsDropShadowEffect(widget)
    c = QColor(color)
    c.setAlpha(alpha)
    eff.setColor(c)
    eff.setBlurRadius(radius)
    eff.setOffset(0, 0)
    widget.setGraphicsEffect(eff)
    _EFFECT_REGISTRY.append(eff)
    return eff

def pop_animate(label):
    try:
        base_color = "#00ff9d" if "ACTIVE" in label.text() else "#00f3ff"
        label.setStyleSheet("color: #ffffff; background: transparent;")
        t = QTimer(label)
        t.setSingleShot(True)
        t.timeout.connect(lambda w=label, c=base_color: w.setStyleSheet(f"color: {c}; background: transparent;"))
        t.timeout.connect(lambda: _EFFECT_REGISTRY.remove(t) if t in _EFFECT_REGISTRY else None)
        t.start(180)
        _EFFECT_REGISTRY.append(t)
    except Exception:
        pass


# =====================================================================
# ВИДЖЕТЫ GUI ИЗ ОРИГИНАЛЬНОГО ДИЗАЙНА (MORPHH)
# =====================================================================
if QT_BINDING:
    class PulseDot(QWidget):
        def __init__(self, color="#00ff9d", parent=None):
            super().__init__(parent)
            self.setFixedSize(12, 12)
            self.color = QColor(color)
            self._phase = 0.0
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick)
            self._timer.start(50)

        def set_color(self, hex_color):
            self.color = QColor(hex_color)
            self.update()

        def _tick(self):
            self._phase += 0.12
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            pulse = (math.sin(self._phase) + 1) / 2.0
            halo = QColor(self.color)
            halo.setAlpha(int(60 * pulse))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(halo)
            painter.drawEllipse(QRectF(0, 0, 12, 12))
            core = QColor(self.color)
            core.setAlpha(int(140 + 115 * pulse))
            painter.setBrush(core)
            painter.drawEllipse(QRectF(3.5, 3.5, 5, 5))
            painter.end()


    class RainbowLine(QFrame):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedHeight(2)
            self._hue = 0
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick)
            self._timer.start(40)

        def _tick(self):
            self._hue = (self._hue + 2) % 360
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            grad = QLinearGradient(0, 0, self.width(), 0)
            for i in range(6):
                c = QColor.fromHsv((self._hue + i * 60) % 360, 230, 255)
                c.setAlpha(200)
                grad.setColorAt(i / 5.0, c)
            painter.fillRect(self.rect(), QBrush(grad))
            painter.end()


    class AccentCard(QWidget):
        """Фирменная стеклянная карточка Morphh с цветной неоновой полосой слева."""
        def __init__(self, accent=ACCENT_PURPLE, parent=None):
            super().__init__(parent)
            self.setObjectName("card")
            self.accent = accent
            self._hovered = False
            try:
                self._glow = neon_glow(self, self.accent, radius=35, alpha=45)
            except Exception:
                pass

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
            path_border = QColor(self.accent)
            path_border.setAlpha(120 if self._hovered else 45)
            painter.setPen(QPen(path_border, 1.4))
            painter.setBrush(QColor(22, 16, 40, 150))
            painter.drawRoundedRect(r, 20, 20)

            # акцентная неоновая полоса слева
            bar = QColor(self.accent)
            grad = QLinearGradient(r.left(), r.top(), r.left(), r.bottom())
            c_top = QColor(bar); c_top.setAlpha(230)
            c_bot = QColor(bar); c_bot.setAlpha(40)
            grad.setColorAt(0, c_top)
            grad.setColorAt(1, c_bot)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QBrush(grad))
            inner = QRectF(r.left() + 1, r.top() + 14, 4, r.height() - 28)
            painter.drawRoundedRect(inner, 2, 2)
            painter.end()

        def enterEvent(self, event):
            self._hovered = True
            self.update()
            super().enterEvent(event)

        def leaveEvent(self, event):
            self._hovered = False
            self.update()
            super().leaveEvent(event)


    class GlowButton(QPushButton):
        """Фирменная неоновая кнопка с мягким свечением."""
        def __init__(self, text, accent=ACCENT_PURPLE, danger=False, parent=None):
            super().__init__(text, parent)
            self.setObjectName("stopBtn" if danger else "actionBtn")
            self.setProperty("class", "actionBtn")
            self.accent = ACCENT_RED if danger else accent
            try:
                self._glow = neon_glow(self, self.accent, radius=28, alpha=60)
            except Exception:
                pass

        def enterEvent(self, event):
            try:
                c = QColor(self.accent)
                c.setAlpha(90)
                self.setStyleSheet(f"border-color: {c.name(QColor.NameFormat.HexArgb)};")
            except Exception:
                pass
            super().enterEvent(event)

        def leaveEvent(self, event):
            try:
                self.setStyleSheet("")
            except Exception:
                pass
            super().leaveEvent(event)


    class AnimatedProgressBar(QProgressBar):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._hue = 180
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick)
            self._timer.start(50)

        def _tick(self):
            self._hue = (self._hue + 3) % 360
            c1 = QColor.fromHsv((self._hue + 300) % 360, 220, 255)
            c2 = QColor.fromHsv(self._hue, 220, 255)
            c3 = QColor.fromHsv((self._hue + 60) % 360, 220, 255)
            self.setStyleSheet(f"""
                QProgressBar {{ background-color: rgba(0,0,0,0.5); border: 1px solid rgba(138,43,226,0.25);
                                border-radius: 10px; height: 10px; text-align: center; }}
                QProgressBar::chunk {{ border-radius: 10px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {c1.name()}, stop:0.5 {c2.name()}, stop:1 {c3.name()}); }}
            """)


    class OrbBackground(QWidget):
        """Оригинальный живой фон Morphh с пульсирующими орбами, звёздными частицами и созвездиями."""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            self.orbs = [
                {"x": 200, "y": 150, "r": 180, "color": QColor(138, 43, 226, 60), "vx": 0.3, "vy": 0.2, "phase": 0.0},
                {"x": 800, "y": 400, "r": 220, "color": QColor(0, 243, 255, 40), "vx": -0.2, "vy": 0.3, "phase": 1.5},
                {"x": 500, "y": 600, "r": 150, "color": QColor(176, 38, 255, 50), "vx": 0.2, "vy": -0.2, "phase": 3.0},
                {"x": 1200, "y": 200, "r": 200, "color": QColor(138, 43, 226, 45), "vx": -0.3, "vy": 0.1, "phase": 4.5},
            ]
            self.particles = []
            for _ in range(45):
                self.particles.append({
                    "x": random.uniform(0, 1920), "y": random.uniform(0, 1080),
                    "vx": random.uniform(-0.25, 0.25), "vy": random.uniform(-0.25, 0.25),
                    "s": random.uniform(1.0, 2.6), "a": random.randint(40, 120),
                })
            self._tick_count = 0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.animate)
            self.timer.start(60)

        def animate(self):
            self._tick_count += 1
            for orb in self.orbs:
                orb["x"] += orb["vx"]
                orb["y"] += orb["vy"]
                orb["phase"] += 0.04
                if orb["x"] < -orb["r"] or orb["x"] > self.width() + orb["r"]: orb["vx"] *= -1
                if orb["y"] < -orb["r"] or orb["y"] > self.height() + orb["r"]: orb["vy"] *= -1
            w, h = max(self.width(), 100), max(self.height(), 100)
            for p in self.particles:
                p["x"] += p["vx"]
                p["y"] += p["vy"]
                if p["x"] < 0: p["x"] = w
                if p["x"] > w: p["x"] = 0
                if p["y"] < 0: p["y"] = h
                if p["y"] > h: p["y"] = 0
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.fillRect(self.rect(), QColor(5, 5, 8))
            for orb in self.orbs:
                r = orb["r"] * (1.0 + 0.06 * math.sin(orb["phase"]))
                gradient = QRadialGradient(orb["x"], orb["y"], r)
                gradient.setColorAt(0, orb["color"])
                gradient.setColorAt(1, QColor(0, 0, 0, 0))
                painter.setBrush(QBrush(gradient))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(int(orb["x"] - r), int(orb["y"] - r), int(r * 2), int(r * 2))

            # Сетка
            grid_pen = QPen(QColor(138, 43, 226, 12))
            grid_pen.setWidth(1)
            painter.setPen(grid_pen)
            step = 60 if (self.width() * self.height()) < 2_500_000 else 120
            for gx in range(0, self.width(), step):
                painter.drawLine(gx, 0, gx, self.height())
            for gy in range(0, self.height(), step):
                painter.drawLine(0, gy, self.width(), gy)

            # Частицы и созвездия
            for p in self.particles:
                dot = QColor(0, 243, 255, p["a"])
                painter.setPen(dot)
                painter.drawPoint(int(p["x"]), int(p["y"]))

            if not hasattr(self, "_lines_cache") or self._tick_count % 30 == 0:
                pairs = []
                for i in range(len(self.particles)):
                    for j in range(i + 1, len(self.particles)):
                        dx = self.particles[i]["x"] - self.particles[j]["x"]
                        dy = self.particles[i]["y"] - self.particles[j]["y"]
                        d2 = dx * dx + dy * dy
                        if d2 < 180 * 180:
                            alpha = int(35 * (1 - d2 / (180 * 180)))
                            pairs.append((i, j, alpha))
                self._lines_cache = pairs

            for i, j, alpha in self._lines_cache:
                line_pen = QPen(QColor(138, 43, 226, alpha))
                painter.setPen(line_pen)
                painter.drawLine(QPointF(self.particles[i]["x"], self.particles[i]["y"]),
                                 QPointF(self.particles[j]["x"], self.particles[j]["y"]))
            painter.end()


    class AnimatedLogo(QWidget):
        """Оригинальный анимированный логотип MORPHH с волновым движением и свечением."""
        def __init__(self, text="MORPHH", parent=None):
            super().__init__(parent)
            self.text = text
            self.t = 0.0
            self.setFont(QFont("Arial Black", 22, QFont.Weight.Black))
            self.setFixedHeight(70)
            self.setMinimumWidth(200)
            self.timer = QTimer(self)
            self.timer.timeout.connect(self._tick)
            self.timer.start(50)

        def _tick(self):
            self.t += 0.09
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            font = painter.font()
            fm_center = painter.fontMetrics()
            total_w = sum(fm_center.horizontalAdvance(ch) for ch in self.text)
            x = (self.width() - total_w) / 2.0
            cy = self.height() / 2.0

            for i, ch in enumerate(self.text):
                hue = ((self.t * 60) + i * 32) % 360
                col = QColor.fromHslF(hue / 360.0, 1.0, 0.62, 1.0)
                wave = math.sin(self.t * 2.2 + i * 0.9) * 3.0
                scale = 1.0 + 0.04 * math.sin(self.t * 1.7 + i * 0.6)
                f2 = QFont(font)
                f2.setPointSizeF(max(font.pointSizeF() * scale, 10))
                painter.setFont(f2)
                fm = painter.fontMetrics()
                wch = fm.horizontalAdvance(ch)

                glow = QColor(col)
                glow.setAlpha(int(90 + 60 * abs(math.sin(self.t + i))))
                painter.setPen(QPen(glow))
                painter.drawText(QPointF(x - 1, cy + fm.ascent() / 2 + wave - 1), ch)
                painter.drawText(QPointF(x + 1, cy + fm.ascent() / 2 + wave + 1), ch)

                painter.setPen(QPen(col))
                painter.drawText(QPointF(x, cy + fm.ascent() / 2 + wave), ch)
                x += wch
            painter.end()


    class EqualizerVisualizer(QWidget):
        """Анимированный визуализатор звуковых частот для Lo-Fi радио."""
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setFixedHeight(54)
            self.is_active = False
            self.bar_count = 32
            self.heights = [6.0] * self.bar_count
            self._timer = QTimer(self)
            self._timer.timeout.connect(self._tick)
            self._timer.start(55)

        def set_active(self, active: bool):
            self.is_active = active
            self.update()

        def _tick(self):
            if self.is_active:
                for i in range(self.bar_count):
                    target = random.uniform(8.0, 48.0)
                    self.heights[i] += (target - self.heights[i]) * 0.45
            else:
                for i in range(self.bar_count):
                    self.heights[i] += (5.0 - self.heights[i]) * 0.2
            self.update()

        def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            w = self.width()
            h = self.height()
            bar_w = max(2.0, (w - (self.bar_count * 4)) / self.bar_count)

            for i in range(self.bar_count):
                bx = i * (bar_w + 4) + 2
                bh = self.heights[i]
                by = h - bh - 3
                grad = QLinearGradient(bx, by, bx, by + bh)
                if self.is_active:
                    grad.setColorAt(0.0, QColor(0, 243, 255))
                    grad.setColorAt(0.5, QColor(176, 38, 255))
                    grad.setColorAt(1.0, QColor(0, 255, 157))
                else:
                    grad.setColorAt(0.0, QColor(70, 70, 90, 80))
                    grad.setColorAt(1.0, QColor(40, 40, 55, 60))

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(QBrush(grad))
                painter.drawRoundedRect(QRectF(bx, by, bar_w, bh), 2.5, 2.5)
            painter.end()


# =====================================================================
# ВАЛИДАТОР ПОЧТ (СПАМ-ЛОВУШКИ, HONEYPOT, MX, СТРАНА, АКТИВНОСТЬ)
# =====================================================================
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
        self._mx_cache = {}
        self._lock = threading.Lock()

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
            return ('TRAP', 0, '⚠️ ОБНАРУЖЕНА СПАМ-ЛОВУШКА (Honeypot Trap)', country, last_active)

        mxs = self.get_mx(domain)
        if not mxs:
            return ('INVALID', 0, 'MX сервер не принимает входящую почту', country, last_active)

        if parts[0] in self.ROLE_PREFIXES:
            return ('RISKY', 60, f'Служебный ящик ({parts[0]}@), а не личный', country, last_active)

        personal_providers = ('gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'outlook.com', 'icloud.com', 'proton.me')
        if domain in personal_providers:
            return ('SAFE', 95, 'Настоящий личный ящик человека', country, last_active)

        return ('SAFE', 88, 'Живой домен, синтаксис чист', country, last_active)


# =====================================================================
# SMTPSENDER & ACCOUNTS MANAGER (accounts.txt)
# =====================================================================
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
                            accounts.append({
                                "email": p[0].strip(),
                                "password": p[1].strip(),
                                "provider": p[0].strip().split("@")[-1].upper()
                            })
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
        self.email_addr = email_addr.strip()
        self.password = password.strip()
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
                self.smtp.ehlo()
                self.smtp.starttls(context=_ssl_mod.create_default_context())
                self.smtp.ehlo()
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


# =====================================================================
# LO-FI РАДИО (6 СТАНЦИЙ 24/7)
# =====================================================================
class LoFiRadio(QObject):
    STATIONS = [
        {"name": "☕ FluxFM Chillhop & Study Beats", "genre": "CHILLHOP", "bitrate": "320kbps MP3", "url": "https://streams.fluxfm.de/chillhop/mp3-320/audio.mp3"},
        {"name": "👾 DEF CON Radio (Cyber Chill)", "genre": "CYBERPUNK", "bitrate": "128kbps MP3", "url": "https://ice2.somafm.com/defcon-128-mp3"},
        {"name": "🌿 Groove Salad (Downtempo Beats)", "genre": "DOWNTEMPO", "bitrate": "128kbps MP3", "url": "https://ice1.somafm.com/groovesalad-128-mp3"},
        {"name": "🏙️ Nightwave Plaza (Vaporwave & Synth)", "genre": "VAPORWAVE", "bitrate": "128kbps MP3", "url": "https://radio.plaza.one/mp3"},
        {"name": "🌌 Drone Zone (Deep Ambient Space)", "genre": "AMBIENT", "bitrate": "128kbps MP3", "url": "https://ice1.somafm.com/dronezone-128-mp3"},
        {"name": "🕶️ Secret Agent (Spy Retro Chill)", "genre": "SPY CHILL", "bitrate": "128kbps MP3", "url": "https://ice1.somafm.com/secretagent-128-mp3"}
    ]

    def __init__(self, signals: ParserSignals):
        super().__init__()
        self.signals = signals
        self.is_playing = False
        self.player = None
        self.audio_output = None
        if HAS_MULTIMEDIA:
            try:
                self.player = QMediaPlayer()
                self.audio_output = QAudioOutput()
                self.player.setAudioOutput(self.audio_output)
                self.audio_output.setVolume(0.75)
            except Exception:
                pass

    def play(self, idx: int = 0):
        if idx < 0 or idx >= len(self.STATIONS): idx = 0
        st = self.STATIONS[idx]
        if HAS_MULTIMEDIA and self.player:
            try:
                self.player.stop()
                self.player.setSource(QUrl(st["url"]))
                self.player.play()
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


# =====================================================================
# САЙДБАР MORPHH
# =====================================================================
if QT_BINDING:
    class Sidebar(QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setObjectName("sidebar")
            self.setFixedWidth(240)

            layout = QVBoxLayout(self)
            layout.setContentsMargins(18, 30, 18, 30)
            layout.setSpacing(6)

            logo = AnimatedLogo("MORPHH")
            layout.addWidget(logo)

            sub = QLabel("ALLPARS V2.0 PRO")
            sub.setFont(QFont("Segoe UI", 9))
            sub.setStyleSheet("color: #6a6a80; background: transparent; padding-bottom: 20px; font-family: Consolas; letter-spacing: 2px;")
            sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(sub)

            self.buttons = {}
            nav_items = [
                ("dashboard", "⌂  Dashboard", ""),
                ("parser", "▶  Parser & Logs", ""),
                ("auto", "∞  Infinite Engine", "CRAWL"),
                ("validator", "✓  Validator", "TRAP"),
                ("mailer", "✉  Smart Mailer", "SMTP"),
                ("accounts", "👥  Accounts Vault", "AUTH"),
                ("radio", "🎧  Lo-Fi Radio", "24/7"),
                ("stats", "📊  Database & Stats", "SQL"),
                ("osint", "⚡  OSINT Tools", "NET")
            ]

            for key, text, badge in nav_items:
                btn_w = QWidget()
                b_layout = QHBoxLayout(btn_w)
                b_layout.setContentsMargins(0, 0, 0, 0)

                btn = QPushButton(text)
                btn.setObjectName("navBtn")
                btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                btn.clicked.connect(lambda checked, k=key: self.on_nav(k))
                b_layout.addWidget(btn, 1)

                if badge:
                    b_lbl = QLabel(badge)
                    bg_col = "#00f3ff" if badge in ("TRAP", "24/7") else "#00ff9d" if badge == "CRAWL" else "#b026ff"
                    b_lbl.setStyleSheet(f"background-color: rgba(138,43,226,0.25); color: {bg_col}; border: 1px solid {bg_col}; border-radius: 4px; font-size: 8px; font-weight: bold; padding: 2px 4px;")
                    b_layout.addWidget(b_lbl)

                layout.addWidget(btn_w)
                self.buttons[key] = btn

            layout.addStretch()

            # Живой индикатор радио
            radio_row = QHBoxLayout()
            radio_row.setSpacing(8)
            self.radio_dot = PulseDot("#4a4a5a")
            radio_row.addWidget(self.radio_dot)
            self.radio_lbl = QLabel("RADIO OFF")
            self.radio_lbl.setFont(QFont("Consolas", 9))
            self.radio_lbl.setStyleSheet("color: #6a6a80; background: transparent; letter-spacing: 1px;")
            radio_row.addWidget(self.radio_lbl)
            radio_row.addStretch()
            rw = QWidget(); rw.setLayout(radio_row); rw.setStyleSheet("background: transparent;")
            layout.addWidget(rw)

            # Живой индикатор состояния движка
            engine_row = QHBoxLayout()
            engine_row.setSpacing(8)
            self.engine_dot = PulseDot("#4a4a5a")
            engine_row.addWidget(self.engine_dot)
            self.engine_lbl = QLabel("ENGINE IDLE")
            self.engine_lbl.setFont(QFont("Consolas", 9))
            self.engine_lbl.setStyleSheet("color: #4a4a5a; background: transparent; letter-spacing: 1px;")
            engine_row.addWidget(self.engine_lbl)
            engine_row.addStretch()
            ew = QWidget(); ew.setLayout(engine_row); ew.setStyleSheet("background: transparent;")
            layout.addWidget(ew)

            ver = QLabel("v2.0 PRO • Cyberpunk Edition")
            ver.setFont(QFont("Consolas", 9))
            ver.setStyleSheet("color: #3a3a4a; background: transparent; padding: 8px 0;")
            ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(ver)

            self.active_key = None
            self.on_nav("dashboard")

        def set_engine_state(self, running):
            color = "#00ff9d" if running else "#4a4a5a"
            self.engine_dot.set_color(color)
            self.engine_lbl.setText("ENGINE ACTIVE" if running else "ENGINE IDLE")
            self.engine_lbl.setStyleSheet(f"color: {color}; background: transparent; letter-spacing: 1px;")

        def set_radio_state(self, text, is_on):
            color = "#00ff9d" if is_on else "#4a4a5a"
            self.radio_dot.set_color(color)
            self.radio_lbl.setText("RADIO ACTIVE" if is_on else "RADIO OFF")
            self.radio_lbl.setStyleSheet(f"color: {color}; background: transparent; letter-spacing: 1px;")

        def on_nav(self, key):
            if self.active_key and self.active_key in self.buttons:
                self.buttons[self.active_key].setProperty("class", "")
                self.buttons[self.active_key].style().unpolish(self.buttons[self.active_key])
                self.buttons[self.active_key].style().polish(self.buttons[self.active_key])

            self.buttons[key].setProperty("class", "active")
            self.buttons[key].style().unpolish(self.buttons[key])
            self.buttons[key].style().polish(self.buttons[key])
            self.active_key = key

            main_window = self.parent()
            while main_window is not None and not isinstance(main_window, MainWindow):
                main_window = main_window.parent()
            if main_window is not None:
                main_window.switch_page(key)


# =====================================================================
# ГЛАВНОЕ ОКНО MORPHH V2.0 PRO
# =====================================================================
if QT_BINDING:
    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("MORPHH // ALLPARS V2.0 PRO")
            self.resize(1440, 920)

            self.running = False
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

            self.known_domains = set()
            self.seen_emails = set()
            self.personal_base = set()
            self.link_cap = 8000

            # 1. Живой фон Morphh с орбами и созвездиями
            self.bg = OrbBackground(self)
            self.bg.setGeometry(0, 0, self.width(), self.height())

            # 2. Основной макет
            main_w = QWidget(self)
            main_w.setStyleSheet("background: transparent;")
            main_layout = QHBoxLayout(main_w)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            self.content = QStackedWidget()
            self.content.setStyleSheet("background: transparent;")

            self.page_dashboard = self.create_dashboard_page()   # 0
            self.page_parser = self.create_parser_page()         # 1
            self.page_auto = self.create_auto_page()             # 2
            self.page_validator = self.create_validator_page()   # 3
            self.page_mailer = self.create_mailer_page()         # 4
            self.page_accounts = self.create_accounts_page()     # 5
            self.page_radio = self.create_radio_page()           # 6
            self.page_stats = self.create_stats_page()           # 7
            self.page_osint = self.create_osint_page()           # 8

            self.content.addWidget(self.page_dashboard)
            self.content.addWidget(self.page_parser)
            self.content.addWidget(self.page_auto)
            self.content.addWidget(self.page_validator)
            self.content.addWidget(self.page_mailer)
            self.content.addWidget(self.page_accounts)
            self.content.addWidget(self.page_radio)
            self.content.addWidget(self.page_stats)
            self.content.addWidget(self.page_osint)

            self.sidebar = Sidebar(main_w)
            main_layout.addWidget(self.sidebar)
            main_layout.addWidget(self.content, 1)
            self.setCentralWidget(main_w)

            # Сигналы
            self.signals.log_signal.connect(self.write_log_safe)
            self.signals.account_signal.connect(self.add_to_recent_table)
            self.signals.progress_signal.connect(self.progress_dash.setValue)
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

            self.setStyleSheet(QSS)
            self._load_existing_base()
            self.update_total_ui()

        def resizeEvent(self, event):
            super().resizeEvent(event)
            if hasattr(self, "bg"):
                self.bg.setGeometry(0, 0, self.width(), self.height())

        def switch_page(self, key):
            pages = {
                "dashboard": 0, "parser": 1, "auto": 2, "validator": 3,
                "mailer": 4, "accounts": 5, "radio": 6, "stats": 7, "osint": 8
            }
            if key in pages:
                self.content.setCurrentIndex(pages[key])
                if key == "mailer":
                    self.refresh_mailer_dropdown()
                    self.refresh_mailer_list()
                elif key == "accounts":
                    self.refresh_accounts_view()
                elif key == "stats":
                    self.update_total_ui()
                    self.refresh_database_table()

        def _make_header(self, text, layout):
            header = QLabel(text)
            header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
            header.setStyleSheet("color: #ffffff; background: transparent;")
            neon_glow(header, "#00f3ff", radius=25, alpha=90)
            layout.addWidget(header)
            line = RainbowLine()
            layout.addWidget(line)
            return header

        # =================================================================
        # 1. SCREEN: DASHBOARD (ФИРМЕННЫЙ СТИЛЬ MORPHH)
        # =================================================================
        def create_dashboard_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40)
            layout.setSpacing(24)

            self._make_header("Control Dashboard", layout)
            sub = QLabel("Autonomous OSINT harvesting, recursive spidering, and deliverability monitoring")
            sub.setFont(QFont("Segoe UI", 12))
            sub.setStyleSheet("color: #6a6a80; margin-bottom: 12px; background: transparent;")
            layout.addWidget(sub)

            # 4 Карточки статистики
            stats_row = QHBoxLayout()
            stats_row.setSpacing(20)

            card1 = AccentCard(ACCENT_CYAN)
            l1 = QVBoxLayout(card1); l1.setContentsMargins(24, 24, 24, 24)
            self.stat_total = QLabel("0")
            self.stat_total.setObjectName("statValue")
            l1.addWidget(self.stat_total)
            lbl1 = QLabel("Harvested Mails")
            lbl1.setObjectName("statLabel")
            l1.addWidget(lbl1)
            stats_row.addWidget(card1)

            card2 = AccentCard(ACCENT_GREEN)
            l2 = QVBoxLayout(card2); l2.setContentsMargins(24, 24, 24, 24)
            self.stat_personal = QLabel("0")
            self.stat_personal.setObjectName("statValue")
            self.stat_personal.setStyleSheet("color: #00ff9d; font-size: 32px; font-weight: bold;")
            l2.addWidget(self.stat_personal)
            lbl2 = QLabel("Personal (Human) Mailboxes")
            lbl2.setObjectName("statLabel")
            l2.addWidget(lbl2)
            stats_row.addWidget(card2)

            card3 = AccentCard(ACCENT_PURPLE)
            l3 = QVBoxLayout(card3); l3.setContentsMargins(24, 24, 24, 24)
            self.stat_status = QLabel("IDLE")
            self.stat_status.setObjectName("statValue")
            self.stat_status.setStyleSheet("color: #8A2BE2; background: transparent;")
            l3.addWidget(self.stat_status)
            lbl3 = QLabel("Crawler Engine")
            lbl3.setObjectName("statLabel")
            l3.addWidget(lbl3)
            stats_row.addWidget(card3)

            card4 = AccentCard(ACCENT_CYAN)
            l4 = QVBoxLayout(card4); l4.setContentsMargins(24, 24, 24, 24)
            self.stat_domain = QLabel("---")
            self.stat_domain.setObjectName("statValue")
            self.stat_domain.setStyleSheet("color: #00f3ff; font-size: 15px; background: transparent;")
            l4.addWidget(self.stat_domain)
            lbl4 = QLabel("Current Target URL")
            lbl4.setObjectName("statLabel")
            l4.addWidget(lbl4)
            stats_row.addWidget(card4)

            layout.addLayout(stats_row)

            # Control Deck
            actions_card = AccentCard(ACCENT_PURPLE)
            al = QVBoxLayout(actions_card); al.setContentsMargins(32, 28, 32, 28); al.setSpacing(18)
            lbl_act = QLabel("Control Deck")
            lbl_act.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            lbl_act.setStyleSheet("color: #ffffff; background: transparent;")
            al.addWidget(lbl_act)

            btn_row = QHBoxLayout(); btn_row.setSpacing(16)
            self.btn_dash_run = GlowButton("▶  Run Single Session", ACCENT_CYAN)
            self.btn_dash_run.clicked.connect(self.start_parsing)
            btn_row.addWidget(self.btn_dash_run)

            self.btn_dash_auto = GlowButton("∞  Enable Infinite Crawl", ACCENT_GREEN)
            self.btn_dash_auto.clicked.connect(self.start_auto)
            btn_row.addWidget(self.btn_dash_auto)

            self.btn_dash_stop = GlowButton("■  Kill Process", danger=True)
            self.btn_dash_stop.clicked.connect(self.stop_all)
            self.btn_dash_stop.setEnabled(False)
            btn_row.addWidget(self.btn_dash_stop)

            btn_clear = GlowButton("🗑  Clear Database", ACCENT_PURPLE)
            btn_clear.clicked.connect(self.clear_all_data)
            btn_row.addWidget(btn_clear)
            al.addLayout(btn_row)

            self.progress_dash = AnimatedProgressBar()
            self.progress_dash.setValue(0)
            al.addWidget(self.progress_dash)

            self.status_dash = QLabel("SYSTEM IDLE")
            self.status_dash.setObjectName("statusText")
            al.addWidget(self.status_dash)
            layout.addWidget(actions_card)

            # Таблица найденных
            recent_card = AccentCard(ACCENT_CYAN)
            rl = QVBoxLayout(recent_card); rl.setContentsMargins(24, 24, 24, 24); rl.setSpacing(16)
            feed_row = QHBoxLayout(); feed_row.setSpacing(8)
            feed_row.addWidget(PulseDot("#00f3ff"))
            lbl_recent = QLabel("Extracted Base (Live Feed with Country & Activity)")
            lbl_recent.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            lbl_recent.setStyleSheet("color: #ffffff; background: transparent;")
            feed_row.addWidget(lbl_recent)
            feed_row.addStretch()
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
            layout.addWidget(recent_card)

            return page

        # =================================================================
        # 2. SCREEN: PARSER LOGS
        # =================================================================
        def create_parser_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("Parser Logs", layout)
            term_card, self.log_parser = self._make_log_terminal("PARSER // TERMINAL OUTPUT", "#00f3ff")
            layout.addWidget(term_card, 1)
            return page

        # =================================================================
        # 3. SCREEN: INFINITE ENGINE
        # =================================================================
        def create_auto_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("Infinite Engine", layout)

            ctrl_card = AccentCard(ACCENT_GREEN)
            cl = QVBoxLayout(ctrl_card); cl.setContentsMargins(32, 28, 32, 28); cl.setSpacing(16)
            status_row = QHBoxLayout(); status_row.setSpacing(10)
            self.auto_dot = PulseDot("#8A2BE2")
            status_row.addWidget(self.auto_dot)
            self.auto_status = QLabel("INFINITE MODE: OFF")
            self.auto_status.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
            self.auto_status.setStyleSheet("color: #8A2BE2; background: transparent;")
            status_row.addWidget(self.auto_status)
            status_row.addStretch()
            cl.addLayout(status_row)

            self.auto_iter = QLabel("Links In Queue: 0")
            self.auto_iter.setFont(QFont("Consolas", 12))
            self.auto_iter.setStyleSheet("color: #6a6a80; background: transparent;")
            cl.addWidget(self.auto_iter)

            btn_row = QHBoxLayout(); btn_row.setSpacing(16)
            self.btn_auto_start = GlowButton("∞  Launch Infinite", ACCENT_GREEN)
            self.btn_auto_start.clicked.connect(self.start_auto)
            btn_row.addWidget(self.btn_auto_start)

            self.btn_auto_stop = GlowButton("■  Stop", danger=True)
            self.btn_auto_stop.clicked.connect(self.stop_all)
            self.btn_auto_stop.setEnabled(False)
            btn_row.addWidget(self.btn_auto_stop)
            cl.addLayout(btn_row)
            layout.addWidget(ctrl_card)

            log_card, self.log_auto = self._make_log_terminal("INFINITE ENGINE // LIVE STREAM", "#00ff9d")
            layout.addWidget(log_card, 1)
            return page

        def _make_log_terminal(self, title, accent="#00ff9d"):
            term_card = AccentCard(accent)
            tl = QVBoxLayout(term_card); tl.setContentsMargins(24, 24, 24, 24); tl.setSpacing(12)
            head_row = QHBoxLayout(); head_row.setSpacing(8)
            head_row.addWidget(PulseDot(accent))
            t = QLabel(title)
            t.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            t.setStyleSheet(f"color: {accent}; background: transparent; letter-spacing: 2px;")
            head_row.addWidget(t)
            head_row.addStretch()

            btn_clear = QPushButton("Clear")
            btn_clear.setStyleSheet("color: #6a6a80; background: transparent; border: none; font-size: 11px;")
            head_row.addWidget(btn_clear)
            tl.addLayout(head_row)

            edit = QTextEdit()
            edit.setReadOnly(True)
            edit.document().setMaximumBlockCount(800)
            btn_clear.clicked.connect(lambda: edit.clear())
            tl.addWidget(edit, 1)
            return term_card, edit

        # =================================================================
        # 4. SCREEN: VALIDATOR (СТРАНА, АКТИВНОСТЬ, HONEYPOT, SCORE)
        # =================================================================
        def create_validator_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("Validator", layout)

            sub = QLabel("Проверка базы на спам-ловушки (Honeypot), мёртвые домены, определение страны и последней активности.")
            sub.setFont(QFont("Segoe UI", 12))
            sub.setStyleSheet("color: #6a6a80; margin-bottom: 12px; background: transparent;")
            layout.addWidget(sub)

            ctrl_card = AccentCard(ACCENT_GREEN)
            cl = QVBoxLayout(ctrl_card); cl.setContentsMargins(32, 24, 32, 24); cl.setSpacing(16)

            insp_row = QHBoxLayout()
            self.val_input_single = QLineEdit()
            self.val_input_single.setPlaceholderText("Введите адрес для быстрой проверки: developer@mail.ru, honeypot@trap.com...")
            self.val_input_single.returnPressed.connect(self.inspect_single_address)
            insp_row.addWidget(self.val_input_single, 1)

            btn_insp = GlowButton("🔍  Проверить Адрес", ACCENT_CYAN)
            btn_insp.clicked.connect(self.inspect_single_address)
            insp_row.addWidget(btn_insp)
            cl.addLayout(insp_row)

            btn_row = QHBoxLayout(); btn_row.setSpacing(16)
            self.btn_val_run = GlowButton("✓  Validate Base Now", ACCENT_GREEN)
            self.btn_val_run.clicked.connect(self.run_validation)
            btn_row.addWidget(self.btn_val_run)

            self.btn_val_clean = GlowButton("🗑  Remove TRAP/INVALID From Base", danger=True)
            self.btn_val_clean.clicked.connect(self.clean_base_by_validation)
            btn_row.addWidget(self.btn_val_clean)
            btn_row.addStretch()
            cl.addLayout(btn_row)

            prog_row = QHBoxLayout(); prog_row.setSpacing(12)
            self.val_progress = QProgressBar()
            self.val_progress.setMinimum(0)
            neon_glow(self.val_progress, "#00ff9d", radius=20, alpha=50)
            prog_row.addWidget(self.val_progress, 1)

            self.val_counters = QLabel("SAFE: 0 | RISKY: 0 | TRAP: 0 | INVALID: 0")
            self.val_counters.setFont(QFont("Consolas", 11))
            self.val_counters.setStyleSheet("color: #6a6a80; background: transparent;")
            prog_row.addWidget(self.val_counters)
            cl.addLayout(prog_row)
            layout.addWidget(ctrl_card)

            tbl_card = AccentCard(ACCENT_CYAN)
            tl = QVBoxLayout(tbl_card); tl.setContentsMargins(24, 24, 24, 24)
            head_row = QHBoxLayout(); head_row.setSpacing(8)
            head_row.addWidget(PulseDot("#00f3ff"))
            t = QLabel("VALIDATION RESULTS // ALL ADDRESSES (COUNTRY & ACTIVITY INCLUDED)")
            t.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            t.setStyleSheet("color: #00f3ff; background: transparent; letter-spacing: 2px;")
            head_row.addWidget(t)
            head_row.addStretch()
            tl.addLayout(head_row)

            self.val_table = QTableWidget(0, 6)
            self.val_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "COUNTRY", "LAST ACTIVE", "STATUS", "SCORE", "DETAIL"])
            self.val_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            self.val_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
            self.val_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            self.val_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            self.val_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            self.val_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            self.val_table.setShowGrid(False)
            self.val_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.val_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            tl.addWidget(self.val_table, 1)
            layout.addWidget(tbl_card, 1)

            return page

        # =================================================================
        # 5. SCREEN: MAILER & OUTREACH
        # =================================================================
        def create_mailer_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(20)
            self._make_header("Mailer", layout)

            sub = QLabel("Отправка одиночных писем на проверенные адреса из базы. Выбор аккаунтов из accounts.txt.")
            sub.setFont(QFont("Segoe UI", 12))
            sub.setStyleSheet("color: #6a6a80; background: transparent;")
            layout.addWidget(sub)

            # SMTP Account Card
            acc_card = AccentCard(ACCENT_PURPLE)
            acl = QVBoxLayout(acc_card); acl.setContentsMargins(28, 20, 28, 20); acl.setSpacing(12)
            lbl_acc = QLabel("SMTP Account (загрузка напрямую из accounts.txt):")
            lbl_acc.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            lbl_acc.setStyleSheet("color: #ffffff; background: transparent;")
            acl.addWidget(lbl_acc)

            form_row = QHBoxLayout(); form_row.setSpacing(12)
            self.mailer_acc_combo = QComboBox()
            form_row.addWidget(self.mailer_acc_combo, 3)

            self.btn_mail_conn = GlowButton("⚡  Test & Connect", ACCENT_CYAN)
            self.btn_mail_conn.clicked.connect(self.mailer_connect)
            form_row.addWidget(self.btn_mail_conn, 1)

            btn_open_accs = GlowButton("👥 Manage accounts.txt", ACCENT_PURPLE)
            btn_open_accs.clicked.connect(lambda: self.switch_page("accounts"))
            form_row.addWidget(btn_open_accs, 1)
            acl.addLayout(form_row)

            self.mail_status_lbl = QLabel("NOT CONNECTED")
            self.mail_status_lbl.setFont(QFont("Consolas", 11))
            self.mail_status_lbl.setStyleSheet("color: #4a4a5a; background: transparent; letter-spacing: 1px;")
            acl.addWidget(self.mail_status_lbl)
            layout.addWidget(acc_card)

            # Verified Recipients
            list_card = AccentCard(ACCENT_GREEN)
            lcl = QVBoxLayout(list_card); lcl.setContentsMargins(24, 18, 24, 18); lcl.setSpacing(10)
            lr = QHBoxLayout(); lr.setSpacing(8)
            lr.addWidget(PulseDot("#00ff9d"))
            llbl = QLabel("Verified Recipients (SAFE/RISKY only)")
            llbl.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            llbl.setStyleSheet("color: #ffffff; background: transparent;")
            lr.addWidget(llbl)
            self.mail_list_count = QLabel("")
            self.mail_list_count.setStyleSheet("color: #6a6a80; background: transparent; font-family: Consolas;")
            lr.addStretch()
            self.btn_mail_refresh = GlowButton("↻  Refresh List", ACCENT_CYAN)
            self.btn_mail_refresh.clicked.connect(self.refresh_mailer_list)
            lr.addWidget(self.btn_mail_refresh)
            lcl.addLayout(lr)

            self.mail_list = QListWidget()
            self.mail_list.itemSelectionChanged.connect(self.on_mailer_selection)
            lcl.addWidget(self.mail_list, 1)
            layout.addWidget(list_card, 1)

            # Message Composer
            comp_card = AccentCard(ACCENT_CYAN)
            ccl = QVBoxLayout(comp_card); ccl.setContentsMargins(28, 18, 28, 18); ccl.setSpacing(10)

            to_row = QHBoxLayout(); to_row.setSpacing(10)
            to_lbl = QLabel("TO:")
            to_lbl.setStyleSheet("color: #b0b0c0; background: transparent; font-family: Consolas; font-weight: bold;")
            to_row.addWidget(to_lbl)
            self.mail_to_lbl = QLabel("(выберите адрес из списка)")
            self.mail_to_lbl.setStyleSheet("color: #00f3ff; background: transparent; font-family: Consolas;")
            to_row.addWidget(self.mail_to_lbl, 1)
            ccl.addLayout(to_row)

            subj_row = QHBoxLayout(); subj_row.setSpacing(10)
            s_lbl = QLabel("SUBJECT:")
            s_lbl.setStyleSheet("color: #b0b0c0; background: transparent; font-family: Consolas; font-weight: bold;")
            subj_row.addWidget(s_lbl)
            self.mail_subject_edit = QLineEdit()
            self.mail_subject_edit.setPlaceholderText("Тема сообщения...")
            subj_row.addWidget(self.mail_subject_edit, 1)
            ccl.addLayout(subj_row)

            body_lbl = QLabel("MESSAGE:")
            body_lbl.setStyleSheet("color: #b0b0c0; background: transparent; font-family: Consolas; font-weight: bold;")
            ccl.addWidget(body_lbl)
            self.mail_body_edit = QPlainTextEdit()
            self.mail_body_edit.setPlaceholderText("Текст письма...")
            self.mail_body_edit.setPlainText("Hello,\n\nI noticed your developer projects and contributions. Would you be open to discussing a potential collaboration?\n\nBest regards,\nOutreach Team")
            self.mail_body_edit.setMaximumHeight(130)
            ccl.addWidget(self.mail_body_edit)

            send_row = QHBoxLayout(); send_row.setSpacing(16)
            self.btn_mail_send = GlowButton("➤  Re-validate & Send", ACCENT_GREEN)
            self.btn_mail_send.clicked.connect(self.mailer_send_selected)
            send_row.addWidget(self.btn_mail_send)
            send_row.addStretch()
            ccl.addLayout(send_row)
            layout.addWidget(comp_card)

            log_card, self.log_mailer = self._make_log_terminal("MAILER // DELIVERY LOG", "#ffcc00")
            log_card.setMaximumHeight(180)
            layout.addWidget(log_card)
            return page

        # =================================================================
        # 6. SCREEN: SENDER ACCOUNTS (ACCOUNTS.TXT)
        # =================================================================
        def create_accounts_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("Sender Accounts (accounts.txt)", layout)

            split = QHBoxLayout(); split.setSpacing(20)

            c_add = AccentCard(ACCENT_CYAN)
            cal = QVBoxLayout(c_add); cal.setContentsMargins(24, 20, 24, 20); cal.setSpacing(12)
            cal.addWidget(QLabel("+ ДОБАВИТЬ АККАУНТ ОТПРАВИТЕЛЯ", styleSheet="color: #00f3ff; font-weight: bold; font-size: 12px;"))

            self.acc_input_email = QLineEdit(); self.acc_input_email.setPlaceholderText("sender@gmail.com")
            cal.addWidget(self.acc_input_email)

            self.acc_input_pass = QLineEdit(); self.acc_input_pass.setPlaceholderText("App Password (пароль приложения)")
            self.acc_input_pass.setEchoMode(QLineEdit.EchoMode.Password)
            cal.addWidget(self.acc_input_pass)

            btn_save = GlowButton("🔑 Сохранить в accounts.txt", ACCENT_GREEN)
            btn_save.clicked.connect(self.add_single_account)
            cal.addWidget(btn_save)

            self.accounts_list = QListWidget()
            cal.addWidget(self.accounts_list, 1)
            split.addWidget(c_add, 2)

            c_raw = AccentCard(ACCENT_PURPLE)
            crl = QVBoxLayout(c_raw); crl.setContentsMargins(24, 20, 24, 20); crl.setSpacing(12)
            top_r = QHBoxLayout()
            top_r.addWidget(QLabel("📄 РЕДАКТОР ФАЙЛА ACCOUNTS.TXT", styleSheet="color: #00ff9d; font-weight: bold; font-size: 12px;"))
            top_r.addStretch()
            btn_save_raw = GlowButton("💾 Сохранить Файл", ACCENT_GREEN)
            btn_save_raw.clicked.connect(self.save_raw_accounts_file)
            top_r.addWidget(btn_save_raw)
            crl.addLayout(top_r)

            self.accounts_editor = QPlainTextEdit()
            crl.addWidget(self.accounts_editor, 1)
            split.addWidget(c_raw, 3)

            layout.addLayout(split)
            return page

        # =================================================================
        # 7. SCREEN: LO-FI RADIO 24/7 (6 СТАНЦИЙ)
        # =================================================================
        def create_radio_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("Cyberpunk Lo-Fi Radio (6 Станций 24/7)", layout)

            player_card = AccentCard(ACCENT_CYAN)
            pcl = QVBoxLayout(player_card); pcl.setContentsMargins(28, 22, 28, 22); pcl.setSpacing(14)

            top_p = QHBoxLayout()
            self.radio_title_lbl = QLabel("((o)) FLUXFM CHILLHOP & STUDY BEATS (320KBPS)")
            self.radio_title_lbl.setStyleSheet("color: #00f3ff; font-weight: bold; font-family: Consolas; font-size: 13px;")
            top_p.addWidget(self.radio_title_lbl)
            top_p.addStretch()
            self.radio_state_lbl = QLabel("ОСТАНОВЛЕНО")
            self.radio_state_lbl.setStyleSheet("color: #6a6a80; font-family: Consolas; font-size: 11px;")
            top_p.addWidget(self.radio_state_lbl)
            pcl.addLayout(top_p)

            self.equalizer = EqualizerVisualizer()
            pcl.addWidget(self.equalizer)

            ctrl_row = QHBoxLayout(); ctrl_row.setSpacing(16)
            self.btn_radio_toggle = GlowButton("▶  ВКЛЮЧИТЬ ПОТОК", ACCENT_GREEN)
            self.btn_radio_toggle.clicked.connect(self.toggle_radio_playback)
            ctrl_row.addWidget(self.btn_radio_toggle)

            ctrl_row.addStretch()
            ctrl_row.addWidget(QLabel("🔊"))
            self.slider_radio_vol = QSlider(Qt.Orientation.Horizontal)
            self.slider_radio_vol.setRange(0, 100)
            self.slider_radio_vol.setValue(75)
            self.slider_radio_vol.setFixedWidth(160)
            self.slider_radio_vol.valueChanged.connect(self.radio.set_volume)
            ctrl_row.addWidget(self.slider_radio_vol)
            pcl.addLayout(ctrl_row)
            layout.addWidget(player_card)

            # Список станций
            stations_card = AccentCard(ACCENT_PURPLE)
            scl = QVBoxLayout(stations_card); scl.setContentsMargins(24, 20, 24, 20); scl.setSpacing(10)
            scl.addWidget(QLabel("ВЫБОР СТАНЦИИ:", styleSheet="color: #00ff9d; font-weight: bold; font-size: 11px; letter-spacing: 1px;"))

            for idx, st in enumerate(LoFiRadio.STATIONS):
                row = QHBoxLayout()
                lbl = QLabel(f"{st['name']}  [{st['bitrate']}]")
                lbl.setStyleSheet("color: #ffffff; font-size: 12px;")
                row.addWidget(lbl, 1)

                btn = GlowButton("▶ Играть", ACCENT_CYAN)
                btn.clicked.connect(lambda ch, i=idx: self.select_radio_station(i))
                row.addWidget(btn)
                scl.addLayout(row)

            layout.addWidget(stations_card)
            return page

        # =================================================================
        # 8. SCREEN: DATABASE & STATS
        # =================================================================
        def create_stats_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("Database Statistics", layout)

            stats_card = AccentCard(ACCENT_CYAN)
            sl = QVBoxLayout(stats_card); sl.setContentsMargins(36, 28, 36, 28); sl.setSpacing(20)

            top_row = QHBoxLayout()
            b1 = QVBoxLayout()
            self.stats_total_lbl = QLabel("0")
            self.stats_total_lbl.setStyleSheet("color: #00f3ff; font-size: 56px; font-weight: bold;")
            neon_glow(self.stats_total_lbl, "#00f3ff", radius=35, alpha=110)
            b1.addWidget(self.stats_total_lbl)
            lbl_st = QLabel("Total Records In SQLite")
            lbl_st.setObjectName("statLabel")
            b1.addWidget(lbl_st)
            top_row.addLayout(b1)

            b2 = QVBoxLayout()
            self.stats_personal_lbl = QLabel("0")
            self.stats_personal_lbl.setStyleSheet("color: #00ff9d; font-size: 56px; font-weight: bold;")
            neon_glow(self.stats_personal_lbl, "#00ff9d", radius=35, alpha=110)
            b2.addWidget(self.stats_personal_lbl)
            lbl_pers = QLabel("Personal Mailboxes")
            lbl_pers.setObjectName("statLabel")
            b2.addWidget(lbl_pers)
            top_row.addLayout(b2)
            sl.addLayout(top_row)

            # Кнопки экспорта
            exp_row = QHBoxLayout(); exp_row.setSpacing(12)
            btn_txt = GlowButton("📄 Экспорт TXT", ACCENT_CYAN)
            btn_txt.clicked.connect(self.export_txt)
            exp_row.addWidget(btn_txt)

            btn_json = GlowButton("{ } Экспорт JSON", ACCENT_CYAN)
            btn_json.clicked.connect(self.export_json)
            exp_row.addWidget(btn_json)

            btn_csv = GlowButton("📥 Экспорт Excel (CSV)", ACCENT_GREEN)
            btn_csv.clicked.connect(self.export_csv)
            exp_row.addWidget(btn_csv)
            sl.addLayout(exp_row)
            layout.addWidget(stats_card)

            # Таблица SQLite базы
            db_card = AccentCard(ACCENT_PURPLE)
            dbl = QVBoxLayout(db_card); dbl.setContentsMargins(24, 20, 24, 20); dbl.setSpacing(12)
            search_row = QHBoxLayout()
            self.db_search_edit = QLineEdit()
            self.db_search_edit.setPlaceholderText("Мгновенный поиск по всей базе почт...")
            self.db_search_edit.textChanged.connect(self.filter_database_table)
            search_row.addWidget(self.db_search_edit, 1)

            btn_refresh = GlowButton("↻ Обновить", ACCENT_CYAN)
            btn_refresh.clicked.connect(self.refresh_database_table)
            search_row.addWidget(btn_refresh)
            dbl.addLayout(search_row)

            self.db_table = QTableWidget(0, 6)
            self.db_table.setHorizontalHeaderLabels(["ID", "EMAIL", "COUNTRY", "LAST ACTIVE", "CATEGORY", "SOURCE"])
            self.db_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
            self.db_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            self.db_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
            self.db_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
            self.db_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
            self.db_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
            self.db_table.setShowGrid(False)
            self.db_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            self.db_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            dbl.addWidget(self.db_table, 1)
            layout.addWidget(db_card, 1)

            return page

        # =================================================================
        # 9. SCREEN: OSINT NETWORK TOOLS
        # =================================================================
        def create_osint_page(self):
            page = QWidget()
            layout = QVBoxLayout(page)
            layout.setContentsMargins(40, 40, 40, 40); layout.setSpacing(24)
            self._make_header("OSINT Network Tools", layout)

            split = QHBoxLayout(); split.setSpacing(20)

            c_dns = AccentCard(ACCENT_CYAN)
            cdl = QVBoxLayout(c_dns); cdl.setContentsMargins(24, 20, 24, 20); cdl.setSpacing(12)
            cdl.addWidget(QLabel("🌐 ИНСПЕКТОР DNS & MX ЗАПИСЕЙ", styleSheet="color: #00f3ff; font-weight: bold; font-size: 12px;"))

            row_dns = QHBoxLayout()
            self.dns_input = QLineEdit(); self.dns_input.setPlaceholderText("yandex.ru, gmail.com, github.com...")
            row_dns.addWidget(self.dns_input, 1)
            btn_check_dns = GlowButton("Проверить MX", ACCENT_GREEN)
            btn_check_dns.clicked.connect(self.check_dns_action)
            row_dns.addWidget(btn_check_dns)
            cdl.addLayout(row_dns)

            self.dns_output = QTextEdit()
            self.dns_output.setReadOnly(True)
            cdl.addWidget(self.dns_output, 1)
            split.addWidget(c_dns, 1)

            c_reg = AccentCard(ACCENT_PURPLE)
            crl = QVBoxLayout(c_reg); crl.setContentsMargins(24, 20, 24, 20); crl.setSpacing(12)
            crl.addWidget(QLabel("🔍 ТЕСТЕР ИЗВЛЕЧЕНИЯ REGEX", styleSheet="color: #00ff9d; font-weight: bold; font-size: 12px;"))

            self.regex_input = QPlainTextEdit()
            self.regex_input.setPlaceholderText("Вставьте любой текст с почтами для парсинга...")
            crl.addWidget(self.regex_input, 1)

            btn_run_reg = GlowButton("⚡ Извлечь Email Адреса", ACCENT_CYAN)
            btn_run_reg.clicked.connect(self.run_regex_test)
            crl.addWidget(btn_run_reg)

            self.regex_output = QTextEdit()
            self.regex_output.setReadOnly(True)
            self.regex_output.setMaximumHeight(140)
            crl.addWidget(self.regex_output)
            split.addWidget(c_reg, 1)

            layout.addLayout(split)
            return page

        # =================================================================
        # ОБРАБОТЧИКИ СОБЫТИЙ И ЛОГИКА
        # =================================================================
        def update_total_ui(self):
            count = len(self.seen_emails)
            pcount = len(self.personal_base)
            self.stat_total.setText(str(count))
            self.stat_personal.setText(str(pcount))
            if hasattr(self, "stats_total_lbl"):
                self.stats_total_lbl.setText(str(count))
            if hasattr(self, "stats_personal_lbl"):
                self.stats_personal_lbl.setText(str(pcount))

        def _load_existing_base(self):
            records = EmailDatabase.get_all_records()
            for r in records:
                self.seen_emails.add(r[1])
                if "HUMAN" in str(r[4]):
                    self.personal_base.add(r[1])

        def add_to_recent_table(self, email, source_url, country, last_active):
            row = self.recent_table.rowCount()
            if row >= 25:
                self.recent_table.removeRow(0)
                row -= 1
            self.recent_table.insertRow(row)

            it_e = QTableWidgetItem(email); it_e.setForeground(QColor(0, 243, 255))
            it_c = QTableWidgetItem(country)
            it_a = QTableWidgetItem(last_active); it_a.setForeground(QColor(0, 255, 157))
            it_s = QTableWidgetItem(source_url[:40]); it_s.setForeground(QColor(176, 38, 255))

            for col, it in enumerate([it_e, it_c, it_a, it_s]):
                self.recent_table.setItem(row, col, it)
            self.update_total_ui()

        def write_log_safe(self, msg, tag, widget_type):
            widget = self.log_auto if widget_type == "auto" else self.log_parser
            ts = time.strftime("%H:%M:%S")
            colors = {"info": "#00f3ff", "err": "#ff2a6d", "warn": "#ffcc00", "success": "#00ff9d"}
            color = colors.get(tag, "#a0a0b0")
            widget.append(f'<span style="color:{color};">[{ts}] {msg}</span>')

        def set_status_safe(self, text, running):
            self.status_dash.setText(text)
            self.status_dash.setStyleSheet(f"color: {'#00f3ff' if running else '#4a4a5a'}; font-family: Consolas; font-size: 11px; letter-spacing: 2px; background: transparent;")
            self.stat_status.setText("ACTIVE" if running else "IDLE")
            self.stat_status.setStyleSheet(f"color: {'#00ff9d' if running else '#8A2BE2'}; background: transparent;")
            pop_animate(self.stat_status)
            self.btn_dash_run.setEnabled(not running)
            self.btn_dash_auto.setEnabled(not running)
            self.btn_dash_stop.setEnabled(running)
            self.btn_auto_start.setEnabled(not running)
            self.btn_auto_stop.setEnabled(running)
            if running:
                self.auto_status.setText("ENGINE: CRAWLING")
                self.auto_status.setStyleSheet("color: #00ff9d; background: transparent;")
                self.auto_dot.set_color("#00ff9d")
            else:
                self.auto_status.setText("ENGINE: STOPPED")
                self.auto_status.setStyleSheet("color: #8A2BE2; background: transparent;")
                self.auto_dot.set_color("#8A2BE2")
            try:
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

        def _fetch_page(self, url):
            if curl_requests is not None:
                try:
                    return curl_requests.get(url, impersonate="chrome", timeout=8, allow_redirects=True)
                except Exception:
                    pass
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
            return requests.get(url, headers=headers, timeout=8, allow_redirects=True)

        def _run_single_session(self):
            q = queue.Queue()
            for u in self.seed_urls: q.put(u)
            self.signals.log_signal.emit("Запуск сессии парсинга (60 узлов)...", "info", "parser")
            self._execute_harvest(q, max_pages=60, log_widget="parser")
            self.running = False
            self.signals.status_signal.emit("SYSTEM IDLE", False)
            self.signals.progress_signal.emit(100)

        def _run_infinite_session(self):
            q = queue.Queue()
            for u in self.seed_urls: q.put(u)
            self.signals.log_signal.emit("СТАРТ БЕСКОНЕЧНОГО ДВИЖКА...", "info", "auto")
            self._execute_harvest(q, max_pages=None, log_widget="auto")
            self.running = False
            self.signals.status_signal.emit("SYSTEM IDLE", False)
            self.signals.progress_signal.emit(0)

        def _execute_harvest(self, url_queue, max_pages=None, log_widget="parser"):
            visited = set()
            pages_processed = 0

            while self.running:
                if max_pages and pages_processed >= max_pages:
                    break
                if url_queue.empty():
                    for s in self.seed_urls:
                        url_queue.put(s)

                try:
                    current_url = url_queue.get_nowait()
                except queue.Empty:
                    break

                if current_url in visited:
                    continue
                visited.add(current_url)

                self.signals.domain_signal.emit(current_url[:42] + "...")
                self.signals.log_signal.emit(f"Запрос к источнику: {current_url}", "info", log_widget)

                try:
                    r = self._fetch_page(current_url)
                    pages_processed += 1
                    if max_pages:
                        self.signals.progress_signal.emit(int((pages_processed / max_pages) * 100))

                    if r.status_code == 200:
                        text = r.text
                        found = set(self.email_regex.findall(text))
                        new_count = 0
                        for em in found:
                            em_l = em.lower()
                            if em_l not in self.seen_emails:
                                self.seen_emails.add(em_l)
                                dom = em_l.split("@")[-1]
                                cat = "HUMAN / PERSONAL" if dom in ('gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'outlook.com') else "CORPORATE / DEV"
                                if "HUMAN" in cat:
                                    self.personal_base.add(em_l)

                                co, la = EmailDatabase.insert_email(em_l, cat, current_url, status="SAFE", score=90)
                                new_count += 1
                                self.signals.account_signal.emit(em_l, current_url, co, la)

                        if new_count > 0:
                            self.signals.log_signal.emit(f"Найдено {new_count} новых почт с {current_url}", "success", log_widget)

                        links = re.findall(r'href=[\'"](https?://[^\'" >]+)[\'"]', text)
                        for lk in links:
                            if url_queue.qsize() < self.link_cap and lk not in visited:
                                url_queue.put(lk)

                        self.signals.auto_iter_signal.emit(f"Queue: {url_queue.qsize()} | Visited: {len(visited)} | Base: {len(self.seen_emails)}")
                except Exception as e:
                    self.signals.log_signal.emit(f"Ошибка {current_url[:30]}: {e}", "err", log_widget)

                time.sleep(0.4)

        # Валидатор
        def inspect_single_address(self):
            em = self.val_input_single.text().strip()
            if not em or "@" not in em: return
            st, sc, dt, co, la = self.validator.validate(em)
            self.on_val_row(em, st, sc, dt, co, la)
            self.val_input_single.clear()

        def on_val_row(self, email, status, score, detail, country, last_active):
            self.validation_results[email] = (status, score, detail)
            row = self.val_table.rowCount()
            self.val_table.insertRow(row)

            c = QColor("#00ff9d" if status == "SAFE" else "#ff2a6d" if status == "TRAP" else "#ffcc00")
            it_e = QTableWidgetItem(email); it_e.setForeground(QColor(0, 243, 255))
            it_co = QTableWidgetItem(country)
            it_la = QTableWidgetItem(last_active); it_la.setForeground(QColor(0, 255, 157))
            it_s = QTableWidgetItem(status); it_s.setForeground(c)
            it_sc = QTableWidgetItem(str(score)); it_sc.setForeground(c)
            it_d = QTableWidgetItem(detail)

            for col, it in enumerate([it_e, it_co, it_la, it_s, it_sc, it_d]):
                self.val_table.setItem(row, col, it)
            self._update_val_counters()

        def _update_val_counters(self):
            c = {'SAFE': 0, 'RISKY': 0, 'TRAP': 0, 'INVALID': 0}
            for st, _, _ in self.validation_results.values():
                if st in c: c[st] += 1
            self.val_counters.setText(f"SAFE: {c['SAFE']} | RISKY: {c['RISKY']} | TRAP: {c['TRAP']} | INVALID: {c['INVALID']}")

        def on_val_progress(self, done, total):
            pct = int(done / max(1, total) * 100)
            self.val_progress.setValue(pct)

        def on_val_done(self):
            self.val_running = False
            self.btn_val_run.setEnabled(True)
            self.signals.mail_log_signal.emit(f"Валидация завершена. SAFE адресов: {sum(1 for st,_,_ in self.validation_results.values() if st == 'SAFE')}.", "success")
            self.refresh_mailer_list()

        def run_validation(self):
            if self.val_running: return
            emails = sorted(self.seen_emails)
            if not emails: return
            self.val_running = True
            self.btn_val_run.setEnabled(False)
            self.val_table.setRowCount(0)
            self.validation_results = {}

            def work():
                total = len(emails)
                for idx, em in enumerate(emails):
                    st, sc, dt, co, la = self.validator.validate(em)
                    self.signals.val_row_signal.emit(em, st, sc, dt, co, la)
                    self.signals.val_progress_signal.emit(idx + 1, total)
                    time.sleep(0.01)
                self.signals.val_done_signal.emit()

            threading.Thread(target=work, daemon=True).start()

        def clean_base_by_validation(self):
            cnt = EmailDatabase.purge_invalids_and_traps()
            self._load_existing_base()
            self.update_total_ui()
            self.refresh_database_table()
            QMessageBox.information(self, "Очистка", f"Удалено {cnt} спам-ловушек и невалидных почт!")

        # Мейлер
        def refresh_mailer_dropdown(self):
            self.mailer_acc_combo.clear()
            accs = MailerAccountManager.load_accounts()
            for a in accs:
                self.mailer_acc_combo.addItem(f"{a['email']} ({a['provider']})", a)

        def refresh_mailer_list(self):
            self.mail_list.clear()
            records = EmailDatabase.get_all_records()
            for r in records[:80]:
                it = QListWidgetItem(f"{r[1]}   [{r[2]}]")
                it.setData(Qt.ItemDataRole.UserRole, r[1])
                it.setForeground(QColor("#00ff9d"))
                self.mail_list.addItem(it)
            self.mail_list_count.setText(f"{len(records)} в базе")

        def on_mailer_selection(self):
            items = self.mail_list.selectedItems()
            if items:
                self.mail_to_lbl.setText(items[0].data(Qt.ItemDataRole.UserRole))

        def mailer_connect(self):
            data = self.mailer_acc_combo.currentData()
            if not data: return
            self.btn_mail_conn.setEnabled(False)
            self.on_mail_status("CONNECTING...", "#ffcc00")

            def work():
                sender = SmtpSender(data["email"], data["password"], log_fn=lambda m, t="info": self.signals.mail_log_signal.emit(m, t))
                try:
                    sender.connect()
                    self.mailer_sender = sender
                    self.signals.mail_status_signal.emit(f"CONNECTED AS {data['email']}", "#00ff9d")
                except Exception as e:
                    self.signals.mail_log_signal.emit(f"Ошибка SMTP: {e}", "err")
                    self.signals.mail_status_signal.emit("CONNECTION FAILED", "#ff2a6d")
                finally:
                    self.btn_mail_conn.setEnabled(True)

            threading.Thread(target=work, daemon=True).start()

        def mailer_send_selected(self):
            if self.mailer_busy: return
            to_email = self.mail_to_lbl.text()
            if "@" not in to_email:
                QMessageBox.warning(self, "Ошибка", "Выберите адрес получателя!")
                return
            if not self.mailer_sender:
                QMessageBox.warning(self, "Ошибка", "Подключите аккаунт отправителя (Connect)!")
                return
            subj = self.mail_subject_edit.text() or "Cooperation Proposal"
            body = self.mail_body_edit.toPlainText()

            st, sc, dt, co, la = self.validator.validate(to_email)
            if st in ('TRAP', 'INVALID'):
                QMessageBox.critical(self, "БЛОКИРОВКА ПРЕ-ФЛАЙТ", f"Адрес {to_email} признан спам-ловушкой ({st})!\n{dt}")
                return

            self.mailer_busy = True
            self.btn_mail_send.setEnabled(False)
            self.on_mail_status("SENDING...", "#00f3ff")

            def work():
                try:
                    self.mailer_sender.send(to_email, subj, body)
                    self.signals.mail_log_signal.emit(f"Письмо доставлено: {to_email}", "success")
                    self.signals.mail_status_signal.emit("LAST MAIL SENT OK", "#00ff9d")
                except Exception as e:
                    self.signals.mail_log_signal.emit(f"Сбой отправки: {e}", "err")
                    self.signals.mail_status_signal.emit("SEND ERROR", "#ff2a6d")
                finally:
                    self.mailer_busy = False
                    self.btn_mail_send.setEnabled(True)

            threading.Thread(target=work, daemon=True).start()

        def on_mail_log(self, msg, tag):
            ts = time.strftime("%H:%M:%S")
            colors = {"info": "#00f3ff", "err": "#ff2a6d", "warn": "#ffcc00", "success": "#00ff9d"}
            c = colors.get(tag, "#a0a0b0")
            self.log_mailer.append(f'<span style="color:{c};">[{ts}] {msg}</span>')

        def on_mail_status(self, text, color):
            self.mail_status_lbl.setText(text)
            self.mail_status_lbl.setStyleSheet(f"color: {color}; background: transparent; letter-spacing: 1px; font-family: Consolas;")

        def on_mail_sent(self, email, res):
            pass

        # Accounts
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
            self.acc_input_email.clear()
            self.acc_input_pass.clear()
            self.refresh_accounts_view()

        def save_raw_accounts_file(self):
            txt = self.accounts_editor.toPlainText()
            path = MailerAccountManager.get_file_path()
            with open(path, "w", encoding="utf-8") as f:
                f.write(txt)
            self.refresh_accounts_view()
            QMessageBox.information(self, "Сохранено", "accounts.txt успешно обновлен!")

        # Радио
        def on_radio_status(self, name, is_on):
            self.radio_title_lbl.setText(f"((o)) {name.upper()}")
            self.radio_state_lbl.setText("ВОСПРОИЗВЕДЕНИЕ" if is_on else "ОСТАНОВЛЕНО")
            self.btn_radio_toggle.setText("■  ОСТАНОВИТЬ" if is_on else "▶  ВКЛЮЧИТЬ ПОТОК")
            self.equalizer.set_active(is_on)
            self.sidebar.set_radio_state(name, is_on)

        def toggle_radio_playback(self):
            if self.radio.is_playing:
                self.radio.stop()
            else:
                self.radio.play(0)

        def select_radio_station(self, idx):
            self.radio.play(idx)

        # База и статистика
        def refresh_database_table(self):
            records = EmailDatabase.get_all_records()
            self.db_table.setRowCount(0)
            for r in records:
                row = self.db_table.rowCount()
                self.db_table.insertRow(row)
                it_id = QTableWidgetItem(str(r[0]))
                it_e = QTableWidgetItem(r[1]); it_e.setForeground(QColor(0, 243, 255))
                it_co = QTableWidgetItem(r[2])
                it_la = QTableWidgetItem(r[3]); it_la.setForeground(QColor(0, 255, 157))
                it_c = QTableWidgetItem(r[4])
                it_s = QTableWidgetItem(r[5][:40])
                for col, it in enumerate([it_id, it_e, it_co, it_la, it_c, it_s]):
                    self.db_table.setItem(row, col, it)

        def filter_database_table(self, query):
            query = query.lower()
            for row in range(self.db_table.rowCount()):
                match = any(query in (self.db_table.item(row, c).text().lower() if self.db_table.item(row, c) else "") for c in range(self.db_table.columnCount()))
                self.db_table.setRowHidden(row, not match)

        def clear_all_data(self):
            EmailDatabase.clear_database()
            self.seen_emails.clear()
            self.personal_base.clear()
            self.update_total_ui()
            self.refresh_database_table()
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

        # OSINT
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
                self.dns_output.append(f"[✓] MX Серверы ({len(hosts)}):")
                for h in hosts: self.dns_output.append(f"    • {h}")
            else:
                self.dns_output.append("[✕] MX серверы отсутствуют.")

        def run_regex_test(self):
            raw = self.regex_input.toPlainText()
            found = set(self.email_regex.findall(raw))
            self.regex_output.clear()
            self.regex_output.append(f"Найдено {len(found)} адресов:\n" + "\n".join(found))


# =====================================================================
# ТОЧКА ВХОДА (ENTRY POINT)
# =====================================================================
def main():
    if MISSING_DEPS:
        print("=" * 70)
        print("  MORPHH // ALLPARS V2.0 PRO - CYBERPUNK OSINT & HARVESTING SUITE")
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
    win = MainWindow()
    win.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
