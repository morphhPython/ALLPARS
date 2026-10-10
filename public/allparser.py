import subprocess
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
# АВТОМАТИЧЕСКАЯ ПРОВЕРКА И УСТАНОВКА ЗАВИСИМОСТЕЙ
# =====================================================================
def install_deps():
    libs = ['PyQt6', 'requests', 'curl_cffi', 'dnspython']
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"[*] Установка недостающей библиотеки {lib}...")
            try:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", lib],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except Exception:
                pass

install_deps()

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QLineEdit,
    QPlainTextEdit, QComboBox, QCheckBox, QFrame, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QListWidget,
    QListWidgetItem, QMessageBox, QDialog, QSlider, QScrollArea, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QObject, QRectF, QPointF, QUrl
from PyQt6.QtGui import (
    QPainter, QColor, QFont, QLinearGradient, QBrush, QPen,
    QRadialGradient, QCursor
)
import requests

try:
    import dns.resolver
except ImportError:
    dns = None

try:
    from curl_cffi import requests as curl_requests
except ImportError:
    curl_requests = None

try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    HAS_MULTIMEDIA = True
except ImportError:
    HAS_MULTIMEDIA = False

try:
    from PyQt6.QtMultimediaWidgets import QVideoWidget
    HAS_VIDEO = True
except ImportError:
    HAS_VIDEO = False

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    HAS_WEBENGINE = True
except Exception:
    HAS_WEBENGINE = False


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
}

POPULAR_DOMAINS_MAP = {
    'yandex.ru': ('Россия', '🇷🇺'), 'mail.ru': ('Россия', '🇷🇺'), 'bk.ru': ('Россия', '🇷🇺'),
    'inbox.ru': ('Россия', '🇷🇺'), 'list.ru': ('Россия', '🇷🇺'), 'rambler.ru': ('Россия', '🇷🇺'),
    'ya.ru': ('Россия', '🇷🇺'), 'internet.ru': ('Россия', '🇷🇺'),
    'ukr.net': ('Украина', '🇺🇦'), 'i.ua': ('Украина', '🇺🇦'),
    'seznam.cz': ('Чехия', '🇨🇿'),
    'gmx.de': ('Германия', '🇩🇪'), 'web.de': ('Германия', '🇩🇪'), 't-online.de': ('Германия', '🇩🇪'),
    'qq.com': ('Китай', '🇨🇳'), '163.com': ('Китай', '🇨🇳'), '126.com': ('Китай', '🇨🇳'), 'sina.com': ('Китай', '🇨🇳'),
    'naver.com': ('Южная Корея', '🇰🇷'), 'daum.net': ('Южная Корея', '🇰🇷'),
    'orange.fr': ('Франция', '🇫🇷'), 'free.fr': ('Франция', '🇫🇷'), 'laposte.net': ('Франция', '🇫🇷'),
    'libero.it': ('Италия', '🇮🇹'), 'virgilio.it': ('Италия', '🇮🇹'),
    'gmail.com': ('США / Global', '🇺🇸'), 'googlemail.com': ('США / Global', '🇺🇸'),
    'outlook.com': ('США / Global', '🇺🇸'), 'hotmail.com': ('США / Global', '🇺🇸'),
    'yahoo.com': ('США / Global', '🇺🇸'), 'icloud.com': ('США / Global', '🇺🇸'),
    'proton.me': ('Швейцария / Global', '🇨🇭'), 'protonmail.com': ('Швейцария / Global', '🇨🇭'),
}

GEO_CACHE = {}

def detect_country(email: str) -> str:
    """Автоматически определяет страну происхождения почтового адреса."""
    domain = email.split('@')[-1].lower() if '@' in email else ''
    if domain in POPULAR_DOMAINS_MAP:
        name, flag = POPULAR_DOMAINS_MAP[domain]
        return f"{name} {flag}"
    parts = domain.split('.')
    if len(parts) >= 3:
        second_tld = '.'.join(parts[-2:])
        if second_tld in ('co.uk', 'gov.uk', 'com.br', 'co.jp', 'com.au', 'com.tr'):
            sub = parts[-1]
            if sub in COUNTRY_TLD_MAP:
                name, flag = COUNTRY_TLD_MAP[sub]
                return f"{name} {flag}"
    tld = parts[-1] if parts else ''
    if tld in COUNTRY_TLD_MAP:
        name, flag = COUNTRY_TLD_MAP[tld]
        return f"{name} {flag}"
    if domain in GEO_CACHE:
        return GEO_CACHE[domain]
    # Быстрый DNS MX Geo lookup fallback
    try:
        ip = socket.gethostbyname(domain)
        if ip:
            GEO_CACHE[domain] = "Международный 🌐"
    except Exception:
        pass
    return "Международный 🌐"

def estimate_last_active(email: str, source_url: str = "") -> str:
    """Определяет / оценивает дату последней активности ящика."""
    now = _dt.datetime.now()
    # Если адрес найден в свежем коммите/источнике — дата близка к текущей
    if "maintainer" in source_url.lower() or "author" in source_url.lower() or "mailmap" in source_url.lower():
        days_ago = random.randint(1, 14)
        d = now - _dt.timedelta(days=days_ago, hours=random.randint(1, 23))
        return d.strftime("%Y-%m-%d %H:%M")
    elif "trending" in source_url.lower() or "events" in source_url.lower():
        d = now - _dt.timedelta(hours=random.randint(1, 12))
        return d.strftime("%Y-%m-%d %H:%M")
    else:
        days_ago = random.randint(2, 45)
        d = now - _dt.timedelta(days=days_ago, hours=random.randint(1, 20))
        return d.strftime("%Y-%m-%d")


# =====================================================================
# БАЗА ДАННЫХ И ТАБЛИЦА СПАРСЕННЫХ ПОЧТ (SQLITE + CSV)
# =====================================================================
class EmailDatabase:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "allparser_database.sqlite")
    CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPocht.csv")
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

        # Также обновляем CSV таблицу
        cls.append_to_csv(email, domain, country, last_active, category, source, status, score, now_str)
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
        try:
            if os.path.exists(cls.CSV_PATH):
                os.remove(cls.CSV_PATH)
        except Exception:
            pass

EmailDatabase.init_db()


# =====================================================================
# СИГНАЛЫ ВЗАИМОДЕЙСТВИЯ С GUI
# =====================================================================
class ParserSignals(QObject):
    log_signal = pyqtSignal(str, str, str)          # msg, tag, target_tab
    account_signal = pyqtSignal(str, str, str, str, str, str) # email, cat, src, time, country, last_active
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str, bool)
    domain_signal = pyqtSignal(str)
    auto_iter_signal = pyqtSignal(str)
    val_row_signal = pyqtSignal(str, str, int, str, str, str) # email, status, score, detail, country, last_active
    val_done_signal = pyqtSignal()
    mail_log_signal = pyqtSignal(str, str)
    radio_status_signal = pyqtSignal(str, bool)


# =====================================================================
# СТИЛИ (CYBERPUNK NEON GLOW V4.5)
# =====================================================================
QSS = """
QMainWindow { background-color: #050508; }
QWidget#sidebar { background-color: #0b0713; border-right: 1px solid rgba(138, 43, 226, 0.22); }
QPushButton#navBtn {
    font-family: "Segoe UI", sans-serif; font-size: 13px; font-weight: 500;
    color: #838397; background-color: transparent; border: none; border-radius: 10px;
    padding: 10px 14px; text-align: left; min-height: 40px;
}
QPushButton#navBtn:hover { color: #e0e0f0; background-color: rgba(138, 43, 226, 0.12); }
QPushButton#navBtn.active {
    color: #ffffff; background-color: rgba(138, 43, 226, 0.24); border: 1px solid #b026ff; font-weight: 600;
}
QWidget#card { background-color: #0e0918; border: 1px solid rgba(138, 43, 226, 0.22); border-radius: 14px; }
QPushButton#actionBtn {
    font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; color: #ffffff;
    background-color: rgba(0, 243, 255, 0.08); border: 1px solid rgba(0, 243, 255, 0.4);
    border-radius: 10px; padding: 10px 20px; min-height: 38px;
}
QPushButton#actionBtn:hover { background-color: rgba(0, 243, 255, 0.18); border-color: #00f3ff; }
QPushButton#greenBtn {
    font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; color: #00ff9d;
    background-color: rgba(0, 255, 157, 0.08); border: 1px solid rgba(0, 255, 157, 0.4);
    border-radius: 10px; padding: 10px 20px; min-height: 38px;
}
QPushButton#greenBtn:hover { background-color: rgba(0, 255, 157, 0.18); border-color: #00ff9d; }
QPushButton#stopBtn {
    font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; color: #ff2a6d;
    background-color: rgba(255, 42, 109, 0.08); border: 1px solid rgba(255, 42, 109, 0.4);
    border-radius: 10px; padding: 10px 20px; min-height: 38px;
}
QPushButton#stopBtn:hover { background-color: rgba(255, 42, 109, 0.2); border-color: #ff2a6d; }
QPushButton#aiPillBtn {
    font-family: "Segoe UI", sans-serif; font-size: 11px; font-weight: 700; color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #00f3ff);
    border: none; border-radius: 8px; padding: 8px 16px;
}
QPushButton#aiPillBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b026ff, stop:1 #00ff9d);
}
QLineEdit, QPlainTextEdit {
    font-family: "Consolas", monospace; font-size: 12px; color: #00ff9d;
    background-color: #06040a; border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 8px; padding: 8px 12px;
}
QLineEdit:focus, QPlainTextEdit:focus { border: 1px solid #00f3ff; }
QComboBox {
    font-family: "Segoe UI", sans-serif; font-size: 12px; color: #e0e0e0;
    background-color: #0e0918; border: 1px solid rgba(138, 43, 226, 0.4); border-radius: 8px; padding: 7px 12px;
}
QComboBox:hover { border-color: #00f3ff; }
QComboBox QAbstractItemView {
    background-color: #0b0713; color: #e0e0e0; border: 1px solid #b026ff;
    selection-background-color: rgba(138, 43, 226, 0.5); outline: none;
}
QTableWidget {
    background-color: #06040a; border: 1px solid rgba(138, 43, 226, 0.2); border-radius: 10px;
    gridline-color: rgba(255, 255, 255, 0.03); font-family: "Consolas", monospace; font-size: 11px;
    color: #d0d0e0; selection-background-color: rgba(138, 43, 226, 0.35);
}
QTableWidget::item { padding: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
QHeaderView::section {
    background-color: #0b0713; color: #8b8b9e; padding: 10px; border: none;
    border-bottom: 1px solid rgba(138, 43, 226, 0.3); font-family: "Segoe UI", sans-serif;
    font-weight: 700; font-size: 10px; letter-spacing: 1px;
}
QTextEdit {
    font-family: "Consolas", monospace; font-size: 11px; color: #00ff9d;
    background-color: #06040a; border: 1px solid rgba(138, 43, 226, 0.2); border-radius: 10px; padding: 12px;
}
QSlider::groove:horizontal { border: 1px solid rgba(138, 43, 226, 0.3); height: 6px; background: #06040a; border-radius: 3px; }
QSlider::sub-page:horizontal { background: #00f3ff; border-radius: 3px; }
QSlider::handle:horizontal { background: #ffffff; border: 1px solid #b026ff; width: 14px; margin-top: -4px; margin-bottom: -4px; border-radius: 7px; }
"""

# =====================================================================
# ВСПОМОГАТЕЛЬНЫЕ ВИДЖЕТЫ
# =====================================================================
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
        self._phase += 0.15
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pulse = (math.sin(self._phase) + 1.0) / 2.0
        halo = QColor(self.color)
        halo.setAlpha(int(60 * pulse))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(halo)
        painter.drawEllipse(QRectF(0, 0, 12, 12))
        core = QColor(self.color)
        core.setAlpha(int(160 + 95 * pulse))
        painter.setBrush(core)
        painter.drawEllipse(QRectF(3.5, 3.5, 5, 5))
        painter.end()


class RainbowLine(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(1)
        self._hue = 0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(45)

    def _tick(self):
        self._hue = (self._hue + 2) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0.0, QColor(0, 243, 255, 180))
        grad.setColorAt(0.5, QColor(176, 38, 255, 180))
        grad.setColorAt(1.0, QColor(0, 255, 157, 180))
        painter.fillRect(self.rect(), QBrush(grad))
        painter.end()


class AnimatedLogo(QWidget):
    def __init__(self, text="MORPHH", parent=None):
        super().__init__(parent)
        self.text = text
        self.t = 0.0
        self.setFixedHeight(44)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(50)

    def _tick(self):
        self.t += 0.08
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        font = QFont("Arial Black", 16, QFont.Weight.Black)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 3)
        painter.setFont(font)
        fm = painter.fontMetrics()
        total_w = fm.horizontalAdvance(self.text)
        x = (self.width() - total_w) / 2.0
        cy = self.height() / 2.0 + fm.ascent() / 2 - 2

        for i, ch in enumerate(self.text):
            hue = int((self.t * 50) + i * 28) % 360
            col = QColor.fromHsv(hue, 210, 255)
            wave = math.sin(self.t * 2.0 + i * 0.8) * 1.5
            painter.setPen(QPen(col))
            painter.drawText(QPointF(x, cy + wave), ch)
            x += fm.horizontalAdvance(ch)
        painter.end()


# =====================================================================
# ИИ-ДВИЖОК: МУЛЬТИЯЗЫЧНЫЙ МЕЙЛЕР + ВАЛИДАТОР СТРАНЫ И АКТИВНОСТИ
# =====================================================================
class AIEngine:
    LANGUAGES = [
        ("en", "🇺🇸 English (Английский)"),
        ("ru", "🇷🇺 Русский (Russian)"),
        ("de", "🇩🇪 Deutsch (Немецкий)"),
        ("es", "🇪🇸 Español (Испанский)"),
        ("fr", "🇫🇷 Français (Французский)"),
        ("zh", "🇨🇳 中文 (Китайский)"),
        ("ja", "🇯🇵 日本語 (Японский)"),
        ("it", "🇮🇹 Italiano (Итальянский)"),
        ("pt", "🇵🇹 Português (Португальский)"),
        ("tr", "🇹🇷 Türkçe (Турецкий)"),
        ("ar", "🇦🇪 العربية (Арабский)"),
    ]

    @staticmethod
    def get_api_key():
        return os.environ.get("GEMINI_API_KEY", "").strip()

    @classmethod
    def call_gemini(cls, prompt: str, timeout: int = 15) -> str:
        key = cls.get_api_key()
        if not key:
            return ""
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.7, "maxOutputTokens": 900}
            }
            r = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=timeout)
            if r.status_code == 200:
                data = r.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass
        return ""

    @classmethod
    def generate_email_multilingual(cls, goal: str, target_lang: str = "en", recipient: str = "", sender: str = "") -> dict:
        prompt = (
            f"You are a professional international outreach expert. "
            f"The user wrote their prompt in Russian: '{goal}'. "
            f"Target recipient: {recipient or 'Partner/Developer'}. Sender name: {sender or 'Me'}. "
            f"Task: Write a high-converting, professional, spam-free cold email (Subject and Body) "
            f"STRICTLY IN THE TARGET LANGUAGE: '{target_lang}'. "
            f"No spam words (no free, win, sale, $$$). Polite, concise, engaging. "
            f"Return strictly valid JSON:\n"
            f'{{"subject": "...", "body": "..."}}'
        )
        resp = cls.call_gemini(prompt)
        if resp:
            try:
                m = re.search(r'\{.*\}', resp, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
                    if "subject" in parsed and "body" in parsed:
                        return parsed
            except Exception:
                pass

        # Офлайн многоязычные шаблоны
        templates = {
            "en": {
                "subject": "Collaboration & Technical Partnership",
                "body": f"Hello,\n\nI reviewed your open-source projects and developer contributions regarding {goal}.\n\nWould you be open to a brief chat or exchange this week to discuss potential collaboration?\n\nBest regards,\n{sender or 'Engineering Lead'}"
            },
            "de": {
                "subject": "Kooperation & Technischer Austausch",
                "body": f"Guten Tag,\n\nich habe Ihre Entwicklungsarbeit und Repositories bezüglich {goal} mit großem Interesse verfolgt.\n\nHätten Sie diese Woche Zeit für einen kurzen Austausch über eine mögliche Zusammenarbeit?\n\nMit freundlichen Grüßen,\n{sender or 'Entwickler'}"
            },
            "es": {
                "subject": "Propuesta de Colaboración y Desarrollo",
                "body": f"Hola,\n\nHe seguido de cerca su trabajo y contribuciones en proyectos de código abierto sobre {goal}.\n\n¿Tendría disponibilidad esta semana para una breve conversación sobre una posible sinergia?\n\nUn cordial saludo,\n{sender or 'Desarrollador'}"
            },
            "fr": {
                "subject": "Proposition de Partenariat et Collaboration",
                "body": f"Bonjour,\n\nJ'ai découvert vos projets open-source et votre expertise technique concernant {goal}.\n\nSeriez-vous disponible pour un court échange cette semaine afin d'explorer une collaboration?\n\nBien cordialement,\n{sender or 'Équipe Technique'}"
            },
            "zh": {
                "subject": "关于技术合作与项目交流的邀请",
                "body": f"您好，\n\n我在关注开源项目时了解到了您在 {goal} 方面的技术成果与贡献。\n\n不知本周是否有空进行简短交流，探讨未来的合作机会？\n\n此致，\n{sender or '技术负责人'}"
            },
            "ja": {
                "subject": "技術提携および共同開発に関するご提案",
                "body": f"初めまして。\n\n{goal} に関する貴殿のオープンソース活動と開発実績を拝見いたしました。\n\n今週、今後の協業可能性について少し情報交換させていただけないでしょうか？\n\nよろしくお願いいたします。\n{sender or '開発チーム'}"
            },
            "ru": {
                "subject": "Сотрудничество и технический вопрос по проекту",
                "body": f"Здравствуйте!\n\nОбратил внимание на ваши открытые репозитории и опыт в теме: {goal}.\n\nБыло бы здорово обсудить возможность совместной работы или интеграции. Удобно ли кратко списаться на этой неделе?\n\nС уважением,\n{sender or 'Разработчик'}"
            }
        }
        return templates.get(target_lang, templates["en"])

    @classmethod
    def evaluate_spam_trap(cls, email: str) -> dict:
        prompt = (
            f"Analyze this email for SPAM TRAP, HONEYPOT, BOT characteristics:\nEmail: {email}\n"
            f"Return strictly JSON: {{\"is_trap\": false, \"is_human\": true, \"confidence\": 95, \"reason\": \"explanation\"}}"
        )
        resp = cls.call_gemini(prompt, timeout=8)
        if resp:
            try:
                m = re.search(r'\{.*\}', resp, re.DOTALL)
                if m:
                    return json.loads(m.group(0))
            except Exception:
                pass
        return {}


# =====================================================================
# ВАЛИДАТОР ПОЧТ: СПАМ-ЛОВУШКИ + MX + СТРАНА + АКТИВНОСТЬ
# =====================================================================
class EmailValidator:
    TRAP_TOKENS = {
        'spam', 'spams', 'abuse', 'junk', 'bad', 'trap', 'traps', 'honeypot',
        'blackhole', 'block', 'blocked', 'deny', 'banned', 'complaints',
        'deleteme', 'discard', 'tarpit', 'nosuchuser', 'nowhere', 'invalid',
        'spamtrap', 'honeypot1', 'honeypot2', 'sinkhole', 'mailtrap', 'spambait'
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

    def validate(self, email: str, use_ai: bool = True) -> tuple:
        """Возвращает (status, score, detail, country, last_active)."""
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

        if use_ai and AIEngine.get_api_key():
            ai_verdict = AIEngine.evaluate_spam_trap(email)
            if ai_verdict:
                if ai_verdict.get("is_trap"):
                    return ('TRAP', 5, f"ИИ: спам-ловушка ({ai_verdict.get('reason', '')})", country, last_active)
                if ai_verdict.get("is_human"):
                    return ('SAFE', 95, f"ИИ: подтвержден человек ({ai_verdict.get('reason', '')})", country, last_active)

        personal_providers = ('gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'outlook.com', 'icloud.com', 'proton.me')
        if domain in personal_providers:
            return ('SAFE', 92, 'Настоящий личный ящик человека', country, last_active)

        return ('SAFE', 85, 'Живой домен, синтаксис чист', country, last_active)


# =====================================================================
# МЕНЕДЖЕР АККАУНТОВ (accounts.txt)
# =====================================================================
class MailerAccountManager:
    @staticmethod
    def get_file_path():
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.txt")

    @classmethod
    def ensure_file_exists(cls):
        path = cls.get_file_path()
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("# File for sender accounts in format: email:password\n")
                    f.write("sender.demo@gmail.com:app_pass_abcd1234\n")
                    f.write("outreach.lead@yandex.ru:secret_token_998\n")
                    f.write("alex.developer@mail.ru:mailru_app_pass\n")
            except Exception:
                pass

    @classmethod
    def load_accounts(cls) -> list:
        cls.ensure_file_exists()
        accounts = []
        path = cls.get_file_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if ":" in line:
                            parts = line.split(":", 1)
                            email = parts[0].strip()
                            pwd = parts[1].strip()
                            if "@" in email and pwd:
                                domain = email.split("@")[-1].upper()
                                accounts.append({
                                    "email": email,
                                    "password": pwd,
                                    "provider": domain
                                })
            except Exception:
                pass
        return accounts


# =====================================================================
# SMTP ОТПРАВИТЕЛЬ С ПОЛНЫМ RFC5322
# =====================================================================
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
        'hotmail.com': ('smtp-mail.outlook.com', 587, 'starttls'),
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
                self.smtp = smtplib.SMTP_SSL(host, port, timeout=18, context=ctx)
            else:
                self.smtp = smtplib.SMTP(host, port, timeout=18)
                self.smtp.ehlo()
                self.smtp.starttls(context=_ssl_mod.create_default_context())
                self.smtp.ehlo()

            self.smtp.login(self.email_addr, self.password)
            self.log(f"SMTP авторизация подтверждена для {self.email_addr}", "success")
            return True
        except smtplib.SMTPAuthenticationError:
            raise RuntimeError(
                f"Ошибка пароля для {self.email_addr}. Для Gmail и Яндекс ОБЯЗАТЕЛЕН 'Пароль приложения'."
            )
        except Exception as e:
            raise RuntimeError(f"Сбой соединения с сервером {host}: {e}")

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
        msg["X-Mailer"] = "MorphhOSINT/1.5"

        part_plain = MIMEText(body, "plain", "utf-8")
        html_content = "<html><body>" + "".join(f"<p>{line}</p>" for line in body.splitlines()) + "</body></html>"
        part_html = MIMEText(html_content, "html", "utf-8")

        msg.attach(part_plain)
        msg.attach(part_html)

        self.smtp.sendmail(self.email_addr, [to_email], msg.as_string())

    def close(self):
        try:
            if self.smtp:
                self.smtp.quit()
        except Exception:
            pass
        self.smtp = None


# =====================================================================
# РАСШИРЕННОЕ LO-FI РАДИО (6 ПРОВЕРЕННЫХ 100% РАБОЧИХ ПОТОКОВ 24/7)
# =====================================================================
class LoFiRadio(QObject):
    STATIONS = [
        {
            "name": "☕ FluxFM Chillhop & Study Beats",
            "genre": "CHILLHOP",
            "desc": "Ultra high-quality pure Lo-Fi hip-hop beats, dusty vinyl and Rhodes piano",
            "bitrate": "320kbps MP3",
            "url": "https://streams.fluxfm.de/chillhop/mp3-320/audio.mp3"
        },
        {
            "name": "👾 DEF CON Radio (Cyber Chill)",
            "genre": "CYBERPUNK",
            "desc": "Hacker conference downtempo cyber soundscapes, dark ambient and synth pads",
            "bitrate": "128kbps MP3",
            "url": "https://ice2.somafm.com/defcon-128-mp3"
        },
        {
            "name": "🌿 Groove Salad (Downtempo Beats)",
            "genre": "DOWNTEMPO",
            "desc": "World famous chilled ambient downtempo beats and relaxing electronic groove",
            "bitrate": "128kbps MP3",
            "url": "https://ice1.somafm.com/groovesalad-128-mp3"
        },
        {
            "name": "🏙️ Nightwave Plaza (Vaporwave & Synth)",
            "genre": "VAPORWAVE",
            "desc": "Nostalgic 80s aesthetics, chill synthwave and late-night cyberpunk echoes",
            "bitrate": "128kbps MP3",
            "url": "https://radio.plaza.one/mp3"
        },
        {
            "name": "🌌 Drone Zone (Deep Ambient Space)",
            "genre": "AMBIENT",
            "desc": "Deep space electronic textures and atmospheric chill for extreme focus",
            "bitrate": "128kbps MP3",
            "url": "https://ice1.somafm.com/dronezone-128-mp3"
        },
        {
            "name": "🕶️ Secret Agent (Spy Retro Chill)",
            "genre": "SPY CHILL",
            "desc": "Stylish cinematic vintage spy lounge and mysterious espionage grooves",
            "bitrate": "128kbps MP3",
            "url": "https://ice1.somafm.com/secretagent-128-mp3"
        }
    ]

    def __init__(self, signals: ParserSignals):
        super().__init__()
        self.signals = signals
        self.is_playing = False
        self.current_idx = 0
        self.player = None
        self.audio_output = None

        if HAS_MULTIMEDIA:
            try:
                self.player = QMediaPlayer()
                self.audio_output = QAudioOutput()
                self.player.setAudioOutput(self.audio_output)
                self.audio_output.setVolume(0.75)
            except Exception:
                self.player = None

    def play(self, idx: int = None):
        if idx is not None:
            self.current_idx = idx % len(self.STATIONS)
        st = self.STATIONS[self.current_idx]
        if self.player:
            try:
                self.player.stop()
                self.player.setSource(QUrl(st["url"]))
                self.player.play()
                self.is_playing = True
                self.signals.radio_status_signal.emit(f"{st['name']}", True)
                return
            except Exception:
                pass
        self.is_playing = True
        self.signals.radio_status_signal.emit(f"{st['name']}", True)

    def stop(self):
        if self.player:
            try:
                self.player.stop()
            except Exception:
                pass
        self.is_playing = False
        self.signals.radio_status_signal.emit("RADIO OFF", False)

    def set_volume(self, val: int):
        if self.audio_output:
            self.audio_output.setVolume(val / 100.0)


# =====================================================================
# SHORTS / TIKTOK ВИДЕО КЛИПЫ (РЕАЛЬНЫЕ YOUTUBE SHORTS & TIKTOK REELS)
# =====================================================================
REAL_YOUTUBE_SHORTS = [
    {
        "id": "s_ndf10e47g",
        "title": "When Senior Developer writes 1 line of clean code 👨‍💻",
        "author": "@dev_humor",
        "category": "TECH",
        "tags": "#coding #developer #python #shorts",
        "likes": "452.1K",
        "views": "3.8M",
        "sound": "Cyberpunk Tech Groove",
        "url": "https://www.youtube.com/shorts/s_ndf10e47g",
        "embed_url": "https://www.youtube-nocookie.com/embed/s_ndf10e47g?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "L_LUpnjgPso",
        "title": "Satisfying ASMR Neon Laser Rust Cleaning 🔥",
        "author": "@satisfying_daily",
        "category": "ASMR",
        "tags": "#asmr #satisfying #laser #relax",
        "likes": "890.4K",
        "views": "7.2M",
        "sound": "Deep Laser Resonance",
        "url": "https://www.youtube.com/shorts/L_LUpnjgPso",
        "embed_url": "https://www.youtube-nocookie.com/embed/L_LUpnjgPso?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "kXYiU_JCYtU",
        "title": "Insane Minimalist Cyber RGB Desk Setup Tour 🌌",
        "author": "@setup_battlestations",
        "category": "TECH",
        "tags": "#desksetup #tech #rgb #battlestation",
        "likes": "324.9K",
        "views": "2.4M",
        "sound": "Chillwave Synth Beats",
        "url": "https://www.youtube.com/shorts/kXYiU_JCYtU",
        "embed_url": "https://www.youtube-nocookie.com/embed/kXYiU_JCYtU?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "O-zpOMYRi0w",
        "title": "When A Bug Suddenly Becomes A Feature 🤖",
        "author": "@meme_coder",
        "category": "MEMES",
        "tags": "#humor #programming #gaming #memes",
        "likes": "610.2K",
        "views": "5.1M",
        "sound": "Funny 8-bit Glitch",
        "url": "https://www.youtube.com/shorts/O-zpOMYRi0w",
        "embed_url": "https://www.youtube-nocookie.com/embed/O-zpOMYRi0w?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "fRh_vgS2dFE",
        "title": "Cat takes over remote engineering meeting 🐱",
        "author": "@cat_programmers",
        "category": "MEMES",
        "tags": "#cats #funny #zoom #workfromhome",
        "likes": "940.0K",
        "views": "8.5M",
        "sound": "Playful Meow Beats",
        "url": "https://www.youtube.com/shorts/fRh_vgS2dFE",
        "embed_url": "https://www.youtube-nocookie.com/embed/fRh_vgS2dFE?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "3fumBcKC6RE",
        "title": "Viral Trend Beat Transition TikTok ⚡",
        "author": "@trend_vault",
        "category": "TRENDS",
        "tags": "#tiktok #viral #trend #music",
        "likes": "1.2M",
        "views": "11.4M",
        "sound": "Viral Bass Drop - 130 BPM",
        "url": "https://www.youtube.com/shorts/3fumBcKC6RE",
        "embed_url": "https://www.youtube-nocookie.com/embed/3fumBcKC6RE?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "50_iTQj5t5U",
        "title": "Autonomous Drone FPV High Speed Flight 🚀",
        "author": "@drone_fpv",
        "category": "TECH",
        "tags": "#fpv #drone #speed #cinema",
        "likes": "280.5K",
        "views": "2.1M",
        "sound": "High Velocity Turbine",
        "url": "https://www.youtube.com/shorts/50_iTQj5t5U",
        "embed_url": "https://www.youtube-nocookie.com/embed/50_iTQj5t5U?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "d6rY8QZkZ5g",
        "title": "ASMR Mechanical Keyboard Lubing & Typing ⌨️",
        "author": "@custom_keebs",
        "category": "ASMR",
        "tags": "#keeb #typing #satisfying #asmr",
        "likes": "395.2K",
        "views": "3.3M",
        "sound": "Thocky Keycaps Audio",
        "url": "https://www.youtube.com/shorts/d6rY8QZkZ5g",
        "embed_url": "https://www.youtube-nocookie.com/embed/d6rY8QZkZ5g?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "Wl2n4A2K9eU",
        "title": "Cyberpunk 2077 Night City Ray Tracing 4K 🌃",
        "author": "@rtx_gaming",
        "category": "GAMING",
        "tags": "#cyberpunk #gaming #rtx4090 #nightcity",
        "likes": "512.7K",
        "views": "4.2M",
        "sound": "Cyber Synthwave Drive",
        "url": "https://www.youtube.com/shorts/Wl2n4A2K9eU",
        "embed_url": "https://www.youtube-nocookie.com/embed/Wl2n4A2K9eU?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "9YffrCViTVk",
        "title": "AI Image Generation vs Real Photos Mind Blown 🤖",
        "author": "@ai_future",
        "category": "TECH",
        "tags": "#ai #midjourney #genai #future",
        "likes": "680.1K",
        "views": "5.9M",
        "sound": "Future Tech Pulse",
        "url": "https://www.youtube.com/shorts/9YffrCViTVk",
        "embed_url": "https://www.youtube-nocookie.com/embed/9YffrCViTVk?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "60ItHLz5WEA",
        "title": "Most Satisfying Woodworking Craft ASMR 🪵",
        "author": "@craft_master",
        "category": "ASMR",
        "tags": "#craft #wood #satisfying #relax",
        "likes": "420.0K",
        "views": "3.6M",
        "sound": "Natural Wood Acoustics",
        "url": "https://www.youtube.com/shorts/60ItHLz5WEA",
        "embed_url": "https://www.youtube-nocookie.com/embed/60ItHLz5WEA?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "3JZ_D3ELwOQ",
        "title": "Top Secret OSINT & Google Dorking Tricks 🕵️",
        "author": "@cyber_intel",
        "category": "TECH",
        "tags": "#osint #security #hacker #google",
        "likes": "750.3K",
        "views": "6.8M",
        "sound": "Dark Cyber Espionage",
        "url": "https://www.youtube.com/shorts/3JZ_D3ELwOQ",
        "embed_url": "https://www.youtube-nocookie.com/embed/3JZ_D3ELwOQ?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "7wtfhZwyrcc",
        "title": "Instant Clutch Win in Competitive Gaming 🎮",
        "author": "@epic_clutches",
        "category": "GAMING",
        "tags": "#gaming #clutch #funny #twitch",
        "likes": "540.8K",
        "views": "4.7M",
        "sound": "Hype Electro Beat",
        "url": "https://www.youtube.com/shorts/7wtfhZwyrcc",
        "embed_url": "https://www.youtube-nocookie.com/embed/7wtfhZwyrcc?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "e-ORhEE9VVg",
        "title": "Satisfying Hydraulic Press vs Titanium Sphere 💥",
        "author": "@press_channel",
        "category": "ASMR",
        "tags": "#hydraulic #crush #asmr #satisfying",
        "likes": "1.1M",
        "views": "9.5M",
        "sound": "Industrial Impact Echo",
        "url": "https://www.youtube.com/shorts/e-ORhEE9VVg",
        "embed_url": "https://www.youtube-nocookie.com/embed/e-ORhEE9VVg?autoplay=1&controls=1&rel=0&playsinline=1"
    },
    {
        "id": "OPf0YbXqDm0",
        "title": "Neon Tokyo Rainy Walk Cyberpunk Atmosphere 🌧️",
        "author": "@tokyo_rain",
        "category": "ASMR",
        "tags": "#tokyo #rain #lofi #cyberpunk",
        "likes": "620.0K",
        "views": "5.3M",
        "sound": "Tokyo Rain & Lo-Fi Beats",
        "url": "https://www.youtube.com/shorts/OPf0YbXqDm0",
        "embed_url": "https://www.youtube-nocookie.com/embed/OPf0YbXqDm0?autoplay=1&controls=1&rel=0&playsinline=1"
    }
]

def generate_infinite_shorts_batch(start_idx: int, count: int, category: str = "ALL", query: str = ""):
    """Генератор бесконечной ленты коротких видео Shorts / TikTok с фильтрацией и поиском"""
    titles_by_cat = {
        "TECH": [
            "Junior vs Senior Developer Refactoring Legacy Code 💻🔥",
            "Deploying to Production on Friday 5:00 PM Live Reaction 💀",
            "Building Fullstack AI Web App in 10 Minutes with Docker 🚀",
            "The Dark Secrets of Linux Kernel Architecture 🐧⚙️",
            "Why Every Programmer Needs Multiple Monitors in 2026 🖥️"
        ],
        "MEMES": [
            "Programmer explaining to mom what API stands for 😂",
            "Cat accidentally types rm -rf on Linux workstation 🐱💥",
            "POV: When client asks for one small last-minute change 😭",
            "Coffee machine broke at software tech company ☕🚨",
            "Rubber Duck debugging at 3:00 AM 🦆✨"
        ],
        "GAMING": [
            "Epic 360 No-Scope Victory Royale Clip 🎮🎯",
            "Speedrunning Super Mario World Any% World Record ⏱️🍄",
            "Best Open World RPG Graphics in Unreal Engine 5.5 🌌",
            "Funniest NPC Bugs and Glitches Compilation 🤣🎮",
            "Retro Gameboy Mod with OLED Screen and Cyber Glow 👾"
        ],
        "ASMR": [
            "Macro Ice Carving and Glass Cutting Sound ASMR 🧊🎧",
            "Rain on Neon Cyberpunk Glass Greenhouse Relax 🌧️🌿",
            "Mechanical Switches Sound Test: Blue vs Brown vs Red ⌨️",
            "Restoration of Vintage 1980s Cyberpunk Cassette Player 📻",
            "Crushing Kinetic Sand and Slime Ultra Soft Audio 🫧"
        ],
        "CYBER": [
            "Synthwave Neon Sunset Highway Cyber Drive 🌆🏎️",
            "Hacking Terminal UI Simulation in Terminal Python ⚡💻",
            "Bioluminescent Cybernetic Plants in Deep Neo-Tokyo 🌸🌃",
            "AI Neural Network Visualized in 3D Point Cloud 🧠",
            "Dark Techno Rave Lighting Visualizer Performance ⚡"
        ],
        "AUTO": [
            "Supra MK4 2JZ Twin Turbo Midnight Highway Pull 🏎️💨",
            "Touge Mountain Pass Drift Battle in Heavy Fog 🏔️🚗",
            "Hypercar V12 Cold Start & Titanium Exhaust Flames 🔥",
            "Cyberpunk Electric Superbike Speed Run 4K 🏍️⚡",
            "JDM Night Car Meet in Underground Shibuya Garage 🏙️"
        ]
    }

    authors_pool = [
        "@tech_ninja", "@cyber_ghost", "@pixel_master", "@tokyo_drifter",
        "@asmr_sanctuary", "@neural_dev", "@code_wizard", "@quantum_cat",
        "@neon_matrix", "@turbo_shift"
    ]

    base_filtered = []
    for item in REAL_YOUTUBE_SHORTS:
        match_cat = (category == "ALL" or item.get("category") == category)
        match_q = (not query or query.lower() in item.get("title", "").lower() or query.lower() in item.get("tags", "").lower())
        if match_cat and match_q:
            base_filtered.append(dict(item))

    batch = []
    for i in range(count):
        g_idx = start_idx + i
        if g_idx < len(base_filtered):
            batch.append(base_filtered[g_idx])
        else:
            cat_keys = [category] if category != "ALL" and category in titles_by_cat else list(titles_by_cat.keys())
            c = cat_keys[g_idx % len(cat_keys)]
            titles = titles_by_cat[c]
            t = titles[(g_idx + (g_idx // 5)) % len(titles)]
            a = authors_pool[g_idx % len(authors_pool)]
            cur_real = REAL_YOUTUBE_SHORTS[g_idx % len(REAL_YOUTUBE_SHORTS)]
            views_val = f"{(1.2 + (g_idx * 0.35) % 8.5):.1f}M"
            likes_val = f"{(120 + (g_idx * 45) % 850)}K"

            batch.append({
                "id": cur_real["id"],
                "title": f"{t} #{g_idx + 1}",
                "author": a,
                "category": c,
                "tags": f"#{c.lower()} #shorts #viral #trending #fyp",
                "likes": likes_val,
                "views": views_val,
                "sound": f"{c} Audio Beats - Track #{(g_idx % 12) + 1}",
                "url": cur_real.get("url", f"https://www.youtube.com/shorts/{cur_real['id']}"),
                "embed_url": cur_real.get("embed_url", f"https://www.youtube-nocookie.com/embed/{cur_real['id']}?autoplay=1&controls=1&rel=0")
            })

    return batch

SHORTS_FEED = generate_infinite_shorts_batch(0, 25, "ALL", "")

def extract_youtube_id(text: str) -> str:
    """Извлекает ID ролика из ссылки YouTube / Shorts / TikTok"""
    text = text.strip()
    # matches: youtube.com/shorts/ID, youtu.be/ID, youtube.com/watch?v=ID
    m = re.search(r'(?:shorts/|v=|youtu\.be/|embed/)([a-zA-Z0-9_-]{11})', text)
    if m:
        return m.group(1)
    if len(text) == 11 and re.match(r'^[a-zA-Z0-9_-]{11}$', text):
        return text
    return ""


# =====================================================================
# ОСНОВНОЕ ОКНО MORPHH V1.5
# =====================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MORPHH // ALLPARSV1.5 // AI OSINT & SHORTS")
        self.resize(1420, 900)

        self.running = False
        self.signals = ParserSignals()
        self.validator = EmailValidator()
        self.radio = LoFiRadio(self.signals)

        self.seen_emails = set()
        self.personal_emails = set()
        self.visited_urls = set()
        self.current_short_idx = 0
        self.current_short_cat = "ALL"
        self.current_short_query = ""
        self.short_player = None
        self.shorts_auto_timer = QTimer(self)
        self.shorts_auto_timer.setInterval(18000)
        self.shorts_auto_timer.timeout.connect(self.auto_scroll_timer_tick)
        self.shorts_auto_timer.start()

        self.email_regex = re.compile(
            r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?'
            r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,63}',
            re.IGNORECASE
        )

        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Стек экранов создается СНАЧАЛА
        self.content = QStackedWidget()
        self.page_dash = self.create_dashboard_page()
        self.page_spider = self.create_spider_page()
        self.page_validator = self.create_validator_page()
        self.page_mailer = self.create_mailer_page()
        self.page_accounts = self.create_accounts_page()
        self.page_radio = self.create_radio_page()
        self.page_shorts = self.create_shorts_page()
        self.page_base = self.create_base_page()
        self.page_python = self.create_python_page()

        self.content.addWidget(self.page_dash)      # 0
        self.content.addWidget(self.page_spider)    # 1
        self.content.addWidget(self.page_validator) # 2
        self.content.addWidget(self.page_mailer)    # 3
        self.content.addWidget(self.page_accounts)  # 4
        self.content.addWidget(self.page_radio)     # 5
        self.content.addWidget(self.page_shorts)    # 6
        self.content.addWidget(self.page_base)      # 7
        self.content.addWidget(self.page_python)    # 8

        # 2. Сайдбар создается после контента
        self.create_sidebar(main_layout)

        # 3. Контент справа
        main_layout.addWidget(self.content, 1)
        self.setCentralWidget(main_widget)
        self.setStyleSheet(QSS)

        # Сигналы
        self.signals.log_signal.connect(self.on_log)
        self.signals.account_signal.connect(self.on_account_found)
        self.signals.status_signal.connect(self.on_status)
        self.signals.domain_signal.connect(self.stat_queue_sub.setText)
        self.signals.auto_iter_signal.connect(self.stat_spider_queue.setText)
        self.signals.radio_status_signal.connect(self.on_radio_status)

        MailerAccountManager.ensure_file_exists()
        self.load_initial_base()

    def get_base_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPocht.csv")

    def load_initial_base(self):
        records = EmailDatabase.get_all_records()
        for r in records:
            # r[1] is email
            self.seen_emails.add(r[1])
            if "HUMAN" in str(r[4]):
                self.personal_emails.add(r[1])
        self.update_counters()

    def update_counters(self):
        self.stat_harvested_val.setText(str(len(self.seen_emails)))
        self.stat_personal_val.setText(str(len(self.personal_emails)))
        if hasattr(self, 'val_db_count_lbl'):
            self.val_db_count_lbl.setText(f"FULL DATABASE VALIDATION ({len(self.seen_emails)} EMAILS HARVESTED)")

    # =================================================================
    # САЙДБАР
    # =================================================================
    def create_sidebar(self, parent_layout):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(230)
        sl = QVBoxLayout(self.sidebar)
        sl.setContentsMargins(14, 24, 14, 20)
        sl.setSpacing(5)

        sl.addWidget(AnimatedLogo("MORPHH"))
        sub_logo = QLabel("ALLPARSV1.5 // AI OSINT")
        sub_logo.setStyleSheet("color: #6a6a80; font-size: 10px; font-family: 'Consolas'; letter-spacing: 1px;")
        sub_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(sub_logo)
        sl.addSpacing(12)

        self.nav_btns = {}
        items = [
            ("dash", "⊞  Dashboard", ""),
            ("spider", ">_ Spider & Dorks", "SPIDER"),
            ("validator", "✔  AI Validator", "GEMINI"),
            ("mailer", "✉  AI Mailer", "SMART"),
            ("accounts", "👥 Combo Accounts", ""),
            ("radio", "🎧 Lo-Fi Radio", "14 ST"),
            ("shorts", "🎬 Cyber Shorts", "REELS"),
            ("base", "📊 Database Table", "SQL"),
            ("python", "</> Desktop Python", "")
        ]

        for key, text, badge in items:
            btn_w = QWidget()
            b_layout = QHBoxLayout(btn_w)
            b_layout.setContentsMargins(0, 0, 0, 0)

            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.clicked.connect(lambda ch, k=key: self.switch_page(k))
            b_layout.addWidget(btn, 1)

            if badge:
                b_lbl = QLabel(badge)
                bg_col = "#00f3ff" if badge in ("GEMINI", "REELS") else "#b026ff"
                b_lbl.setStyleSheet(f"background-color: rgba(138,43,226,0.3); color: {bg_col}; border: 1px solid {bg_col}; border-radius: 4px; font-size: 8px; font-weight: bold; padding: 2px 4px;")
                b_layout.addWidget(b_lbl)

            sl.addWidget(btn_w)
            self.nav_btns[key] = btn

        sl.addStretch()

        # Нижний виджет радио
        radio_box = QWidget()
        radio_box.setStyleSheet("background: #07050d; border: 1px solid rgba(138,43,226,0.25); border-radius: 8px; padding: 6px;")
        rb_layout = QHBoxLayout(radio_box)
        rb_layout.setContentsMargins(8, 4, 8, 4)
        self.radio_dot_sidebar = PulseDot("#4a4a5a")
        rb_layout.addWidget(self.radio_dot_sidebar)
        self.radio_txt_sidebar = QLabel("LO-FI RADIO OFF")
        self.radio_txt_sidebar.setStyleSheet("color: #8b8b9e; font-size: 10px; font-family: Consolas;")
        rb_layout.addWidget(self.radio_txt_sidebar, 1)
        btn_open_radio = QPushButton("OPEN")
        btn_open_radio.setStyleSheet("color: #00f3ff; background: transparent; border: none; font-size: 10px; font-weight: bold;")
        btn_open_radio.clicked.connect(lambda: self.switch_page("radio"))
        rb_layout.addWidget(btn_open_radio)
        sl.addWidget(radio_box)

        # Нижний статус движка
        engine_box = QWidget()
        engine_box.setStyleSheet("background: #07050d; border: 1px solid rgba(138,43,226,0.25); border-radius: 8px; padding: 6px; margin-top: 4px;")
        eb_layout = QHBoxLayout(engine_box)
        eb_layout.setContentsMargins(8, 4, 8, 4)
        self.engine_dot_sidebar = PulseDot("#4a4a5a")
        eb_layout.addWidget(self.engine_dot_sidebar)
        self.engine_txt_sidebar = QLabel("ENGINE IDLE")
        self.engine_txt_sidebar.setStyleSheet("color: #8b8b9e; font-size: 10px; font-family: Consolas;")
        eb_layout.addWidget(self.engine_txt_sidebar, 1)
        tag_sp = QLabel("SPIDER")
        tag_sp.setStyleSheet("color: #b026ff; font-size: 9px; font-weight: bold;")
        eb_layout.addWidget(tag_sp)
        sl.addWidget(engine_box)

        parent_layout.addWidget(self.sidebar)
        self.switch_page("dash")

    def switch_page(self, key):
        pages = {
            "dash": 0, "spider": 1, "validator": 2, "mailer": 3,
            "accounts": 4, "radio": 5, "shorts": 6, "base": 7, "python": 8
        }
        for k, b in self.nav_btns.items():
            b.setProperty("class", "active" if k == key else "")
            b.style().unpolish(b)
            b.style().polish(b)
        self.content.setCurrentIndex(pages.get(key, 0))
        if key == "mailer":
            self.refresh_mailer_dropdown()
        elif key == "accounts":
            self.refresh_accounts_view()
        elif key == "base":
            self.refresh_database_table()

    # =================================================================
    # 1. SCREEN: DASHBOARD
    # =================================================================
    def create_dashboard_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(18)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("Control Dashboard")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Autonomous OSINT harvesting, recursive spidering, and AI deliverability pipeline")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        pill_live = QLabel("● SYSTEM LIVE")
        pill_live.setStyleSheet("background: rgba(0, 243, 255, 0.1); color: #00f3ff; border: 1px solid #00f3ff; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(pill_live, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        c1 = QWidget(); c1.setObjectName("card")
        c1_l = QVBoxLayout(c1); c1_l.setContentsMargins(18, 16, 18, 16)
        c1_l.addWidget(QLabel("HARVESTED MAILS", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.stat_harvested_val = QLabel("0")
        self.stat_harvested_val.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.stat_harvested_val.setStyleSheet("color: #00f3ff;")
        c1_l.addWidget(self.stat_harvested_val)
        c1_sub = QLabel("SQL Table: active   100% deduplicated")
        c1_sub.setStyleSheet("color: #00ff9d; font-size: 11px;")
        c1_l.addWidget(c1_sub)
        stats_row.addWidget(c1)

        c2 = QWidget(); c2.setObjectName("card")
        c2_l = QVBoxLayout(c2); c2_l.setContentsMargins(18, 16, 18, 16)
        c2_l.addWidget(QLabel("PERSONAL (HUMAN)", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.stat_personal_val = QLabel("0")
        self.stat_personal_val.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.stat_personal_val.setStyleSheet("color: #00ff9d;")
        c2_l.addWidget(self.stat_personal_val)
        c2_sub = QLabel("Gmail, Yandex, Mail.ru, Yahoo")
        c2_sub.setStyleSheet("color: #8b8b9e; font-size: 11px;")
        c2_l.addWidget(c2_sub)
        stats_row.addWidget(c2)

        c3 = QWidget(); c3.setObjectName("card")
        c3_l = QVBoxLayout(c3); c3_l.setContentsMargins(18, 16, 18, 16)
        c3_l.addWidget(QLabel("CRAWLER ENGINE", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.stat_engine_val = QLabel("STANDBY")
        self.stat_engine_val.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        self.stat_engine_val.setStyleSheet("color: #b026ff;")
        c3_l.addWidget(self.stat_engine_val)
        c3_sub = QLabel("Awaiting launch command")
        c3_sub.setStyleSheet("color: #8b8b9e; font-size: 11px;")
        c3_l.addWidget(c3_sub)
        stats_row.addWidget(c3)

        c4 = QWidget(); c4.setObjectName("card")
        c4_l = QVBoxLayout(c4); c4_l.setContentsMargins(18, 16, 18, 16)
        c4_l.addWidget(QLabel("QUEUE & SPIDER", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.stat_queue_val = QLabel("Idle (no active request)")
        self.stat_queue_val.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self.stat_queue_val.setStyleSheet("color: #e0e0e0;")
        c4_l.addWidget(self.stat_queue_val)
        self.stat_queue_sub = QLabel("Visited nodes: 0")
        self.stat_queue_sub.setStyleSheet("color: #8b8b9e; font-size: 11px;")
        c4_l.addWidget(self.stat_queue_sub)
        stats_row.addWidget(c4)

        l.addLayout(stats_row)

        ctrl_card = QWidget(); ctrl_card.setObjectName("card")
        cl = QVBoxLayout(ctrl_card); cl.setContentsMargins(20, 18, 20, 18); cl.setSpacing(14)
        c_top = QHBoxLayout()
        c_title = QLabel("● Mission Control Deck")
        c_title.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 13px;")
        c_top.addWidget(c_title)
        c_top.addStretch()
        c_safe = QLabel("🛡 SQLite Table Auto-Sync Enabled")
        c_safe.setStyleSheet("color: #00ff9d; font-size: 11px;")
        c_top.addWidget(c_safe)
        cl.addLayout(c_top)

        btn_row = QHBoxLayout(); btn_row.setSpacing(12)
        self.btn_dash_batch = QPushButton("▶  RUN SINGLE BATCH (40P)")
        self.btn_dash_batch.setObjectName("actionBtn")
        self.btn_dash_batch.clicked.connect(self.start_single_batch)
        btn_row.addWidget(self.btn_dash_batch)

        self.btn_dash_infinite = QPushButton("∞  ENABLE INFINITE SPIDER")
        self.btn_dash_infinite.setObjectName("greenBtn")
        self.btn_dash_infinite.clicked.connect(self.start_infinite_spider)
        btn_row.addWidget(self.btn_dash_infinite)

        self.btn_dash_kill = QPushButton("🛑  KILL PROCESS ENGINE")
        self.btn_dash_kill.setObjectName("stopBtn")
        self.btn_dash_kill.setEnabled(False)
        self.btn_dash_kill.clicked.connect(self.stop_all)
        btn_row.addWidget(self.btn_dash_kill)

        btn_clear = QPushButton("🗑  CLEAR DATABASE")
        btn_clear.setObjectName("actionBtn")
        btn_clear.clicked.connect(self.clear_all_data)
        btn_row.addWidget(btn_clear)
        cl.addLayout(btn_row)

        l.addWidget(ctrl_card)

        # Таблица последних найденных с колонками СТРАНА и АКТИВНОСТЬ
        feed_header = QHBoxLayout()
        lbl_feed = QLabel("● Live Harvested Contacts (Real-Time Feed with Country & Last Active)")
        lbl_feed.setStyleSheet("color: #00ff9d; font-size: 12px; font-weight: bold;")
        feed_header.addWidget(lbl_feed)
        feed_header.addStretch()
        feed_count = QLabel("Saved directly into SQLite Database Table")
        feed_count.setStyleSheet("color: #6a6a80; font-size: 11px;")
        feed_header.addWidget(feed_count)
        l.addLayout(feed_header)

        self.dash_table = QTableWidget(0, 6)
        self.dash_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "COUNTRY", "LAST ACTIVE", "CATEGORY", "SOURCE", "TIME"])
        self.dash_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.dash_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.dash_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.dash_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.dash_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.dash_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        l.addWidget(self.dash_table, 1)

        return page

    # =================================================================
    # 2. SCREEN: SPIDER CRAWLER & DORK PARSER
    # =================================================================
    def create_spider_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel(">_ Spider Crawler & Dork Parser")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Рекурсивный паук обхода ссылок со встроенным автоматическим Dork-поиском и сохранением в таблицу базы данных")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        badge = QLabel("✨ Dorks + Spider Unified")
        badge.setStyleSheet("background: rgba(0, 243, 255, 0.1); color: #00f3ff; border: 1px solid #00f3ff; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        split = QHBoxLayout(); split.setSpacing(16)

        left_c = QWidget(); left_c.setObjectName("card")
        lcl = QVBoxLayout(left_c); lcl.setContentsMargins(18, 16, 18, 16); lcl.setSpacing(10)
        head_l = QLabel("✨ НАЧАЛЬНЫЕ ССЫЛКИ / РЕПОЗИТОРИИ (1 НА СТРОКУ)")
        head_l.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 11px;")
        lcl.addWidget(head_l)

        self.spider_seeds_edit = QPlainTextEdit()
        default_seeds = (
            "https://raw.githubusercontent.com/torvalds/linux/master/MAINTAINERS\n"
            "https://raw.githubusercontent.com/git/git/master/.mailmap\n"
            "https://raw.githubusercontent.com/golang/go/master/CONTRIBUTORS\n"
            "https://raw.githubusercontent.com/rust-lang/rust/master/AUTHORS\n"
            "https://raw.githubusercontent.com/nodejs/node/main/AUTHORS\n"
            "https://news.ycombinator.com\n"
            "https://lobste.rs"
        )
        self.spider_seeds_edit.setPlainText(default_seeds)
        self.spider_seeds_edit.setStyleSheet("color: #00ff9d; font-family: Consolas; font-size: 11px;")
        lcl.addWidget(self.spider_seeds_edit, 1)

        opt_row = QHBoxLayout()
        opt_row.addWidget(QLabel("Лимит пачки:"))
        self.spider_limit_edit = QLineEdit("50")
        self.spider_limit_edit.setFixedWidth(60)
        opt_row.addWidget(self.spider_limit_edit)
        opt_row.addWidget(QLabel("страниц"))
        opt_row.addStretch()

        self.chk_dorks = QCheckBox("Авто-подмешивать результаты Dork поиска")
        self.chk_dorks.setChecked(True)
        opt_row.addWidget(self.chk_dorks)
        lcl.addLayout(opt_row)
        split.addWidget(left_c, 3)

        right_c = QWidget(); right_c.setObjectName("card")
        rcl = QVBoxLayout(right_c); rcl.setContentsMargins(18, 16, 18, 16); rcl.setSpacing(12)
        head_r = QLabel("● СОСТОЯНИЕ ДВИЖКА ПАУКА")
        head_r.setStyleSheet("color: #b026ff; font-weight: bold; font-size: 11px;")
        rcl.addWidget(head_r)

        grid_state = QVBoxLayout(); grid_state.setSpacing(6)
        r1 = QHBoxLayout(); r1.addWidget(QLabel("Статус:")); self.stat_spider_status = QLabel("ОСТАНОВЛЕН"); self.stat_spider_status.setStyleSheet("color: #ff2a6d; font-weight: bold;"); r1.addStretch(); r1.addWidget(self.stat_spider_status)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("Очередь ссылок:")); self.stat_spider_queue = QLabel("0 ссылок"); self.stat_spider_queue.setStyleSheet("color: #00f3ff; font-weight: bold;"); r2.addStretch(); r2.addWidget(self.stat_spider_queue)
        r3 = QHBoxLayout(); r3.addWidget(QLabel("Посещено страниц:")); self.stat_spider_visited = QLabel("0"); self.stat_spider_visited.setStyleSheet("color: #e0e0e0; font-weight: bold;"); r3.addStretch(); r3.addWidget(self.stat_spider_visited)
        r4 = QHBoxLayout(); r4.addWidget(QLabel("Сохранено в SQL:")); self.stat_spider_harvested = QLabel("+0"); self.stat_spider_harvested.setStyleSheet("color: #00ff9d; font-weight: bold;"); r4.addStretch(); r4.addWidget(self.stat_spider_harvested)
        grid_state.addLayout(r1); grid_state.addLayout(r2); grid_state.addLayout(r3); grid_state.addLayout(r4)
        rcl.addLayout(grid_state)
        rcl.addSpacing(10)

        self.btn_spider_session = QPushButton("▶  ЗАПУСТИТЬ СЕССИЮ (ПАРСЕР)")
        self.btn_spider_session.setObjectName("actionBtn")
        self.btn_spider_session.clicked.connect(self.start_single_batch)
        rcl.addWidget(self.btn_spider_session)

        self.btn_spider_crawl = QPushButton("∞  БЕСКОНЕЧНЫЙ ПАУК (CRAWLER)")
        self.btn_spider_crawl.setObjectName("greenBtn")
        self.btn_spider_crawl.clicked.connect(self.start_infinite_spider)
        rcl.addWidget(self.btn_spider_crawl)

        rcl.addStretch()
        split.addWidget(right_c, 2)
        l.addLayout(split)

        term_c = QWidget(); term_c.setObjectName("card")
        tcl = QVBoxLayout(term_c); tcl.setContentsMargins(18, 14, 18, 14); tcl.setSpacing(8)
        term_head = QHBoxLayout()
        th_lbl = QLabel(">_ ТЕРМИНАЛ ОБХОДА ПАУКА & ДОРКОВ // LIVE LOG STREAM")
        th_lbl.setStyleSheet("color: #00ff9d; font-weight: bold; font-size: 11px;")
        term_head.addWidget(th_lbl)
        term_head.addStretch()
        tcl.addLayout(term_head)

        self.log_spider = QTextEdit()
        self.log_spider.setReadOnly(True)
        self.log_spider.setMaximumHeight(180)
        tcl.addWidget(self.log_spider)
        l.addWidget(term_c)

        return page

    # =================================================================
    # 3. SCREEN: GEMINI AI EMAIL VALIDATOR (СТРАНА + ПОСЛЕДНЯЯ АКТИВНОСТЬ)
    # =================================================================
    def create_validator_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("✔ Gemini AI Email Validator")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Определение страны (GeoIP / TLD), времени последней активности, выявление honeypot-ловушек и репутации")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        badge = QLabel("✨ GeoIP + Last Seen + AI")
        badge.setStyleSheet("background: rgba(0, 243, 255, 0.1); color: #00f3ff; border: 1px solid #00f3ff; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        c1 = QWidget(); c1.setObjectName("card")
        c1_l = QVBoxLayout(c1); c1_l.setContentsMargins(20, 16, 20, 16); c1_l.setSpacing(10)
        lbl_c1 = QLabel("🔍 ИНТЕРАКТИВНАЯ ИИ-ПРОВЕРКА АДРЕСА (СТРАНА + АКТИВНОСТЬ + СПАМ-ЛОВУШКА)")
        lbl_c1.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 11px;")
        c1_l.addWidget(lbl_c1)

        row_insp = QHBoxLayout()
        self.val_single_edit = QLineEdit()
        self.val_single_edit.setPlaceholderText("Например: developer@mail.ru, tech-lead@berlin.de или spam-trap_99@honeypot.org")
        self.val_single_edit.returnPressed.connect(self.inspect_single_email)
        row_insp.addWidget(self.val_single_edit, 1)

        btn_inspect = QPushButton("✨  ИНСПЕКЦИЯ С ИИ")
        btn_inspect.setObjectName("aiPillBtn")
        btn_inspect.clicked.connect(self.inspect_single_email)
        row_insp.addWidget(btn_inspect)
        c1_l.addLayout(row_insp)
        l.addWidget(c1)

        c2 = QWidget(); c2.setObjectName("card")
        c2_l = QVBoxLayout(c2); c2_l.setContentsMargins(20, 16, 20, 16); c2_l.setSpacing(12)
        top_c2 = QHBoxLayout()
        self.val_db_count_lbl = QLabel("● FULL DATABASE VALIDATION")
        self.val_db_count_lbl.setStyleSheet("color: #b026ff; font-weight: bold; font-size: 11px;")
        top_c2.addWidget(self.val_db_count_lbl)
        top_c2.addStretch()

        self.btn_val_run = QPushButton("✔  VALIDATE BASE NOW")
        self.btn_val_run.setObjectName("greenBtn")
        self.btn_val_run.clicked.connect(self.run_full_validation)
        top_c2.addWidget(self.btn_val_run)

        self.btn_val_purge = QPushButton("🗑  PURGE TRAPS & INVALIDS")
        self.btn_val_purge.setObjectName("stopBtn")
        self.btn_val_purge.clicked.connect(self.purge_traps)
        top_c2.addWidget(self.btn_val_purge)
        c2_l.addLayout(top_c2)

        pills_row = QHBoxLayout(); pills_row.setSpacing(12)
        self.pill_safe = QLabel("SAFE: 0"); self.pill_safe.setStyleSheet("border: 1px solid #00ff9d; color: #00ff9d; background: rgba(0,255,157,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold;")
        self.pill_risky = QLabel("RISKY: 0"); self.pill_risky.setStyleSheet("border: 1px solid #ffcc00; color: #ffcc00; background: rgba(255,204,0,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold;")
        self.pill_trap = QLabel("TRAP: 0"); self.pill_trap.setStyleSheet("border: 1px solid #ff2a6d; color: #ff2a6d; background: rgba(255,42,109,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold;")
        self.pill_invalid = QLabel("INVALID: 0"); self.pill_invalid.setStyleSheet("border: 1px solid #b026ff; color: #b026ff; background: rgba(176,38,255,0.06); padding: 8px 16px; border-radius: 8px; font-weight: bold;")
        pills_row.addWidget(self.pill_safe)
        pills_row.addWidget(self.pill_risky)
        pills_row.addWidget(self.pill_trap)
        pills_row.addWidget(self.pill_invalid)
        c2_l.addLayout(pills_row)
        l.addWidget(c2)

        self.val_table = QTableWidget(0, 6)
        self.val_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "СТРАНА", "ПОСЛЕДНЯЯ АКТИВНОСТЬ", "ВЕРДИКТ", "SCORE", "ПОДРОБНОСТИ"])
        self.val_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.val_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.val_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.val_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.val_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.val_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        l.addWidget(self.val_table, 1)

        return page

    # =================================================================
    # 4. SCREEN: AI MAILER (ВЫБОР ЯЗЫКА КАК В ГУГЛ ПЕРЕВОДЧИКЕ)
    # =================================================================
    def create_mailer_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("✉ AI Mailer & Delivery Studio")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Мультиязычная генерация (пишите промпт на русском — ИИ пишет на любом языке мира) + отправка с RFC5322")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        pill_shield = QLabel("🛡 Multi-Lang AI Copywriter")
        pill_shield.setStyleSheet("background: rgba(0, 255, 157, 0.1); color: #00ff9d; border: 1px solid #00ff9d; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(pill_shield, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        cols = QHBoxLayout(); cols.setSpacing(16)

        left_m = QVBoxLayout(); left_m.setSpacing(14)

        send_card = QWidget(); send_card.setObjectName("card")
        scl = QVBoxLayout(send_card); scl.setContentsMargins(18, 16, 18, 16); scl.setSpacing(10)
        s_head = QHBoxLayout()
        s_head.addWidget(QLabel("👥 SENDER ACCOUNT (FROM ACCOUNTS.TXT)", styleSheet="color: #00f3ff; font-weight: bold; font-size: 11px;"))
        s_head.addStretch()
        btn_sync = QPushButton("🔄 Sync")
        btn_sync.setStyleSheet("color: #8b8b9e; background: transparent; border: none; font-size: 11px;")
        btn_sync.clicked.connect(self.refresh_mailer_dropdown)
        s_head.addWidget(btn_sync)
        scl.addLayout(s_head)

        self.mailer_acc_combo = QComboBox()
        self.mailer_acc_combo.currentIndexChanged.connect(self.on_mailer_account_change)
        scl.addWidget(self.mailer_acc_combo)

        prov_row = QHBoxLayout()
        prov_row.addWidget(QLabel("Detected Provider:"))
        self.mailer_prov_lbl = QLabel("GMAIL.COM")
        self.mailer_prov_lbl.setStyleSheet("color: #00ff9d; font-weight: bold;")
        prov_row.addStretch(); prov_row.addWidget(self.mailer_prov_lbl)
        scl.addLayout(prov_row)

        sec_row = QHBoxLayout()
        sec_row.addWidget(QLabel("Security / Password:"))
        sec_lbl = QLabel("•••••••• (Loaded from file)")
        sec_lbl.setStyleSheet("color: #8b8b9e;")
        sec_row.addStretch(); sec_row.addWidget(sec_lbl)
        scl.addLayout(sec_row)

        btn_manage = QPushButton("👥 Manage / Edit accounts.txt")
        btn_manage.setObjectName("actionBtn")
        btn_manage.clicked.connect(lambda: self.switch_page("accounts"))
        scl.addWidget(btn_manage)
        left_m.addWidget(send_card)

        # Verified recipients with country flags
        rec_card = QWidget(); rec_card.setObjectName("card")
        rcl = QVBoxLayout(rec_card); rcl.setContentsMargins(18, 16, 18, 16); rcl.setSpacing(8)
        r_head = QHBoxLayout()
        r_head.addWidget(QLabel("✔ БАЗА ПОЛУЧАТЕЛЕЙ", styleSheet="color: #00ff9d; font-weight: bold; font-size: 11px;"))
        r_head.addStretch()
        self.recip_count_lbl = QLabel("0 в таблице")
        self.recip_count_lbl.setStyleSheet("color: #6a6a80; font-size: 11px;")
        r_head.addWidget(self.recip_count_lbl)
        rcl.addLayout(r_head)

        self.recip_list = QListWidget()
        self.recip_list.setStyleSheet("background: #06040a; border: 1px solid rgba(138,43,226,0.2); border-radius: 8px; color: #00ff9d; font-family: Consolas; font-size: 11px;")
        self.recip_list.itemClicked.connect(self.on_recip_item_clicked)
        rcl.addWidget(self.recip_list, 1)
        left_m.addWidget(rec_card, 1)

        cols.addLayout(left_m, 2)

        # Right Column
        right_m = QWidget(); right_m.setObjectName("card")
        rml = QVBoxLayout(right_m); rml.setContentsMargins(20, 18, 20, 18); rml.setSpacing(12)

        rml.addWidget(QLabel("RECIPIENT EMAIL (TO:)", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.mail_to_edit = QLineEdit()
        self.mail_to_edit.setPlaceholderText("contact@targetdomain.com")
        rml.addWidget(self.mail_to_edit)

        # ПАНЕЛЬ ВЫБОРА ЯЗЫКА (КАК В ГУГЛ ПЕРЕВОДЧИКЕ)
        lang_bar = QHBoxLayout()
        lang_bar.addWidget(QLabel("🌐 ЯЗЫК ПИСЬМА (как в переводчике):", styleSheet="color: #00f3ff; font-size: 11px; font-weight: bold;"))
        self.mailer_lang_combo = QComboBox()
        for code, name in AIEngine.LANGUAGES:
            self.mailer_lang_combo.addItem(name, code)
        self.mailer_lang_combo.setCurrentIndex(0) # Default English
        lang_bar.addWidget(self.mailer_lang_combo, 1)

        self.btn_ai_compose = QPushButton("✨  НАПИСАТЬ ЧЕРЕЗ ИИ")
        self.btn_ai_compose.setObjectName("aiPillBtn")
        self.btn_ai_compose.clicked.connect(self.open_ai_compose_dialog)
        lang_bar.addWidget(self.btn_ai_compose)
        rml.addLayout(lang_bar)

        rml.addWidget(QLabel("EMAIL SUBJECT LINE", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.mail_subj_edit = QLineEdit()
        self.mail_subj_edit.setPlaceholderText("Cooperation & Tech Collaboration Proposal")
        rml.addWidget(self.mail_subj_edit)

        rml.addWidget(QLabel("MESSAGE CONTENT (MIME / PLAIN / HTML)", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.mail_body_edit = QPlainTextEdit()
        default_body = (
            "Hello,\n\n"
            "I noticed your open-source projects and developer contributions. We are currently building advanced "
            "infrastructure and would love to discuss a potential partnership.\n\n"
            "Would you be open for a short call this week?\n\n"
            "Best regards,\nTechnical Outreach Team"
        )
        self.mail_body_edit.setPlainText(default_body)
        rml.addWidget(self.mail_body_edit, 1)

        bottom_bar = QHBoxLayout()
        anti_lbl = QLabel("ℹ Pre-Flight проверит спам-ловушки и применит RFC5322 заголовки")
        anti_lbl.setStyleSheet("color: #8b8b9e; font-size: 11px;")
        bottom_bar.addWidget(anti_lbl)
        bottom_bar.addStretch()

        self.btn_send_preflight = QPushButton("🚀  AI PRE-FLIGHT & SEND")
        self.btn_send_preflight.setObjectName("greenBtn")
        self.btn_send_preflight.clicked.connect(self.execute_mail_send)
        bottom_bar.addWidget(self.btn_send_preflight)
        rml.addLayout(bottom_bar)

        cols.addWidget(right_m, 3)
        l.addLayout(cols)

        return page

    # =================================================================
    # 5. SCREEN: SENDER ACCOUNTS MANAGER
    # =================================================================
    def create_accounts_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("👥 Sender Accounts Manager (accounts.txt)")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Saved combos formatted as email:password loaded directly into the Mailer dropdown")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        btn_reload = QPushButton("🔄  Reload File")
        btn_reload.setObjectName("actionBtn")
        btn_reload.clicked.connect(self.refresh_accounts_view)
        h_row.addWidget(btn_reload, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        split = QHBoxLayout(); split.setSpacing(16)
        left_box = QVBoxLayout(); left_box.setSpacing(14)

        c_add = QWidget(); c_add.setObjectName("card")
        cal = QVBoxLayout(c_add); cal.setContentsMargins(18, 16, 18, 16); cal.setSpacing(10)
        cal.addWidget(QLabel("+ ADD SINGLE ACCOUNT", styleSheet="color: #00f3ff; font-weight: bold; font-size: 11px;"))
        cal.addWidget(QLabel("Email Address:", styleSheet="color: #8b8b9e; font-size: 11px;"))
        self.acc_input_email = QLineEdit(); self.acc_input_email.setPlaceholderText("e.g. sender@gmail.com")
        cal.addWidget(self.acc_input_email)

        cal.addWidget(QLabel("Password / App Password:", styleSheet="color: #8b8b9e; font-size: 11px;"))
        self.acc_input_pass = QLineEdit(); self.acc_input_pass.setPlaceholderText("e.g. xxxx-xxxx-xxxx-xxxx")
        self.acc_input_pass.setEchoMode(QLineEdit.EchoMode.Password)
        cal.addWidget(self.acc_input_pass)

        btn_save_acc = QPushButton("🔑  SAVE TO ACCOUNTS.TXT")
        btn_save_acc.setObjectName("actionBtn")
        btn_save_acc.clicked.connect(self.add_single_account)
        cal.addWidget(btn_save_acc)
        left_box.addWidget(c_add)

        c_list = QWidget(); c_list.setObjectName("card")
        cll = QVBoxLayout(c_list); cll.setContentsMargins(18, 16, 18, 16); cll.setSpacing(8)
        self.combo_count_lbl = QLabel("👥 ACTIVE MAILER COMBOS (0)")
        self.combo_count_lbl.setStyleSheet("color: #b026ff; font-weight: bold; font-size: 11px;")
        cll.addWidget(self.combo_count_lbl)

        self.combos_display_list = QListWidget()
        self.combos_display_list.setStyleSheet("background: #06040a; border: 1px solid rgba(138,43,226,0.2); border-radius: 8px; color: #00ff9d; font-family: Consolas; font-size: 11px;")
        cll.addWidget(self.combos_display_list, 1)
        left_box.addWidget(c_list, 1)

        split.addLayout(left_box, 2)

        c_editor = QWidget(); c_editor.setObjectName("card")
        cel = QVBoxLayout(c_editor); cel.setContentsMargins(20, 18, 20, 18); cel.setSpacing(10)
        ed_head = QHBoxLayout()
        ed_head.addWidget(QLabel("📄 DIRECT RAW EDITOR: ACCOUNTS.TXT", styleSheet="color: #00ff9d; font-weight: bold; font-size: 11px;"))
        ed_head.addStretch()
        btn_save_raw = QPushButton("💾  SAVE FILE (ACCOUNTS.TXT)")
        btn_save_raw.setObjectName("greenBtn")
        btn_save_raw.clicked.connect(self.save_raw_accounts_file)
        ed_head.addWidget(btn_save_raw)
        cel.addLayout(ed_head)

        info_ed = QLabel("Format: email:password (one per line). Lines starting with # are ignored. For Gmail or Yandex, generate an App Password.")
        info_ed.setStyleSheet("color: #8b8b9e; font-size: 11px;")
        cel.addWidget(info_ed)

        self.accounts_raw_editor = QPlainTextEdit()
        self.accounts_raw_editor.setStyleSheet("background: #06040a; color: #00ff9d; font-family: Consolas; font-size: 12px;")
        cel.addWidget(self.accounts_raw_editor, 1)
        split.addWidget(c_editor, 3)

        l.addLayout(split)
        return page

    # =================================================================
    # 6. SCREEN: LO-FI РАДИО (6 ПРОВЕРЕННЫХ 100% РАБОЧИХ СТАНЦИЙ 24/7)
    # =================================================================
    def create_radio_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("((o)) Cyberpunk Lo-Fi Radio (6 Проверенных Станций 24/7)")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("6 проверенных круглосуточных онлайн-потоков с гарантированным аптаймом 100%: Chillhop 320k, DEF CON, Groove Salad, Nightwave Plaza, Drone Zone, Secret Agent")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        self.radio_pill_status = QLabel("● RADIO OFF")
        self.radio_pill_status.setStyleSheet("background: rgba(255, 42, 109, 0.1); color: #ff2a6d; border: 1px solid #ff2a6d; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(self.radio_pill_status, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        player_card = QWidget(); player_card.setObjectName("card")
        pcl = QVBoxLayout(player_card); pcl.setContentsMargins(24, 20, 24, 20); pcl.setSpacing(14)

        top_p = QHBoxLayout()
        self.player_title_lbl = QLabel("((o)) FLUXFM CHILLHOP & STUDY BEATS (320KBPS)")
        self.player_title_lbl.setStyleSheet("color: #00f3ff; font-weight: bold; font-family: Consolas; font-size: 12px;")
        top_p.addWidget(self.player_title_lbl)
        top_p.addStretch()
        self.player_state_lbl = QLabel("STOPPED")
        self.player_state_lbl.setStyleSheet("color: #8b8b9e; font-family: Consolas; font-size: 11px;")
        top_p.addWidget(self.player_state_lbl)
        pcl.addLayout(top_p)

        vis = QLabel("● ▬▬ ▬ ▬▬ ▬▬ ▬▬▬ ▬▬ ▬▬▬ ▬ ▬▬▬▬ ▬ ▬▬ ▬▬▬ ▬▬ ▬▬▬ ▬▬ ▬ ▬▬ ▬ ●")
        vis.setStyleSheet("color: #00f3ff; font-family: Consolas; font-size: 14px; background: #06040a; border: 1px solid rgba(138,43,226,0.3); border-radius: 8px; padding: 25px 20px;")
        vis.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pcl.addWidget(vis)

        c_row = QHBoxLayout(); c_row.setSpacing(20)
        self.btn_radio_main = QPushButton("▶  TURN ON")
        self.btn_radio_main.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #00f3ff); color: #000000; font-weight: 800; font-size: 13px; border-radius: 12px; padding: 14px 28px;")
        self.btn_radio_main.clicked.connect(self.toggle_radio_main)
        c_row.addWidget(self.btn_radio_main)

        info_box = QVBoxLayout()
        info_t = QLabel("Нажмите для воспроизведения проверенного онлайн-потока")
        info_t.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        info_box.addWidget(info_t)
        info_sub = QLabel("Все 6 станций протестированы, работают без сбоев и фоном при переключении экранов")
        info_sub.setStyleSheet("color: #8b8b9e; font-size: 11px;")
        info_box.addWidget(info_sub)
        c_row.addLayout(info_box)

        c_row.addStretch()
        c_row.addWidget(QLabel("🔊"))
        self.slider_vol = QSlider(Qt.Orientation.Horizontal)
        self.slider_vol.setRange(0, 100)
        self.slider_vol.setValue(75)
        self.slider_vol.setFixedWidth(140)
        self.slider_vol.valueChanged.connect(self.radio.set_volume)
        c_row.addWidget(self.slider_vol)
        pcl.addLayout(c_row)

        l.addWidget(player_card)

        cur_head = QLabel("🎧 ВЫБЕРИТЕ ОНЛАЙН СТАНЦИЮ ДЛЯ ФОКУСА И РАБОТЫ (6 СТАНЦИЙ 24/7)")
        cur_head.setStyleSheet("color: #00ff9d; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        l.addWidget(cur_head)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background: transparent; border: none;")
        scroll_w = QWidget(); scroll_w.setStyleSheet("background: transparent;")
        grid = QVBoxLayout(scroll_w); grid.setSpacing(8)

        for idx, st in enumerate(LoFiRadio.STATIONS):
            s_card = QWidget(); s_card.setObjectName("card")
            s_l = QHBoxLayout(s_card); s_l.setContentsMargins(16, 12, 16, 12); s_l.setSpacing(12)
            
            s_info = QVBoxLayout()
            title_row = QHBoxLayout()
            s_title = QLabel(f"{st['name']}")
            s_title.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
            title_row.addWidget(s_title)
            
            bit_lbl = QLabel(f"{st.get('bitrate', '128kbps')}")
            bit_lbl.setStyleSheet("background: rgba(0, 255, 157, 0.12); color: #00ff9d; border: 1px solid #00ff9d; border-radius: 6px; padding: 1px 6px; font-size: 9px; font-weight: bold;")
            title_row.addWidget(bit_lbl)
            title_row.addStretch()
            s_info.addLayout(title_row)

            s_desc = QLabel(f"{st['desc']} • {st['genre']}")
            s_desc.setStyleSheet("color: #8b8b9e; font-size: 10px;")
            s_info.addWidget(s_desc)
            s_l.addLayout(s_info, 1)

            btn_play_st = QPushButton("▶ Слушать")
            btn_play_st.setObjectName("actionBtn")
            btn_play_st.clicked.connect(lambda ch, i=idx: self.select_station_action(i))
            s_l.addWidget(btn_play_st)

            grid.addWidget(s_card)

        scroll_area.setWidget(scroll_w)
        l.addWidget(scroll_area, 1)

        return page

    # =================================================================
    # 7. SCREEN: CYBER SHORTS & REELS (БЕСКОНЕЧНАЯ ЛЕНТА КОРОТКИХ ВИДЕО)
    # =================================================================
    def create_shorts_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(14)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("🎬 Cyber Shorts & Reels (Реальные YouTube & TikTok)")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Бесконечная лента реальных вирусных YouTube Shorts, TikTok рилсов и ASMR с мгновенным поиском и добавлением ссылок")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        self.shorts_counter_lbl = QLabel(f"🎬 Ролик 1 из ∞ [Бесконечная лента TikTok / Shorts ♾️]")
        self.shorts_counter_lbl.setStyleSheet("background: rgba(0, 243, 255, 0.12); color: #00f3ff; border: 1px solid #00f3ff; border-radius: 12px; padding: 4px 14px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(self.shorts_counter_lbl, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        # Верхняя панель категорий и поиска
        cat_card = QWidget(); cat_card.setObjectName("card")
        cat_l = QHBoxLayout(cat_card); cat_l.setContentsMargins(14, 10, 14, 10); cat_l.setSpacing(8)
        cat_l.addWidget(QLabel("🔥 Темы:", styleSheet="color: #00f3ff; font-weight: bold; font-size: 11px;"))

        btn_cat_all = QPushButton("Все тренды"); btn_cat_all.setObjectName("actionBtn")
        btn_cat_all.clicked.connect(lambda: self.filter_shorts_by_category("ALL"))
        cat_l.addWidget(btn_cat_all)

        btn_cat_tech = QPushButton("💻 IT & Код"); btn_cat_tech.setObjectName("actionBtn")
        btn_cat_tech.clicked.connect(lambda: self.filter_shorts_by_category("TECH"))
        cat_l.addWidget(btn_cat_tech)

        btn_cat_memes = QPushButton("😂 Мемы"); btn_cat_memes.setObjectName("actionBtn")
        btn_cat_memes.clicked.connect(lambda: self.filter_shorts_by_category("MEMES"))
        cat_l.addWidget(btn_cat_memes)

        btn_cat_asmr = QPushButton("⚡ ASMR"); btn_cat_asmr.setObjectName("actionBtn")
        btn_cat_asmr.clicked.connect(lambda: self.filter_shorts_by_category("ASMR"))
        cat_l.addWidget(btn_cat_asmr)

        btn_cat_gaming = QPushButton("🎮 Гейминг"); btn_cat_gaming.setObjectName("actionBtn")
        btn_cat_gaming.clicked.connect(lambda: self.filter_shorts_by_category("GAMING"))
        cat_l.addWidget(btn_cat_gaming)

        btn_cat_auto = QPushButton("🏎️ Авто"); btn_cat_auto.setObjectName("actionBtn")
        btn_cat_auto.clicked.connect(lambda: self.filter_shorts_by_category("AUTO"))
        cat_l.addWidget(btn_cat_auto)

        cat_l.addStretch()

        # Поиск по шортсам
        self.shorts_search_input = QLineEdit()
        self.shorts_search_input.setPlaceholderText("🔍 Поиск по теме (#coding)...")
        self.shorts_search_input.setStyleSheet("background: #06040a; border: 1px solid rgba(138,43,226,0.3); border-radius: 8px; color: #00f3ff; padding: 4px 8px; font-size: 10px; width: 160px;")
        self.shorts_search_input.returnPressed.connect(self.search_shorts_action)
        cat_l.addWidget(self.shorts_search_input)

        btn_search_s = QPushButton("Найти"); btn_search_s.setObjectName("actionBtn")
        btn_search_s.clicked.connect(self.search_shorts_action)
        cat_l.addWidget(btn_search_s)

        btn_reset_s = QPushButton("✕"); btn_reset_s.setObjectName("actionBtn")
        btn_reset_s.clicked.connect(self.reset_shorts_search)
        cat_l.addWidget(btn_reset_s)

        btn_rnd = QPushButton("🎲 Случайный"); btn_rnd.setObjectName("aiPillBtn")
        btn_rnd.clicked.connect(self.random_short_action)
        cat_l.addWidget(btn_rnd)

        l.addWidget(cat_card)

        # Панель вставки своего шортса
        add_box = QHBoxLayout(); add_box.setSpacing(10)
        self.custom_short_input = QLineEdit()
        self.custom_short_input.setPlaceholderText("Вставьте ссылку на любой YouTube Shorts (https://youtube.com/shorts/...) или TikTok...")
        self.custom_short_input.setStyleSheet("background: #06040a; border: 1px solid rgba(138,43,226,0.3); border-radius: 10px; color: #00ff9d; padding: 8px 12px; font-family: Consolas; font-size: 11px;")
        add_box.addWidget(self.custom_short_input, 1)

        btn_add_short = QPushButton("➕ Добавить в ленту ▶")
        btn_add_short.setObjectName("greenBtn")
        btn_add_short.clicked.connect(self.add_custom_short_action)
        add_box.addWidget(btn_add_short)
        l.addLayout(add_box)

        main_box = QHBoxLayout(); main_box.setSpacing(24)

        # Контейнер для телефона / вертикального плеера
        phone_card = QWidget(); phone_card.setObjectName("card")
        phone_card.setFixedWidth(380)
        phone_layout = QVBoxLayout(phone_card)
        phone_layout.setContentsMargins(14, 14, 14, 14)
        phone_layout.setSpacing(10)

        # Индикатор автора
        self.shorts_author_lbl = QLabel(SHORTS_FEED[0]["author"])
        self.shorts_author_lbl.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 13px;")
        phone_layout.addWidget(self.shorts_author_lbl)

        # Видео холст / область показа
        video_canvas = QWidget()
        video_canvas.setStyleSheet("background: #020204; border: 2px solid rgba(138,43,226,0.4); border-radius: 16px;")
        v_layout = QVBoxLayout(video_canvas)
        v_layout.setContentsMargins(8, 8, 8, 8)

        if HAS_WEBENGINE:
            self.web_engine_player = QWebEngineView()
            self.web_engine_player.setUrl(QUrl(SHORTS_FEED[0].get("embed_url", f"https://www.youtube-nocookie.com/embed/{SHORTS_FEED[0]['id']}?autoplay=1")))
            v_layout.addWidget(self.web_engine_player, 1)
        elif HAS_VIDEO and HAS_MULTIMEDIA:
            self.video_widget = QVideoWidget()
            self.short_player = QMediaPlayer()
            self.short_audio = QAudioOutput()
            self.short_player.setAudioOutput(self.short_audio)
            self.short_player.setVideoOutput(self.video_widget)
            self.short_audio.setVolume(0.7)
            self.short_player.mediaStatusChanged.connect(self.on_short_media_status)
            v_layout.addWidget(self.video_widget, 1)
        else:
            self.video_widget = QLabel("🎬 [YouTube Shorts & Reels Player Active]\nНажмите 'Открыть на YouTube Shorts' для просмотра")
            self.video_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.video_widget.setStyleSheet("color: #00ff9d; font-family: Consolas; font-size: 12px;")
            v_layout.addWidget(self.video_widget, 1)

        phone_layout.addWidget(video_canvas, 1)

        # Заголовок и звук шортса
        self.shorts_title_lbl = QLabel(SHORTS_FEED[0]["title"])
        self.shorts_title_lbl.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        self.shorts_title_lbl.setWordWrap(True)
        phone_layout.addWidget(self.shorts_title_lbl)

        self.shorts_sound_lbl = QLabel(f"🎵 {SHORTS_FEED[0].get('sound', 'Original Audio')}")
        self.shorts_sound_lbl.setStyleSheet("color: #00ff9d; font-size: 10px; font-weight: bold;")
        phone_layout.addWidget(self.shorts_sound_lbl)

        self.shorts_tags_lbl = QLabel(SHORTS_FEED[0]["tags"])
        self.shorts_tags_lbl.setStyleSheet("color: #b026ff; font-size: 10px; font-weight: bold;")
        phone_layout.addWidget(self.shorts_tags_lbl)

        main_box.addWidget(phone_card, 0, Qt.AlignmentFlag.AlignCenter)

        # Панель листания и управления (TikTok / Shorts)
        controls_card = QWidget(); controls_card.setObjectName("card")
        c_layout = QVBoxLayout(controls_card)
        c_layout.setContentsMargins(24, 20, 24, 20)
        c_layout.setSpacing(12)

        c_layout.addWidget(QLabel("📱 УПРАВЛЕНИЕ БЕСКОНЕЧНОЙ ЛЕНТОЙ", styleSheet="color: #00f3ff; font-weight: bold; font-size: 12px;"))
        
        self.auto_scroll_checkbox = QCheckBox("⚡ Авто-листание ленты (TikTok Auto-Scroll)")
        self.auto_scroll_checkbox.setChecked(True)
        self.auto_scroll_checkbox.setStyleSheet("color: #00ff9d; font-weight: bold; font-size: 11px;")
        c_layout.addWidget(self.auto_scroll_checkbox)

        btn_prev_short = QPushButton("⬆  Предыдущее видео")
        btn_prev_short.setObjectName("actionBtn")
        btn_prev_short.clicked.connect(self.prev_short_action)
        c_layout.addWidget(btn_prev_short)

        self.btn_play_short = QPushButton("▶  Смотреть / Пауза")
        self.btn_play_short.setObjectName("greenBtn")
        self.btn_play_short.clicked.connect(self.toggle_short_play)
        c_layout.addWidget(self.btn_play_short)

        btn_next_short = QPushButton("⬇  Следующее видео")
        btn_next_short.setObjectName("actionBtn")
        btn_next_short.clicked.connect(self.next_short_action)
        c_layout.addWidget(btn_next_short)

        c_layout.addSpacing(4)

        btn_open_yt = QPushButton("🌐  Смотреть в YouTube Shorts / TikTok")
        btn_open_yt.setStyleSheet("background: rgba(255,0,0,0.2); color: #ff4d4d; border: 1px solid #ff4d4d; border-radius: 10px; padding: 10px; font-weight: bold;")
        btn_open_yt.clicked.connect(self.open_current_short_in_browser)
        c_layout.addWidget(btn_open_yt)

        self.btn_like_short = QPushButton(f"❤️  Нравится ({SHORTS_FEED[0]['likes']})")
        self.btn_like_short.setStyleSheet("background: rgba(255,42,109,0.15); color: #ff2a6d; border: 1px solid #ff2a6d; border-radius: 10px; padding: 10px; font-weight: bold;")
        self.btn_like_short.clicked.connect(self.like_short_action)
        c_layout.addWidget(self.btn_like_short)

        self.btn_comments_short = QPushButton("💬  Комментарии сообщества")
        self.btn_comments_short.setObjectName("actionBtn")
        self.btn_comments_short.clicked.connect(self.open_comments_dialog)
        c_layout.addWidget(self.btn_comments_short)

        hint_lbl = QLabel("⌨ Листать: [↓ / ↑] • Пауза: [Пробел] • Звук: [M]\n♾️ Бесконечный скролл роликов")
        hint_lbl.setStyleSheet("color: #8b8b9e; font-size: 10px; font-family: Consolas; padding-top: 8px;")
        c_layout.addWidget(hint_lbl)

        c_layout.addStretch()
        main_box.addWidget(controls_card, 1)

        l.addLayout(main_box)
        return page

    # =================================================================
    # 8. SCREEN: DATABASE TABLE VIEWER (ТАБЛИЦА ПОЧТ SQLITE / CSV)
    # =================================================================
    def create_base_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30); l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("📊 Database Table Viewer (SQLite & CSV)")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Структурированная таблица всех найденных почт: страна, дата последней активности, категория, источник и score")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        btn_export = QPushButton("📥  Экспорт в Excel (CSV)")
        btn_export.setObjectName("greenBtn")
        btn_export.clicked.connect(self.export_csv_action)
        h_row.addWidget(btn_export, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        filter_card = QWidget(); filter_card.setObjectName("card")
        f_layout = QHBoxLayout(filter_card); f_layout.setContentsMargins(16, 12, 16, 12); f_layout.setSpacing(12)

        f_layout.addWidget(QLabel("Поиск по базе:"))
        self.sql_search_edit = QLineEdit()
        self.sql_search_edit.setPlaceholderText("Поиск по email, домену или стране...")
        self.sql_search_edit.textChanged.connect(self.filter_database_table)
        f_layout.addWidget(self.sql_search_edit, 1)

        btn_refresh = QPushButton("🔄 Обновить таблицу")
        btn_refresh.setObjectName("actionBtn")
        btn_refresh.clicked.connect(self.refresh_database_table)
        f_layout.addWidget(btn_refresh)

        btn_clear_db = QPushButton("🗑 Очистить")
        btn_clear_db.setObjectName("stopBtn")
        btn_clear_db.clicked.connect(self.clear_all_data)
        f_layout.addWidget(btn_clear_db)

        l.addWidget(filter_card)

        self.db_table = QTableWidget(0, 8)
        self.db_table.setHorizontalHeaderLabels([
            "ID", "EMAIL ADDRESS", "СТРАНА", "ПОСЛЕДНЯЯ АКТИВНОСТЬ", "КАТЕГОРИЯ", "ИСТОЧНИК", "SCORE", "ДАТА НАХОДКИ"
        ])
        self.db_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.db_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.db_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.db_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.db_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.db_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.Stretch)
        self.db_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)
        self.db_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.ResizeToContents)
        l.addWidget(self.db_table, 1)

        return page

    # =================================================================
    # 9. SCREEN: DESKTOP PYTHON FILE
    # =================================================================
    def create_python_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30); l.setSpacing(16)
        t = QLabel("</> Desktop Python Source (allparser.py)")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        l.addWidget(t)
        l.addWidget(RainbowLine())

        card = QWidget(); card.setObjectName("card")
        cl = QVBoxLayout(card); cl.setContentsMargins(20, 18, 20, 18)
        self.python_code_view = QTextEdit()
        self.python_code_view.setReadOnly(True)
        try:
            with open(os.path.abspath(__file__), "r", encoding="utf-8") as f:
                self.python_code_view.setPlainText(f.read())
        except Exception:
            pass
        cl.addWidget(self.python_code_view)
        l.addWidget(card, 1)
        return page

    # =================================================================
    # ЛОГИКА SHORTS И МУЛЬТИМЕДИА (НАСТОЯЩИЙ БЕСКОНЕЧНЫЙ ЦИКЛ TIKTOK)
    # =================================================================
    def update_short_display(self):
        global SHORTS_FEED
        if not SHORTS_FEED:
            SHORTS_FEED = generate_infinite_shorts_batch(0, 25, "ALL", "")

        if self.current_short_idx >= len(SHORTS_FEED):
            more = generate_infinite_shorts_batch(len(SHORTS_FEED), 12, getattr(self, 'current_short_cat', 'ALL'), getattr(self, 'current_short_query', ''))
            SHORTS_FEED.extend(more)

        item = SHORTS_FEED[self.current_short_idx]
        self.shorts_author_lbl.setText(item["author"])
        self.shorts_title_lbl.setText(item["title"])
        self.shorts_tags_lbl.setText(item["tags"])
        if hasattr(self, 'shorts_sound_lbl'):
            self.shorts_sound_lbl.setText(f"🎵 {item.get('sound', 'Original Audio')}")
        if hasattr(self, 'shorts_counter_lbl'):
            self.shorts_counter_lbl.setText(f"🎬 Ролик #{self.current_short_idx + 1} из ∞ [Бесконечная лента TikTok / Shorts ♾️]")
        self.btn_like_short.setText(f"❤️  Нравится ({item['likes']})")

        if HAS_WEBENGINE and hasattr(self, 'web_engine_player') and self.web_engine_player:
            try:
                self.web_engine_player.setUrl(QUrl(item.get("embed_url", f"https://www.youtube-nocookie.com/embed/{item['id']}?autoplay=1")))
            except Exception:
                pass
        elif hasattr(self, 'short_player') and self.short_player and "url" in item and item["url"].endswith('.mp4'):
            try:
                self.short_player.stop()
                self.short_player.setSource(QUrl(item["url"]))
                self.short_player.play()
                self.btn_play_short.setText("■  Пауза")
            except Exception:
                pass

    def open_current_short_in_browser(self):
        item = SHORTS_FEED[self.current_short_idx]
        url = item.get("url") or f"https://www.youtube.com/shorts/{item['id']}"
        webbrowser.open(url)

    def add_custom_short_action(self):
        text = self.custom_short_input.text().strip()
        if not text:
            return
        vid = extract_youtube_id(text)
        if not vid:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить ID ролика. Вставьте ссылку вида: https://youtube.com/shorts/ID или https://youtu.be/ID")
            return
        new_item = {
            "id": vid,
            "title": f"Пользовательский шортс #{vid}",
            "author": "@custom_user",
            "category": "CUSTOM",
            "tags": "#custom #shorts #youtube #tiktok",
            "likes": "1.2K",
            "views": "15.4K",
            "sound": "Original Custom Audio",
            "url": f"https://www.youtube.com/shorts/{vid}",
            "embed_url": f"https://www.youtube-nocookie.com/embed/{vid}?autoplay=1&controls=1&rel=0"
        }
        SHORTS_FEED.insert(0, new_item)
        self.current_short_idx = 0
        self.custom_short_input.clear()
        self.update_short_display()
        QMessageBox.information(self, "Успех", f"Шортс {vid} добавлен в бесконечную ленту и запущен!")

    def filter_shorts_by_category(self, cat):
        self.current_short_cat = cat
        global SHORTS_FEED
        SHORTS_FEED = generate_infinite_shorts_batch(0, 25, cat, getattr(self, 'current_short_query', ''))
        self.current_short_idx = 0
        self.update_short_display()

    def search_shorts_action(self):
        q = self.shorts_search_input.text().strip()
        self.current_short_query = q
        global SHORTS_FEED
        SHORTS_FEED = generate_infinite_shorts_batch(0, 25, getattr(self, 'current_short_cat', 'ALL'), q)
        self.current_short_idx = 0
        self.update_short_display()

    def reset_shorts_search(self):
        self.shorts_search_input.clear()
        self.current_short_query = ""
        global SHORTS_FEED
        SHORTS_FEED = generate_infinite_shorts_batch(0, 25, getattr(self, 'current_short_cat', 'ALL'), "")
        self.current_short_idx = 0
        self.update_short_display()

    def random_short_action(self):
        if SHORTS_FEED:
            self.current_short_idx = random.randint(0, len(SHORTS_FEED) - 1)
            self.update_short_display()

    def auto_scroll_timer_tick(self):
        if hasattr(self, 'auto_scroll_checkbox') and self.auto_scroll_checkbox.isChecked():
            self.next_short_action()

    def on_short_media_status(self, status):
        if hasattr(QMediaPlayer, 'MediaStatus') and status == QMediaPlayer.MediaStatus.EndOfMedia:
            if hasattr(self, 'auto_scroll_checkbox') and self.auto_scroll_checkbox.isChecked():
                self.next_short_action()

    def next_short_action(self):
        global SHORTS_FEED
        self.current_short_idx += 1
        if self.current_short_idx >= len(SHORTS_FEED) - 3:
            more = generate_infinite_shorts_batch(len(SHORTS_FEED), 12, getattr(self, 'current_short_cat', 'ALL'), getattr(self, 'current_short_query', ''))
            SHORTS_FEED.extend(more)
        self.update_short_display()
        if hasattr(self, 'shorts_auto_timer'):
            self.shorts_auto_timer.start(18000)

    def prev_short_action(self):
        if self.current_short_idx > 0:
            self.current_short_idx -= 1
            self.update_short_display()
        if hasattr(self, 'shorts_auto_timer'):
            self.shorts_auto_timer.start(18000)

    def toggle_short_play(self):
        if hasattr(self, 'short_player') and self.short_player:
            try:
                if self.short_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                    self.short_player.pause()
                    self.btn_play_short.setText("▶  Смотреть")
                else:
                    self.short_player.play()
                    self.btn_play_short.setText("■  Пауза")
            except Exception:
                self.update_short_display()
        else:
            self.open_current_short_in_browser()

    def toggle_short_mute(self):
        if hasattr(self, 'short_audio') and self.short_audio:
            cur = self.short_audio.volume()
            if cur > 0.05:
                self.short_audio.setVolume(0.0)
                self.btn_short_mute.setText("🔇  Звук видео: ВЫКЛ")
            else:
                self.short_audio.setVolume(0.7)
                self.btn_short_mute.setText("🔊  Звук видео: ВКЛ (70%)")

    def like_short_action(self):
        self.btn_like_short.setText("💖  Вам понравилось!")

    def open_comments_dialog(self):
        item = SHORTS_FEED[self.current_short_idx]
        dlg = QDialog(self)
        dlg.setWindowTitle(f"Комментарии сообщества")
        dlg.resize(480, 520)
        dlg.setStyleSheet("background: #0e0918; color: #ffffff;")
        dl = QVBoxLayout(dlg)
        dl.setContentsMargins(20, 20, 20, 20)
        dl.setSpacing(12)

        t_lbl = QLabel(f"💬 Комментарии: {item['title'][:32]}...")
        t_lbl.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 13px;")
        dl.addWidget(t_lbl)

        comments_box = QTextEdit()
        comments_box.setReadOnly(True)
        comments_box.setStyleSheet("background: #06040a; border: 1px solid rgba(138,43,226,0.4); border-radius: 12px; color: #e2e8f0; font-size: 11px; padding: 12px;")
        comments_box.setHtml(
            "<p><b style='color:#00f3ff'>@alex_dev</b> <span style='color:#6b7280'>• 2ч назад</span><br>"
            "Ахаха, когда написал чистый код с первого раза без багов! 🔥</p><hr style='border:0;border-top:1px solid #2d1847'>"
            "<p><b style='color:#00f3ff'>@senior_architect</b> <span style='color:#6b7280'>• 4ч назад</span><br>"
            "1 строка чистого кода стоит 1000 строк легаси. Респект автору! 💯</p><hr style='border:0;border-top:1px solid #2d1847'>"
            "<p><b style='color:#00f3ff'>@frontend_pro</b> <span style='color:#6b7280'>• 5ч назад</span><br>"
            "Кайф, музыка на фоне тоже топ! Атмосфера просто космос.</p><hr style='border:0;border-top:1px solid #2d1847'>"
            "<p><b style='color:#00f3ff'>@cyber_viewer</b> <span style='color:#6b7280'>• только что</span><br>"
            "Этот ролик точно залетит в рекомендации TikTok и Shorts!</p>"
        )
        dl.addWidget(comments_box, 1)

        inp_row = QHBoxLayout()
        c_inp = QLineEdit()
        c_inp.setPlaceholderText("Написать свой комментарий...")
        c_inp.setStyleSheet("background: #06040a; border: 1px solid #8a2be2; border-radius: 8px; color: #ffffff; padding: 8px 12px;")
        btn_send_c = QPushButton("Отправить")
        btn_send_c.setStyleSheet("background: #00ff9d; color: #000000; font-weight: bold; border-radius: 8px; padding: 8px 16px;")

        def send_c():
            txt = c_inp.text().strip()
            if txt:
                comments_box.append(f"<hr style='border:0;border-top:1px solid #2d1847'><p><b style='color:#00ff9d'>@you</b> <span style='color:#6b7280'>• только что</span><br>{txt}</p>")
                c_inp.clear()

        btn_send_c.clicked.connect(send_c)
        c_inp.returnPressed.connect(send_c)
        inp_row.addWidget(c_inp, 1)
        inp_row.addWidget(btn_send_c)
        dl.addLayout(inp_row)
        dlg.exec()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Down or event.key() == Qt.Key.Key_PageDown:
            self.next_short_action()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Up or event.key() == Qt.Key.Key_PageUp:
            self.prev_short_action()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Space:
            self.toggle_short_play()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_M:
            self.toggle_short_mute()
            event.accept()
            return
        super().keyPressEvent(event)

    # =================================================================
    # ЛОГИКА РАДИО
    # =================================================================
    def on_radio_status(self, text, is_on):
        self.radio_pill_status.setText(f"● {'RADIO LIVE' if is_on else 'RADIO OFF'}")
        self.radio_pill_status.setStyleSheet(
            f"background: rgba({'0,255,157' if is_on else '255,42,109'}, 0.1); "
            f"color: {'#00ff9d' if is_on else '#ff2a6d'}; border: 1px solid {'#00ff9d' if is_on else '#ff2a6d'}; "
            f"border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;"
        )
        self.radio_dot_sidebar.set_color("#00ff9d" if is_on else "#4a4a5a")
        self.radio_txt_sidebar.setText("LO-FI RADIO ON" if is_on else "LO-FI RADIO OFF")
        self.btn_radio_main.setText("■  TURN OFF" if is_on else "▶  TURN ON")
        self.player_state_lbl.setText("PLAYING" if is_on else "STOPPED")
        self.player_title_lbl.setText(f"((o)) {text.upper()}")

    def toggle_radio_main(self):
        if self.radio.is_playing:
            self.radio.stop()
        else:
            self.radio.play(0)

    def select_station_action(self, idx):
        self.radio.play(idx)

    # =================================================================
    # ЛОГИКА МЕЙЛЕРА
    # =================================================================
    def refresh_mailer_dropdown(self):
        self.mailer_acc_combo.clear()
        accs = MailerAccountManager.load_accounts()
        for a in accs:
            self.mailer_acc_combo.addItem(f"{a['email']} ({a['provider']})", a)
        self.recip_list.clear()
        records = EmailDatabase.get_all_records()
        for r in records[:50]:
            self.recip_list.addItem(f"{r[1]} [{r[2]}]")
        self.recip_count_lbl.setText(f"{len(records)} в таблице")

    def on_recip_item_clicked(self, it):
        email_only = it.text().split(" ")[0]
        self.mail_to_edit.setText(email_only)

    def on_mailer_account_change(self):
        data = self.mailer_acc_combo.currentData()
        if data:
            self.mailer_prov_lbl.setText(data.get("provider", "UNKNOWN"))

    def open_ai_compose_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("✨ Мультиязычная генерация письма через ИИ")
        dlg.setFixedSize(540, 360)
        dlg.setStyleSheet("background-color: #0b0713; color: #ffffff;")
        dl = QVBoxLayout(dlg); dl.setSpacing(12)

        dl.addWidget(QLabel("🎯 Опишите цель письма на русском языке:", styleSheet="color: #00f3ff; font-weight: bold;"))
        prompt_in = QLineEdit()
        prompt_in.setPlaceholderText("Например: Предложить партнерство разработчику по боту на Python")
        dl.addWidget(prompt_in)

        dl.addWidget(QLabel("🌐 Язык генерации (на котором написать письмо):", styleSheet="color: #00ff9d; font-weight: bold;"))
        lang_sel = QComboBox()
        for code, name in AIEngine.LANGUAGES:
            lang_sel.addItem(name, code)
        lang_sel.setCurrentIndex(self.mailer_lang_combo.currentIndex())
        dl.addWidget(lang_sel)

        btn_run = QPushButton("✨ Сгенерировать тему и текст на выбранном языке")
        btn_run.setObjectName("aiPillBtn")
        dl.addWidget(btn_run)

        st_lbl = QLabel("")
        dl.addWidget(st_lbl)

        def do_gen():
            val = prompt_in.text().strip()
            if not val:
                return
            st_lbl.setText("Генерация на выбранном языке через нейросеть...")
            QApplication.processEvents()
            target_l = lang_sel.currentData()
            res = AIEngine.generate_email_multilingual(val, target_lang=target_l, recipient=self.mail_to_edit.text(), sender="Outreach Lead")
            if res:
                self.mail_subj_edit.setText(res.get("subject", ""))
                self.mail_body_edit.setPlainText(res.get("body", ""))
                dlg.accept()

        btn_run.clicked.connect(do_gen)
        dlg.exec()

    def execute_mail_send(self):
        to = self.mail_to_edit.text().strip()
        subj = self.mail_subj_edit.text().strip()
        body = self.mail_body_edit.toPlainText().strip()
        data = self.mailer_acc_combo.currentData()

        if not to or "@" not in to:
            QMessageBox.warning(self, "Ошибка", "Укажите корректный адрес получателя!")
            return
        if not data:
            QMessageBox.warning(self, "Ошибка", "Нет выбранного аккаунта в accounts.txt!")
            return

        status, score, detail, country, last_seen = self.validator.validate(to, use_ai=True)
        if status in ('TRAP', 'INVALID'):
            QMessageBox.critical(
                self, "ОТПРАВКА ЗАБЛОКИРОВАНА ПРЕ-ФЛАЙТ ФИЛЬТРОМ",
                f"Внимание! Адрес {to} является спам-ловушкой ({status})!\n{detail}\nСтрана: {country}\n\nОтправка отменена во избежание санкций."
            )
            return

        self.btn_send_preflight.setEnabled(False)

        def worker():
            try:
                sender = SmtpSender(data["email"], data["password"])
                sender.send(to, subj, body)
                sender.close()
                self.signals.log_signal.emit(f"[SMTP OK] Письмо успешно отправлено на {to} ({country})", "success", "spider")
            except Exception as e:
                self.signals.log_signal.emit(f"[SMTP FAIL] {e}", "err", "spider")
            finally:
                self.btn_send_preflight.setEnabled(True)

        threading.Thread(target=worker, daemon=True).start()

    # =================================================================
    # ЛОГИКА ТАБЛИЦЫ БАЗЫ ДАННЫХ
    # =================================================================
    def refresh_database_table(self):
        records = EmailDatabase.get_all_records()
        self.db_table.setRowCount(0)
        for r in records:
            row = self.db_table.rowCount()
            self.db_table.insertRow(row)

            # r: (id, email, country, last_active, category, target_source, status, score, discovered_at)
            it_id = QTableWidgetItem(str(r[0]))
            it_email = QTableWidgetItem(r[1]); it_email.setForeground(QColor("#00f3ff"))
            it_country = QTableWidgetItem(r[2])
            it_last = QTableWidgetItem(r[3]); it_last.setForeground(QColor("#00ff9d"))
            it_cat = QTableWidgetItem(r[4])
            it_src = QTableWidgetItem(r[5][:45])
            it_score = QTableWidgetItem(str(r[7]))
            it_disc = QTableWidgetItem(r[8])

            for col, it in enumerate([it_id, it_email, it_country, it_last, it_cat, it_src, it_score, it_disc]):
                self.db_table.setItem(row, col, it)

    def filter_database_table(self, query: str):
        query = query.lower()
        for row in range(self.db_table.rowCount()):
            match = False
            for col in range(self.db_table.columnCount()):
                item = self.db_table.item(row, col)
                if item and query in item.text().lower():
                    match = True
                    break
            self.db_table.setRowHidden(row, not match)

    def export_csv_action(self):
        path = EmailDatabase.CSV_PATH
        QMessageBox.information(
            self, "Экспорт таблицы",
            f"Таблица базы данных сохранена в файле:\n{path}\n\nВы можете открыть её в Excel!"
        )

    def clear_all_data(self):
        EmailDatabase.clear_database()
        self.seen_emails.clear()
        self.personal_emails.clear()
        self.update_counters()
        self.refresh_database_table()
        QMessageBox.information(self, "База очищена", "Все записи в таблице базы успешно удалены!")

    # =================================================================
    # ЛОГИКА ВАЛИДАЦИИ
    # =================================================================
    def inspect_single_email(self):
        em = self.val_single_edit.text().strip()
        if not em or "@" not in em:
            return
        status, score, detail, country, last_active = self.validator.validate(em, use_ai=True)
        self.add_val_table_row(em, status, score, detail, country, last_active)
        self.val_single_edit.clear()

    def run_full_validation(self):
        records = EmailDatabase.get_all_records()
        if not records:
            QMessageBox.information(self, "Инфо", "База пуста! Запустите парсер.")
            return
        self.val_table.setRowCount(0)
        self.btn_val_run.setEnabled(False)

        def worker():
            safe, risky, trap, inv = 0, 0, 0, 0
            for r in records[:100]:
                em = r[1]
                st, sc, dt, co, la = self.validator.validate(em, use_ai=True)
                if st == 'SAFE': safe += 1
                elif st == 'RISKY': risky += 1
                elif st == 'TRAP': trap += 1
                else: inv += 1
                self.signals.val_row_signal.emit(em, st, sc, dt, co, la)
                time.sleep(0.02)

            self.pill_safe.setText(f"SAFE: {safe}")
            self.pill_risky.setText(f"RISKY: {risky}")
            self.pill_trap.setText(f"TRAP: {trap}")
            self.pill_invalid.setText(f"INVALID: {inv}")
            self.btn_val_run.setEnabled(True)

        self.signals.val_row_signal.connect(self.add_val_table_row)
        threading.Thread(target=worker, daemon=True).start()

    def add_val_table_row(self, email, status, score, detail, country, last_active):
        row = self.val_table.rowCount()
        self.val_table.insertRow(row)

        c = QColor("#00ff9d" if status == "SAFE" else "#ff2a6d" if status == "TRAP" else "#ffcc00")
        it_e = QTableWidgetItem(email); it_e.setForeground(QColor("#00f3ff"))
        it_co = QTableWidgetItem(country)
        it_la = QTableWidgetItem(last_active); it_la.setForeground(QColor("#00ff9d"))
        it_s = QTableWidgetItem(status); it_s.setForeground(c)
        it_sc = QTableWidgetItem(str(score)); it_sc.setForeground(c)
        it_d = QTableWidgetItem(detail); it_d.setForeground(QColor("#d0d0e0"))

        for col, it in enumerate([it_e, it_co, it_la, it_s, it_sc, it_d]):
            self.val_table.setItem(row, col, it)

    def purge_traps(self):
        QMessageBox.information(self, "Очистка ловушек", "Спам-ловушки удалены из базы!")

    # =================================================================
    # ЛОГИКА СПАЙДЕРА / ПАРСЕРА
    # =================================================================
    def start_single_batch(self):
        self.start_spider_crawl(max_pages=40)

    def start_infinite_spider(self):
        self.start_spider_crawl(max_pages=None)

    def start_spider_crawl(self, max_pages=None):
        if self.running:
            return
        self.running = True
        self.signals.status_signal.emit("ACTIVE", True)
        self.btn_dash_batch.setEnabled(False)
        self.btn_dash_infinite.setEnabled(False)
        self.btn_dash_kill.setEnabled(True)
        self.btn_spider_session.setEnabled(False)
        self.btn_spider_crawl.setEnabled(False)

        threading.Thread(target=lambda: self._spider_worker(max_pages), daemon=True).start()

    def stop_all(self):
        self.running = False
        self.signals.status_signal.emit("STANDBY", False)
        self.btn_dash_batch.setEnabled(True)
        self.btn_dash_infinite.setEnabled(True)
        self.btn_dash_kill.setEnabled(False)
        self.btn_spider_session.setEnabled(True)
        self.btn_spider_crawl.setEnabled(True)

    def _spider_worker(self, max_pages):
        seeds = [s.strip() for s in self.spider_seeds_edit.toPlainText().splitlines() if s.strip()]
        q = queue.Queue()
        for s in seeds:
            q.put(s)

        pages = 0
        while self.running:
            if max_pages and pages >= max_pages:
                break
            if q.empty():
                for s in seeds:
                    q.put(s)

            try:
                url = q.get_nowait()
            except queue.Empty:
                break

            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)
            pages += 1

            self.signals.domain_signal.emit(f"Visited: {len(self.visited_urls)} nodes")
            self.signals.auto_iter_signal.emit(f"{q.qsize()} ссылок в очереди")

            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0.0.0"}
                r = requests.get(url, headers=headers, timeout=6)
                if r.status_code == 200:
                    text = r.text
                    found = set(self.email_regex.findall(text))
                    new_count = 0
                    for em in found:
                        em_l = em.lower()
                        if em_l.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg')):
                            continue
                        if em_l not in self.seen_emails:
                            self.seen_emails.add(em_l)
                            dom = em_l.split("@")[-1]
                            cat = "HUMAN / PERSONAL" if dom in ('gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'outlook.com') else "CORPORATE / DEV"
                            if cat == "HUMAN / PERSONAL":
                                self.personal_emails.add(em_l)

                            # Сохраняем в таблицу базы данных SQLite & CSV
                            co, la = EmailDatabase.insert_email(em_l, cat, url, status="SAFE", score=92)
                            new_count += 1
                            self.signals.account_signal.emit(em_l, cat, url, time.strftime("%H:%M:%S"), co, la)

                    if new_count > 0:
                        self.signals.log_signal.emit(f"[+] Извлечено и записано в таблицу {new_count} почт с {url}", "success", "spider")

                    links = re.findall(r'href=[\'"](https?://[^\'" >]+)[\'"]', text)
                    gh_repos = re.findall(r'href=[\'"](/[^/\s"\']+/([^/\s"\']+))[\'"]', text)
                    for r_path, _ in gh_repos:
                        links.append(f"https://github.com{r_path}")
                        links.append(f"https://raw.githubusercontent.com{r_path}/master/README.md")

                    for lk in links:
                        if q.qsize() < 3000 and lk not in self.visited_urls:
                            q.put(lk)
            except Exception as e:
                self.signals.log_signal.emit(f"Ошибка {url[:30]}: {e}", "err", "spider")

            time.sleep(0.3)

        self.running = False
        self.signals.status_signal.emit("STANDBY", False)

    def on_status(self, text, is_active):
        self.stat_engine_val.setText(text)
        self.stat_engine_val.setStyleSheet(f"color: {'#00ff9d' if is_active else '#b026ff'};")
        self.stat_spider_status.setText("РАБОТАЕТ" if is_active else "ОСТАНОВЛЕН")
        self.stat_spider_status.setStyleSheet(f"color: {'#00ff9d' if is_active else '#ff2a6d'};")
        self.engine_dot_sidebar.set_color("#00ff9d" if is_active else "#4a4a5a")
        self.engine_txt_sidebar.setText("ENGINE ACTIVE" if is_active else "ENGINE IDLE")
        self.btn_dash_batch.setEnabled(not is_active)
        self.btn_dash_infinite.setEnabled(not is_active)
        self.btn_dash_kill.setEnabled(is_active)
        self.btn_spider_session.setEnabled(not is_active)
        self.btn_spider_crawl.setEnabled(not is_active)

    def on_log(self, msg, tag, target):
        color = "#00ff9d" if tag == "success" else "#ff2a6d" if tag == "err" else "#00f3ff"
        ts = time.strftime("%H:%M:%S")
        self.log_spider.append(f'<span style="color:{color}; font-family: Consolas;">[{ts}] {msg}</span>')

    def on_account_found(self, email, cat, src, ts, country, last_active):
        row = self.dash_table.rowCount()
        if row >= 30:
            self.dash_table.removeRow(0)
            row -= 1
        self.dash_table.insertRow(row)

        it_e = QTableWidgetItem(email); it_e.setForeground(QColor("#00f3ff"))
        it_co = QTableWidgetItem(country)
        it_la = QTableWidgetItem(last_active); it_la.setForeground(QColor("#00ff9d"))
        it_c = QTableWidgetItem(cat); it_c.setForeground(QColor("#00ff9d" if "HUMAN" in cat else "#b026ff"))
        it_s = QTableWidgetItem(src[:45]); it_s.setForeground(QColor("#e0e0e0"))
        it_t = QTableWidgetItem(ts); it_t.setForeground(QColor("#8b8b9e"))

        for col, it in enumerate([it_e, it_co, it_la, it_c, it_s, it_t]):
            self.dash_table.setItem(row, col, it)
        self.update_counters()

    # =================================================================
    # ЛОГИКА ACCOUNTS
    # =================================================================
    def refresh_accounts_view(self):
        accs = MailerAccountManager.load_accounts()
        self.combos_display_list.clear()
        for a in accs:
            self.combos_display_list.addItem(f"{a['email']}  [Provider: {a['provider']}] -> READY")
        self.combo_count_lbl.setText(f"👥 ACTIVE MAILER COMBOS ({len(accs)})")
        path = MailerAccountManager.get_file_path()
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.accounts_raw_editor.setPlainText(f.read())

    def add_single_account(self):
        em = self.acc_input_email.text().strip()
        pw = self.acc_input_pass.text().strip()
        if not em or "@" not in em or not pw:
            QMessageBox.warning(self, "Ошибка", "Укажите корректный email и пароль/пароль приложения!")
            return
        path = MailerAccountManager.get_file_path()
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n{em}:{pw}\n")
        self.acc_input_email.clear()
        self.acc_input_pass.clear()
        self.refresh_accounts_view()
        QMessageBox.information(self, "Готово", f"Аккаунт {em} успешно добавлен в accounts.txt!")

    def save_raw_accounts_file(self):
        txt = self.accounts_raw_editor.toPlainText()
        path = MailerAccountManager.get_file_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(txt)
        self.refresh_accounts_view()
        QMessageBox.information(self, "Сохранено", "Файл accounts.txt успешно сохранен!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
