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


# =====================================================================
# СИГНАЛЫ ВЗАИМОДЕЙСТВИЯ С GUI
# =====================================================================
class ParserSignals(QObject):
    log_signal = pyqtSignal(str, str, str)          # msg, tag, target_tab
    account_signal = pyqtSignal(str, str, str, str) # email, category, target_source, timestamp
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str, bool)
    domain_signal = pyqtSignal(str)
    auto_iter_signal = pyqtSignal(str)
    # --- Валидатор ---
    val_row_signal = pyqtSignal(str, str, int, str)
    val_done_signal = pyqtSignal()
    val_progress_signal = pyqtSignal(int, int)
    # --- Мейлер ---
    mail_log_signal = pyqtSignal(str, str)
    mail_sent_signal = pyqtSignal(str, str)
    mail_status_signal = pyqtSignal(str, str)
    # --- Lo-Fi Радио ---
    radio_status_signal = pyqtSignal(str, bool)


# =====================================================================
# СТИЛИ (CYBERPUNK NEON GLOW - ЧЕТКО ПО СКРИНШОТАМ MORPHH)
# =====================================================================
QSS = """
QMainWindow { background-color: #050508; }

/* Сайдбар */
QWidget#sidebar {
    background-color: #0b0713;
    border-right: 1px solid rgba(138, 43, 226, 0.22);
}

QPushButton#navBtn {
    font-family: "Segoe UI", sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: #838397;
    background-color: transparent;
    border: none;
    border-radius: 10px;
    padding: 10px 14px;
    text-align: left;
    min-height: 40px;
}
QPushButton#navBtn:hover {
    color: #e0e0f0;
    background-color: rgba(138, 43, 226, 0.12);
}
QPushButton#navBtn.active {
    color: #ffffff;
    background-color: rgba(138, 43, 226, 0.24);
    border: 1px solid #b026ff;
    font-weight: 600;
}

/* Карточки */
QWidget#card {
    background-color: #0e0918;
    border: 1px solid rgba(138, 43, 226, 0.22);
    border-radius: 14px;
}
QWidget#cardInner {
    background-color: #08060d;
    border: 1px solid rgba(138, 43, 226, 0.18);
    border-radius: 10px;
}

/* Кнопки действий */
QPushButton#actionBtn {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #ffffff;
    background-color: rgba(0, 243, 255, 0.08);
    border: 1px solid rgba(0, 243, 255, 0.4);
    border-radius: 10px;
    padding: 10px 20px;
    min-height: 38px;
}
QPushButton#actionBtn:hover {
    background-color: rgba(0, 243, 255, 0.18);
    border-color: #00f3ff;
}
QPushButton#greenBtn {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #00ff9d;
    background-color: rgba(0, 255, 157, 0.08);
    border: 1px solid rgba(0, 255, 157, 0.4);
    border-radius: 10px;
    padding: 10px 20px;
    min-height: 38px;
}
QPushButton#greenBtn:hover {
    background-color: rgba(0, 255, 157, 0.18);
    border-color: #00ff9d;
}
QPushButton#stopBtn {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #ff2a6d;
    background-color: rgba(255, 42, 109, 0.08);
    border: 1px solid rgba(255, 42, 109, 0.4);
    border-radius: 10px;
    padding: 10px 20px;
    min-height: 38px;
}
QPushButton#stopBtn:hover {
    background-color: rgba(255, 42, 109, 0.2);
    border-color: #ff2a6d;
}

QPushButton#aiPillBtn {
    font-family: "Segoe UI", sans-serif;
    font-size: 11px;
    font-weight: 700;
    color: #ffffff;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #00f3ff);
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
}
QPushButton#aiPillBtn:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #b026ff, stop:1 #00ff9d);
}

/* Поля ввода */
QLineEdit, QPlainTextEdit {
    font-family: "Consolas", monospace;
    font-size: 12px;
    color: #00ff9d;
    background-color: #06040a;
    border: 1px solid rgba(138, 43, 226, 0.3);
    border-radius: 8px;
    padding: 8px 12px;
}
QLineEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #00f3ff;
}

QComboBox {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: #e0e0e0;
    background-color: #0e0918;
    border: 1px solid rgba(138, 43, 226, 0.4);
    border-radius: 8px;
    padding: 7px 12px;
}
QComboBox:hover {
    border-color: #00f3ff;
}
QComboBox QAbstractItemView {
    background-color: #0b0713;
    color: #e0e0e0;
    border: 1px solid #b026ff;
    selection-background-color: rgba(138, 43, 226, 0.5);
    outline: none;
}

/* Таблицы */
QTableWidget {
    background-color: #06040a;
    border: 1px solid rgba(138, 43, 226, 0.2);
    border-radius: 10px;
    gridline-color: rgba(255, 255, 255, 0.03);
    font-family: "Consolas", monospace;
    font-size: 11px;
    color: #d0d0e0;
    selection-background-color: rgba(138, 43, 226, 0.35);
}
QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}
QHeaderView::section {
    background-color: #0b0713;
    color: #8b8b9e;
    padding: 10px;
    border: none;
    border-bottom: 1px solid rgba(138, 43, 226, 0.3);
    font-family: "Segoe UI", sans-serif;
    font-weight: 700;
    font-size: 10px;
    letter-spacing: 1px;
}

/* Терминал */
QTextEdit {
    font-family: "Consolas", monospace;
    font-size: 11px;
    color: #00ff9d;
    background-color: #06040a;
    border: 1px solid rgba(138, 43, 226, 0.2);
    border-radius: 10px;
    padding: 12px;
}

/* Слайдер громкости */
QSlider::groove:horizontal {
    border: 1px solid rgba(138, 43, 226, 0.3);
    height: 6px;
    background: #06040a;
    border-radius: 3px;
}
QSlider::sub-page:horizontal {
    background: #00f3ff;
    border-radius: 3px;
}
QSlider::handle:horizontal {
    background: #ffffff;
    border: 1px solid #b026ff;
    width: 14px;
    margin-top: -4px;
    margin-bottom: -4px;
    border-radius: 7px;
}
"""

ACCENT_CYAN = "#00f3ff"
ACCENT_PURPLE = "#b026ff"
ACCENT_GREEN = "#00ff9d"
ACCENT_RED = "#ff2a6d"


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
# ФОН С НЕОНОВОЙ СЕТКОЙ И ЧАСТИЦАМИ
# =====================================================================
class OrbBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.particles = [
            {"x": random.uniform(0, 1920), "y": random.uniform(0, 1080),
             "vx": random.uniform(-0.15, 0.15), "vy": random.uniform(-0.15, 0.15),
             "a": random.randint(20, 60)}
            for _ in range(30)
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(80)

    def animate(self):
        w, h = max(self.width(), 100), max(self.height(), 100)
        for p in self.particles:
            p["x"] = (p["x"] + p["vx"]) % w
            p["y"] = (p["y"] + p["vy"]) % h
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(5, 5, 8))

        # Тонкая сетка
        painter.setPen(QPen(QColor(138, 43, 226, 8)))
        step = 90
        for gx in range(0, self.width(), step):
            painter.drawLine(gx, 0, gx, self.height())
        for gy in range(0, self.height(), step):
            painter.drawLine(0, gy, self.width(), gy)

        # Частицы
        for p in self.particles:
            painter.setPen(QColor(0, 243, 255, p["a"]))
            painter.drawPoint(int(p["x"]), int(p["y"]))
        painter.end()


# =====================================================================
# МОЩНЫЙ ИИ-ДВИЖОК ДЛЯ ВАЛИДАТОРА И МЕЙЛЕРА
# =====================================================================
class AIEngine:
    """Интеграция с Google Gemini API + продвинутый автономный анализатор.
    Реализует глубокий аудит спам-ловушек и генерацию конверсионных писем."""

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
    def generate_email(cls, goal: str, recipient: str = "", sender: str = "") -> dict:
        prompt = (
            f"Ты эксперт по B2B/B2C outreach и деловой переписке без спама. "
            f"Цель сообщения: '{goal}'. "
            f"Получатель: {recipient or 'коллега/разработчик'}. "
            f"Отправитель: {sender or 'я'}. "
            f"Создай естественное, уважительное, живое письмо, не содержащее спам-триггеров "
            f"(слов 'скидка', '$$$', 'бесплатно', избытка знаков препинания и навязчивости). "
            f"Ответь СТРОГО в формате JSON:\n"
            f'{{"subject": "Краткая тема", "body": "Текст письма"}}'
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

        # Автономный генератор при отсутствии API-ключа
        subj = f"Cooperation & Tech Discussion"
        body = (
            f"Hello,\n\n"
            f"I came across your open-source projects and developer contributions. "
            f"Regarding {goal}:\n\n"
            f"Would you be open to a brief exchange or sync this week? "
            f"Looking forward to hearing from you.\n\n"
            f"Best regards,\n{sender or 'Developer'}"
        )
        return {"subject": subj, "body": body}

    @classmethod
    def evaluate_spam_trap(cls, email: str) -> dict:
        prompt = (
            f"Analyze this email address for SPAM TRAP, HONEYPOT, or FAKE BOT characteristics:\n"
            f"Email: {email}\n"
            f"Determine if this is a genuine individual person, or a spam trap / honeypot / bounce address.\n"
            f"Return strictly JSON:\n"
            f'{{"is_trap": false, "is_human": true, "confidence": 95, "reason": "concise explanation"}}'
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
# ВАЛИДАТОР ПОЧТ: СПАМ-ЛОВУШКИ + MX + DISPOSABLE
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
    JUNK_DOMAINS = {
        'example.com', 'example.org', 'example.net', 'domain.com', 'email.com',
        'test.com', 'sentry.io', 'schema.org', 'wixpress.com', 'localhost'
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
        """Возвращает (status, score 0..100, detail).
        Статусы: SAFE, RISKY, TRAP, INVALID."""
        email = email.strip().lower()
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,63}$", email):
            return ('INVALID', 0, 'Битый синтаксис email')

        local, domain = email.rsplit('@', 1)
        if domain in self.JUNK_DOMAINS:
            return ('INVALID', 0, 'Тестовый домен (example/dummy)')
        if domain in self.DISPOSABLE_DOMAINS:
            return ('INVALID', 10, 'Одноразовый временный сервис')

        # Токены спам-ловушек
        parts = re.split(r'[._+\-]', local)
        if any(p in self.TRAP_TOKENS for p in parts) or any(t in local for t in ('honeypot', 'spamtrap', 'blackhole')):
            return ('TRAP', 0, '⚠️ ОБНАРУЖЕНА СПАМ-ЛОВУШКА (Honeypot Trap)')

        # Проверка MX
        mxs = self.get_mx(domain)
        if not mxs:
            return ('INVALID', 0, 'MX сервер не принимает входящую почту')

        # Служебные ящики
        if parts[0] in self.ROLE_PREFIXES:
            return ('RISKY', 60, f'Служебный ящик ({parts[0]}@), а не личный')

        # ИИ-анализ через Gemini
        if use_ai and AIEngine.get_api_key():
            ai_verdict = AIEngine.evaluate_spam_trap(email)
            if ai_verdict:
                if ai_verdict.get("is_trap"):
                    return ('TRAP', 5, f"ИИ: спам-ловушка ({ai_verdict.get('reason', '')})")
                if ai_verdict.get("is_human"):
                    return ('SAFE', 95, f"ИИ: подтвержден человек ({ai_verdict.get('reason', '')})")

        # Личные провайдеры
        personal_providers = ('gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'outlook.com', 'icloud.com', 'proton.me')
        if domain in personal_providers:
            return ('SAFE', 92, 'Настоящий личный ящик человека')

        return ('SAFE', 85, 'Живой домен, синтаксис чист')


# =====================================================================
# МЕНЕДЖЕР АККАУНТОВ (accounts.txt / mailer.txt)
# =====================================================================
class MailerAccountManager:
    @staticmethod
    def get_file_path():
        # Поддерживаем и accounts.txt (как на скриншоте), и mailer.txt
        p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accounts.txt")
        return p

    @classmethod
    def ensure_file_exists(cls):
        path = cls.get_file_path()
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write("# File for sender accounts in format: email:password\n")
                    f.write("# Add your accounts below, one per line.\n")
                    f.write("# Example:\n")
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

    @classmethod
    def save_raw(cls, content: str):
        path = cls.get_file_path()
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)


# =====================================================================
# НАСТОЯЩИЙ РАБОЧИЙ SMTP ОТПРАВИТЕЛЬ С ПОЛНЫМ RFC5322
# =====================================================================
class SmtpSender:
    """Проверенный рабочий SMTP-транспорт с авто-определением серверов,
    STARTTLS/SSL, генерацией RFC5322 заголовков, Message-ID и защитой от спама."""

    PROVIDERS = {
        'gmail.com': ('smtp.gmail.com', 587, 'starttls'),
        'googlemail.com': ('smtp.gmail.com', 587, 'starttls'),
        'yandex.ru': ('smtp.yandex.ru', 465, 'ssl'),
        'yandex.com': ('smtp.yandex.ru', 465, 'ssl'),
        'ya.ru': ('smtp.yandex.ru', 465, 'ssl'),
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
                f"Ошибка пароля для {self.email_addr}. Внимание: для Gmail и Yandex ОБЯЗАТЕЛЕН 'Пароль приложения' (App Password)."
            )
        except Exception as e:
            raise RuntimeError(f"Сбой соединения с сервером {host}: {e}")

    def send(self, to_email: str, subject: str, body: str):
        if not self.smtp:
            self.connect()

        # Полноценное RFC5322 MIME-сообщение
        msg = MIMEMultipart("alternative")
        sender_domain = self.email_addr.rsplit('@', 1)[-1]
        msg["From"] = formataddr(("", self.email_addr))
        msg["To"] = formataddr(("", to_email))
        msg["Subject"] = subject
        msg["Date"] = _dt.datetime.now(_dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")
        msg["Message-ID"] = make_msgid(domain=sender_domain)
        msg["X-Mailer"] = "MorphhOSINT/1.4"

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
# LO-FI РАДИО С 8 КУЛЬТОВЫМИ СТАНЦИЯМИ
# =====================================================================
class LoFiRadio(QObject):
    STATIONS = [
        {"name": "Lofi Chillhop & Study Beats", "genre": "CHILLHOP", "desc": "Relaxing hip-hop beats, mellow rhodes keys, and dusty vinyl groove", "url": "https://stream.zeno.fm/f3wvbbqmdg8uv"},
        {"name": "Nightwave Plaza & Vaporwave", "genre": "VAPORWAVE", "desc": "Nostalgic 80s aesthetics, synthwave pads, and late-night cyberpunk echoes", "url": "https://radio.plaza.one/mp3"},
        {"name": "DEF CON Radio (Cyber Chill)", "genre": "CYBERPUNK", "desc": "Hacker conference downtempo soundscapes and dark ambient synths", "url": "https://ice2.somafm.com/defcon-128-mp3"},
        {"name": "Groove Salad (SomaFM)", "genre": "DOWNTEMPO", "desc": "A nicely chilled plate of ambient downtempo beats and grooves", "url": "https://ice1.somafm.com/groovesalad-128-mp3"},
        {"name": "Secret Agent (Cinematic)", "genre": "SPY CHILL", "desc": "The soundtrack for your stylish, mysterious secret agent missions", "url": "https://ice1.somafm.com/secretagent-128-mp3"},
        {"name": "Drone Zone (Deep Space)", "genre": "AMBIENT", "desc": "Served best chilled, safe with most medications. Atmospheric textures", "url": "https://ice1.somafm.com/dronezone-128-mp3"},
        {"name": "Lush (Dreamy Vocal)", "genre": "DREAMPOP", "desc": "Sensuous and mellow vocal chillout, mostly female voices", "url": "https://ice1.somafm.com/lush-128-mp3"},
        {"name": "Vaporwaves (Synth Future)", "genre": "RETROWAVE", "desc": "All vaporwave, chillwave and future funk all the time", "url": "https://ice2.somafm.com/vaporwaves-128-mp3"}
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
            self.current_idx = idx
        st = self.STATIONS[self.current_idx]
        if self.player:
            try:
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
# ГЛАВНОЕ ОКНО MORPHH OSINT & MAILER V1.4
# =====================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MORPHH // ALLPARSV1.4 // AI OSINT")
        self.resize(1380, 880)

        self.running = False
        self.signals = ParserSignals()
        self.validator = EmailValidator()
        self.radio = LoFiRadio(self.signals)

        self.seen_emails = set()
        self.personal_emails = set()
        self.visited_urls = set()

        self.email_regex = re.compile(
            r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?'
            r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,63}',
            re.IGNORECASE
        )

        # Фон
        self.bg = OrbBackground(self)
        self.bg.setGeometry(0, 0, 1920, 1080)

        # Центральный виджет
        main_widget = QWidget(self)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Стек экранов и все страницы создаются ДО сайдбара
        self.content = QStackedWidget()
        self.page_dash = self.create_dashboard_page()
        self.page_spider = self.create_spider_page()
        self.page_validator = self.create_validator_page()
        self.page_mailer = self.create_mailer_page()
        self.page_accounts = self.create_accounts_page()
        self.page_radio = self.create_radio_page()
        self.page_base = self.create_base_page()
        self.page_python = self.create_python_page()

        self.content.addWidget(self.page_dash)      # 0
        self.content.addWidget(self.page_spider)    # 1
        self.content.addWidget(self.page_validator) # 2
        self.content.addWidget(self.page_mailer)    # 3
        self.content.addWidget(self.page_accounts)  # 4
        self.content.addWidget(self.page_radio)     # 5
        self.content.addWidget(self.page_base)      # 6
        self.content.addWidget(self.page_python)    # 7

        # Сайдбар (добавляется первым слева, и теперь безопасно вызывает switch_page)
        self.create_sidebar(main_layout)

        # Добавляем стек экранов справа
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg.setGeometry(0, 0, self.width(), self.height())

    def get_base_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPochtRassilka.txt")

    def load_initial_base(self):
        p = self.get_base_path()
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        e = line.strip().lower()
                        if "@" in e:
                            self.seen_emails.add(e)
                            dom = e.split("@")[-1]
                            if dom in ('gmail.com', 'yandex.ru', 'mail.ru', 'yahoo.com', 'outlook.com', 'icloud.com'):
                                self.personal_emails.add(e)
            except Exception:
                pass
        self.update_counters()

    def update_counters(self):
        self.stat_harvested_val.setText(str(len(self.seen_emails)))
        self.stat_personal_val.setText(str(len(self.personal_emails)))
        if hasattr(self, 'val_db_count_lbl'):
            self.val_db_count_lbl.setText(f"FULL DATABASE VALIDATION ({len(self.seen_emails)} EMAILS HARVESTED)")

    # =================================================================
    # САЙДБАР (ТОЧНО ПО СКРИНШОТАМ)
    # =================================================================
    def create_sidebar(self, parent_layout):
        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setFixedWidth(220)
        sl = QVBoxLayout(self.sidebar)
        sl.setContentsMargins(14, 24, 14, 20)
        sl.setSpacing(6)

        # Логотип MORPHH
        sl.addWidget(AnimatedLogo("MORPHH"))
        sub_logo = QLabel("ALLPARSV1.4 // AI OSINT")
        sub_logo.setStyleSheet("color: #6a6a80; font-size: 10px; font-family: 'Consolas'; letter-spacing: 1px;")
        sub_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(sub_logo)
        sl.addSpacing(14)

        self.nav_btns = {}
        items = [
            ("dash", "⊞  Dashboard", ""),
            ("spider", ">_ Spider & Dorks", "SPIDER"),
            ("validator", "✔  AI Validator", "GEMINI"),
            ("mailer", "✉  AI Mailer", "SMART"),
            ("accounts", "👥 Combo Accounts", ""),
            ("radio", "🎧 Lo-Fi Radio", ""),
            ("base", "📊 Database & Base", ""),
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
                bg_col = "#00f3ff" if badge == "GEMINI" else "#b026ff"
                b_lbl.setStyleSheet(f"background-color: rgba(138,43,226,0.3); color: {bg_col}; border: 1px solid {bg_col}; border-radius: 4px; font-size: 9px; font-weight: bold; padding: 2px 4px;")
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

        footer_lbl = QLabel("AI STUDIO FULL-STACK v2.0")
        footer_lbl.setStyleSheet("color: #4a4a5a; font-size: 9px; font-family: Consolas; margin-top: 6px;")
        footer_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sl.addWidget(footer_lbl)

        parent_layout.addWidget(self.sidebar)
        self.switch_page("dash")

    def switch_page(self, key):
        pages = {
            "dash": 0, "spider": 1, "validator": 2, "mailer": 3,
            "accounts": 4, "radio": 5, "base": 6, "python": 7
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
            self.refresh_base_view()

    # =================================================================
    # 1. SCREEN: DASHBOARD
    # =================================================================
    def create_dashboard_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(18)

        # Header
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

        # 4 Карточки метрик (точно как на скрине)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(14)

        # Card 1: Harvested Mails
        c1 = QWidget(); c1.setObjectName("card")
        c1_l = QVBoxLayout(c1); c1_l.setContentsMargins(18, 16, 18, 16)
        c1_l.addWidget(QLabel("HARVESTED MAILS", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.stat_harvested_val = QLabel("0")
        self.stat_harvested_val.setFont(QFont("Segoe UI", 32, QFont.Weight.Bold))
        self.stat_harvested_val.setStyleSheet("color: #00f3ff;")
        c1_l.addWidget(self.stat_harvested_val)
        c1_sub = QLabel("TXT Database: active   100% deduplicated")
        c1_sub.setStyleSheet("color: #00ff9d; font-size: 11px;")
        c1_l.addWidget(c1_sub)
        stats_row.addWidget(c1)

        # Card 2: Personal (Human)
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

        # Card 3: Crawler Engine
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

        # Card 4: Queue & Spider
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

        # Mission Control Deck
        ctrl_card = QWidget(); ctrl_card.setObjectName("card")
        cl = QVBoxLayout(ctrl_card); cl.setContentsMargins(20, 18, 20, 18); cl.setSpacing(14)
        c_top = QHBoxLayout()
        c_title = QLabel("● Mission Control Deck")
        c_title.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 13px;")
        c_top.addWidget(c_title)
        c_top.addStretch()
        c_safe = QLabel("🛡 Anti-Crash Sandboxed Engine")
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

        btn_clear = QPushButton("🗑  CLEAR HARVEST CACHE")
        btn_clear.setObjectName("actionBtn")
        btn_clear.clicked.connect(self.clear_cache)
        btn_row.addWidget(btn_clear)
        cl.addLayout(btn_row)

        l.addWidget(ctrl_card)

        # Live Feed Table
        feed_header = QHBoxLayout()
        lbl_feed = QLabel("● Live Harvested Contacts (Real-Time Feed)")
        lbl_feed.setStyleSheet("color: #00ff9d; font-size: 12px; font-weight: bold;")
        feed_header.addWidget(lbl_feed)
        feed_header.addStretch()
        feed_count = QLabel("Displaying latest entries")
        feed_count.setStyleSheet("color: #6a6a80; font-size: 11px;")
        feed_header.addWidget(feed_count)
        l.addLayout(feed_header)

        self.dash_table = QTableWidget(0, 4)
        self.dash_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "CATEGORY", "TARGET SOURCE", "TIMESTAMP"])
        self.dash_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.dash_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.dash_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.dash_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
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
        sub = QLabel("Рекурсивный паук обхода ссылок со встроенным автоматическим Dork-поиском (Google, DuckDuckGo, Bing, Yandex)")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        badge = QLabel("✨ Dorks + Spider Unified")
        badge.setStyleSheet("background: rgba(0, 243, 255, 0.1); color: #00f3ff; border: 1px solid #00f3ff; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        split = QHBoxLayout()
        split.setSpacing(16)

        # Левая колонка: НАЧАЛЬНЫЕ ССЫЛКИ / РЕПОЗИТОРИИ
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

        # Правая колонка: СОСТОЯНИЕ ДВИЖКА ПАУКА
        right_c = QWidget(); right_c.setObjectName("card")
        rcl = QVBoxLayout(right_c); rcl.setContentsMargins(18, 16, 18, 16); rcl.setSpacing(12)
        head_r = QLabel("● СОСТОЯНИЕ ДВИЖКА ПАУКА")
        head_r.setStyleSheet("color: #b026ff; font-weight: bold; font-size: 11px;")
        rcl.addWidget(head_r)

        grid_state = QVBoxLayout(); grid_state.setSpacing(6)
        r1 = QHBoxLayout(); r1.addWidget(QLabel("Статус:")); self.stat_spider_status = QLabel("ОСТАНОВЛЕН"); self.stat_spider_status.setStyleSheet("color: #ff2a6d; font-weight: bold;"); r1.addStretch(); r1.addWidget(self.stat_spider_status)
        r2 = QHBoxLayout(); r2.addWidget(QLabel("Очередь ссылок:")); self.stat_spider_queue = QLabel("0 ссылок"); self.stat_spider_queue.setStyleSheet("color: #00f3ff; font-weight: bold;"); r2.addStretch(); r2.addWidget(self.stat_spider_queue)
        r3 = QHBoxLayout(); r3.addWidget(QLabel("Посещено страниц:")); self.stat_spider_visited = QLabel("0"); self.stat_spider_visited.setStyleSheet("color: #e0e0e0; font-weight: bold;"); r3.addStretch(); r3.addWidget(self.stat_spider_visited)
        r4 = QHBoxLayout(); r4.addWidget(QLabel("Извлечено почт:")); self.stat_spider_harvested = QLabel("+0"); self.stat_spider_harvested.setStyleSheet("color: #00ff9d; font-weight: bold;"); r4.addStretch(); r4.addWidget(self.stat_spider_harvested)
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

        # Терминал
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
        self.log_spider.setMaximumHeight(200)
        tcl.addWidget(self.log_spider)
        l.addWidget(term_c)

        return page

    # =================================================================
    # 3. SCREEN: GEMINI AI EMAIL VALIDATOR
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
        sub = QLabel("Honeypot detection, MX verification, throwaway domain quarantine, and AI reputation heuristics")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        badge = QLabel("✨ Powered by Gemini")
        badge.setStyleSheet("background: rgba(0, 243, 255, 0.1); color: #00f3ff; border: 1px solid #00f3ff; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(badge, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        # Card 1: Interactive AI Single Email Inspection
        c1 = QWidget(); c1.setObjectName("card")
        c1_l = QVBoxLayout(c1); c1_l.setContentsMargins(20, 16, 20, 16); c1_l.setSpacing(10)
        lbl_c1 = QLabel("🔍 INTERACTIVE AI SINGLE EMAIL INSPECTION")
        lbl_c1.setStyleSheet("color: #00f3ff; font-weight: bold; font-size: 11px;")
        c1_l.addWidget(lbl_c1)

        row_insp = QHBoxLayout()
        self.val_single_edit = QLineEdit()
        self.val_single_edit.setPlaceholderText("e.g. spam-trap_99@honeypot.org or developer@gmail.com")
        self.val_single_edit.returnPressed.connect(self.inspect_single_email)
        row_insp.addWidget(self.val_single_edit, 1)

        btn_inspect = QPushButton("✨  INSPECT WITH AI")
        btn_inspect.setObjectName("aiPillBtn")
        btn_inspect.clicked.connect(self.inspect_single_email)
        row_insp.addWidget(btn_inspect)
        c1_l.addLayout(row_insp)
        l.addWidget(c1)

        # Card 2: Full Database Validation
        c2 = QWidget(); c2.setObjectName("card")
        c2_l = QVBoxLayout(c2); c2_l.setContentsMargins(20, 16, 20, 16); c2_l.setSpacing(12)
        top_c2 = QHBoxLayout()
        self.val_db_count_lbl = QLabel("● FULL DATABASE VALIDATION (0 EMAILS HARVESTED)")
        self.val_db_count_lbl.setStyleSheet("color: #b026ff; font-weight: bold; font-size: 11px;")
        top_c2.addWidget(self.val_db_count_lbl)
        top_c2.addStretch()

        self.btn_val_run = QPushButton("✔  VALIDATE BASE NOW")
        self.btn_val_run.setObjectName("greenBtn")
        self.btn_val_run.clicked.connect(self.run_full_validation)
        top_c2.addWidget(self.btn_val_run)

        self.btn_val_purge = QPushButton("🗑  PURGE TRAPS & INVALIDS (0)")
        self.btn_val_purge.setObjectName("stopBtn")
        self.btn_val_purge.clicked.connect(self.purge_traps)
        top_c2.addWidget(self.btn_val_purge)
        c2_l.addLayout(top_c2)

        # Статистика валидации (4 цветных плашки как на скрине)
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

        # Card 3: Результаты в таблице
        self.val_table = QTableWidget(0, 4)
        self.val_table.setHorizontalHeaderLabels(["EMAIL ADDRESS", "VERDICT", "SCORE", "AI / HEURISTIC DETAIL"])
        self.val_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.val_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.val_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.val_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        l.addWidget(self.val_table, 1)

        return page

    # =================================================================
    # 4. SCREEN: AI MAILER & DELIVERY STUDIO
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
        sub = QLabel("Multi-account combo dispatch with Gemini AI drafting, spam shield evaluation, and RFC5322 compliance")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        pill_shield = QLabel("🛡 Anti-Spam Pre-Flight Armed")
        pill_shield.setStyleSheet("background: rgba(0, 255, 157, 0.1); color: #00ff9d; border: 1px solid #00ff9d; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(pill_shield, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        # Две колонки
        cols = QHBoxLayout(); cols.setSpacing(16)

        # Левая колонка: SENDER ACCOUNT + VERIFIED DATABASE RECIPIENTS
        left_m = QVBoxLayout(); left_m.setSpacing(14)

        # Sender card
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

        # Recipients Card
        rec_card = QWidget(); rec_card.setObjectName("card")
        rcl = QVBoxLayout(rec_card); rcl.setContentsMargins(18, 16, 18, 16); rcl.setSpacing(8)
        r_head = QHBoxLayout()
        r_head.addWidget(QLabel("✔ VERIFIED DATABASE RECIPIENTS", styleSheet="color: #00ff9d; font-weight: bold; font-size: 11px;"))
        r_head.addStretch()
        self.recip_count_lbl = QLabel("0 in base")
        self.recip_count_lbl.setStyleSheet("color: #6a6a80; font-size: 11px;")
        r_head.addWidget(self.recip_count_lbl)
        rcl.addLayout(r_head)

        self.recip_list = QListWidget()
        self.recip_list.setStyleSheet("background: #06040a; border: 1px solid rgba(138,43,226,0.2); border-radius: 8px; color: #00ff9d; font-family: Consolas; font-size: 11px;")
        self.recip_list.itemClicked.connect(lambda it: self.mail_to_edit.setText(it.text()))
        rcl.addWidget(self.recip_list, 1)
        left_m.addWidget(rec_card, 1)

        cols.addLayout(left_m, 2)

        # Правая колонка: ФОРМА ПИСЬМА + КНОПКА ВОСПОЛЬЗОВАТЬСЯ ИИ
        right_m = QWidget(); right_m.setObjectName("card")
        rml = QVBoxLayout(right_m); rml.setContentsMargins(20, 18, 20, 18); rml.setSpacing(12)

        rml.addWidget(QLabel("RECIPIENT EMAIL (TO:)", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.mail_to_edit = QLineEdit()
        self.mail_to_edit.setPlaceholderText("contact@targetdomain.com")
        rml.addWidget(self.mail_to_edit)

        rml.addWidget(QLabel("EMAIL SUBJECT LINE", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        self.mail_subj_edit = QLineEdit()
        self.mail_subj_edit.setPlaceholderText("Cooperation & Tech Collaboration Proposal")
        rml.addWidget(self.mail_subj_edit)

        msg_head = QHBoxLayout()
        msg_head.addWidget(QLabel("MESSAGE CONTENT (MIME / PLAIN / HTML)", styleSheet="color: #8b8b9e; font-size: 10px; font-weight: bold; letter-spacing: 1px;"))
        msg_head.addStretch()

        self.btn_ai_compose = QPushButton("✨  ВОСПОЛЬЗОВАТЬСЯ ИИ")
        self.btn_ai_compose.setObjectName("aiPillBtn")
        self.btn_ai_compose.clicked.connect(self.open_ai_compose_dialog)
        msg_head.addWidget(self.btn_ai_compose)
        rml.addLayout(msg_head)

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
        anti_lbl = QLabel("ℹ Anti-Spam AI Check will audit the message before dispatch")
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
    # 5. SCREEN: SENDER ACCOUNTS MANAGER (accounts.txt)
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

        # Левая колонка
        left_box = QVBoxLayout(); left_box.setSpacing(14)

        # Add single account card
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

        # Active combos list
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

        # Правая колонка: DIRECT RAW EDITOR
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
    # 6. SCREEN: CYBERPUNK LO-FI RADIO
    # =================================================================
    def create_radio_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30)
        l.setSpacing(16)

        h_row = QHBoxLayout()
        title_box = QVBoxLayout()
        t = QLabel("((o)) Cyberpunk Lo-Fi Radio")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        title_box.addWidget(t)
        sub = QLabel("Live streaming lofi beats, ambient chillhop, and atmospheric textures for deep focus OSINT sessions")
        sub.setStyleSheet("color: #8b8b9e; font-size: 12px;")
        title_box.addWidget(sub)
        h_row.addLayout(title_box)

        self.radio_pill_status = QLabel("● RADIO OFF")
        self.radio_pill_status.setStyleSheet("background: rgba(255, 42, 109, 0.1); color: #ff2a6d; border: 1px solid #ff2a6d; border-radius: 12px; padding: 4px 12px; font-size: 11px; font-weight: bold;")
        h_row.addWidget(self.radio_pill_status, 0, Qt.AlignmentFlag.AlignTop)
        l.addLayout(h_row)
        l.addWidget(RainbowLine())

        # Main Player Box
        player_card = QWidget(); player_card.setObjectName("card")
        pcl = QVBoxLayout(player_card); pcl.setContentsMargins(24, 20, 24, 20); pcl.setSpacing(14)

        top_p = QHBoxLayout()
        self.player_title_lbl = QLabel("((o)) LOFI CHILLHOP & STUDY BEATS")
        self.player_title_lbl.setStyleSheet("color: #00f3ff; font-weight: bold; font-family: Consolas; font-size: 12px;")
        top_p.addWidget(self.player_title_lbl)
        top_p.addStretch()
        self.player_state_lbl = QLabel("STOPPED")
        self.player_state_lbl.setStyleSheet("color: #8b8b9e; font-family: Consolas; font-size: 11px;")
        top_p.addWidget(self.player_state_lbl)
        pcl.addLayout(top_p)

        # Аудио-визуализатор имитация
        vis = QLabel("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
        vis.setStyleSheet("color: #00f3ff; font-family: Consolas; font-size: 14px; background: #06040a; border: 1px solid rgba(138,43,226,0.3); border-radius: 8px; padding: 35px 20px;")
        vis.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pcl.addWidget(vis)

        # Контроллеры
        c_row = QHBoxLayout(); c_row.setSpacing(20)
        self.btn_radio_main = QPushButton("▶  TURN ON")
        self.btn_radio_main.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #00f3ff); color: #000000; font-weight: 800; font-size: 13px; border-radius: 12px; padding: 14px 28px;")
        self.btn_radio_main.clicked.connect(self.toggle_radio_main)
        c_row.addWidget(self.btn_radio_main)

        info_box = QVBoxLayout()
        info_t = QLabel("Click to start Lo-Fi stream")
        info_t.setStyleSheet("color: #ffffff; font-weight: bold; font-size: 12px;")
        info_box.addWidget(info_t)
        info_sub = QLabel("Music continues playing even when switching tabs")
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

        # Карточки кураторских станций
        cur_head = QLabel("🎧 CURATED LO-FI STATIONS & MOODS")
        cur_head.setStyleSheet("color: #00ff9d; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        l.addWidget(cur_head)

        stations_grid = QHBoxLayout(); stations_grid.setSpacing(14)
        for idx, st in enumerate(LoFiRadio.STATIONS[:2]):
            s_card = QWidget(); s_card.setObjectName("card")
            s_l = QVBoxLayout(s_card); s_l.setContentsMargins(18, 16, 18, 16); s_l.setSpacing(8)
            sh = QHBoxLayout()
            sh.addWidget(QLabel(f"🎵 {st['name']}", styleSheet="color: #ffffff; font-weight: bold; font-size: 13px;"))
            sh.addStretch()
            sh.addWidget(QLabel(st['genre'], styleSheet="color: #00f3ff; border: 1px solid #00f3ff; border-radius: 4px; padding: 2px 6px; font-size: 9px; font-weight: bold;"))
            s_l.addLayout(sh)

            s_l.addWidget(QLabel(st['desc'], styleSheet="color: #8b8b9e; font-size: 11px;"))
            s_btn = QPushButton("Select Station" if idx == 0 else "Click to select")
            s_btn.setObjectName("actionBtn")
            s_btn.clicked.connect(lambda ch, i=idx: self.select_station_action(i))
            s_l.addWidget(s_btn)
            stations_grid.addWidget(s_card)
        l.addLayout(stations_grid)

        return page

    # =================================================================
    # 7. SCREEN: DATABASE & BASE
    # =================================================================
    def create_base_page(self):
        page = QWidget()
        l = QVBoxLayout(page)
        l.setContentsMargins(35, 30, 35, 30); l.setSpacing(16)
        t = QLabel("📊 Database & Raw Base Viewer")
        t.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        t.setStyleSheet("color: #ffffff;")
        l.addWidget(t)
        l.addWidget(RainbowLine())

        card = QWidget(); card.setObjectName("card")
        cl = QVBoxLayout(card); cl.setContentsMargins(20, 18, 20, 18)
        self.base_raw_view = QTextEdit()
        self.base_raw_view.setReadOnly(True)
        cl.addWidget(self.base_raw_view)
        l.addWidget(card, 1)
        return page

    # =================================================================
    # 8. SCREEN: DESKTOP PYTHON FILE
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
    # ОБРАБОТЧИКИ И ЛОГИКА
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

    def refresh_mailer_dropdown(self):
        self.mailer_acc_combo.clear()
        accs = MailerAccountManager.load_accounts()
        for a in accs:
            self.mailer_acc_combo.addItem(f"{a['email']} ({a['provider']})", a)
        self.recip_list.clear()
        for em in sorted(list(self.seen_emails))[:30]:
            self.recip_list.addItem(em)
        self.recip_count_lbl.setText(f"{len(self.seen_emails)} in base")

    def on_mailer_account_change(self):
        data = self.mailer_acc_combo.currentData()
        if data:
            self.mailer_prov_lbl.setText(data.get("provider", "UNKNOWN"))

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

    def refresh_base_view(self):
        path = self.get_base_path()
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    self.base_raw_view.setPlainText(f.read())
            except Exception:
                pass

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
        MailerAccountManager.save_raw(txt)
        self.refresh_accounts_view()
        QMessageBox.information(self, "Сохранено", "Файл accounts.txt успешно обновлен!")

    def open_ai_compose_dialog(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("✨ Генерация текста письма через ИИ")
        dlg.setFixedSize(500, 320)
        dlg.setStyleSheet("background-color: #0b0713; color: #ffffff;")
        dl = QVBoxLayout(dlg); dl.setSpacing(12)
        dl.addWidget(QLabel("🎯 Опишите цель письма:", styleSheet="color: #00f3ff; font-weight: bold;"))
        prompt_in = QLineEdit()
        prompt_in.setPlaceholderText("Например: Предложить партнерство по совместному Open Source проекту")
        dl.addWidget(prompt_in)

        btn_run = QPushButton("✨ Сгенерировать тему и текст")
        btn_run.setObjectName("aiPillBtn")
        dl.addWidget(btn_run)

        st_lbl = QLabel("")
        dl.addWidget(st_lbl)

        def do_gen():
            val = prompt_in.text().strip()
            if not val:
                return
            st_lbl.setText("Генерация через ИИ...")
            QApplication.processEvents()
            res = AIEngine.generate_email(val, self.mail_to_edit.text(), "Outreach Team")
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
            QMessageBox.warning(self, "Ошибка", "Укажите адрес получателя!")
            return
        if not data:
            QMessageBox.warning(self, "Ошибка", "Нет выбранного аккаунта в accounts.txt!")
            return

        # Pre-Flight проверка получателя
        status, score, detail = self.validator.validate(to, use_ai=True)
        if status in ('TRAP', 'INVALID'):
            QMessageBox.critical(
                self, "ОТПРАВКА ЗАБЛОКИРОВАНА ПРЕ-ФЛАЙТ ФИЛЬТРОМ",
                f"Внимание! Адрес {to} является спам-ловушкой ({status})!\n{detail}\n\nОтправка отменена."
            )
            return

        self.btn_send_preflight.setEnabled(False)

        def worker():
            try:
                sender = SmtpSender(data["email"], data["password"])
                sender.send(to, subj, body)
                sender.close()
                self.signals.log_signal.emit(f"[SMTP OK] Письмо успешно отправлено на {to}", "success", "spider")
            except Exception as e:
                self.signals.log_signal.emit(f"[SMTP FAIL] {e}", "err", "spider")
            finally:
                self.btn_send_preflight.setEnabled(True)

        threading.Thread(target=worker, daemon=True).start()

    def inspect_single_email(self):
        em = self.val_single_edit.text().strip()
        if not em or "@" not in em:
            return
        status, score, detail = self.validator.validate(em, use_ai=True)
        self.add_val_table_row(em, status, score, detail)
        self.val_single_edit.clear()

    def run_full_validation(self):
        emails = list(self.seen_emails)
        if not emails:
            QMessageBox.information(self, "Инфо", "База пуста!")
            return
        self.val_table.setRowCount(0)
        self.btn_val_run.setEnabled(False)

        def worker():
            safe, risky, trap, inv = 0, 0, 0, 0
            for em in emails[:100]:
                st, sc, dt = self.validator.validate(em, use_ai=True)
                if st == 'SAFE': safe += 1
                elif st == 'RISKY': risky += 1
                elif st == 'TRAP': trap += 1
                else: inv += 1
                self.signals.val_row_signal.emit(em, st, sc, dt)
                time.sleep(0.03)

            self.pill_safe.setText(f"SAFE: {safe}")
            self.pill_risky.setText(f"RISKY: {risky}")
            self.pill_trap.setText(f"TRAP: {trap}")
            self.pill_invalid.setText(f"INVALID: {inv}")
            self.btn_val_run.setEnabled(True)

        self.signals.val_row_signal.connect(self.add_val_table_row)
        threading.Thread(target=worker, daemon=True).start()

    def add_val_table_row(self, email, status, score, detail):
        row = self.val_table.rowCount()
        self.val_table.insertRow(row)

        c = QColor("#00ff9d" if status == "SAFE" else "#ff2a6d" if status == "TRAP" else "#ffcc00")
        it_e = QTableWidgetItem(email); it_e.setForeground(QColor("#00f3ff"))
        it_s = QTableWidgetItem(status); it_s.setForeground(c)
        it_sc = QTableWidgetItem(str(score)); it_sc.setForeground(c)
        it_d = QTableWidgetItem(detail); it_d.setForeground(QColor("#d0d0e0"))

        for col, it in enumerate([it_e, it_s, it_sc, it_d]):
            self.val_table.setItem(row, col, it)

    def purge_traps(self):
        traps = set()
        for r in range(self.val_table.rowCount()):
            st = self.val_table.item(r, 1).text()
            if st in ('TRAP', 'INVALID'):
                traps.add(self.val_table.item(r, 0).text())
        p = self.get_base_path()
        if os.path.exists(p) and traps:
            with open(p, "r", encoding="utf-8") as f:
                lines = [l.strip() for l in f if l.strip()]
            clean = [l for l in lines if l.lower() not in traps]
            with open(p, "w", encoding="utf-8") as f:
                for em in clean:
                    f.write(f"{em}\n")
            self.seen_emails -= traps
            self.update_counters()
            QMessageBox.information(self, "Готово", f"Удалено {len(traps)} ловушек!")

    def clear_cache(self):
        self.visited_urls.clear()
        QMessageBox.information(self, "Очищено", "Кэш ссылок очищен!")

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
        base_path = self.get_base_path()

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
                            with open(base_path, "a", encoding="utf-8") as f:
                                f.write(f"{em_l}\n")
                            new_count += 1
                            self.signals.account_signal.emit(em_l, cat, url, time.strftime("%H:%M:%S"))

                    if new_count > 0:
                        self.signals.log_signal.emit(f"[+] Извлечено {new_count} почт с {url}", "success", "spider")

                    # Рекурсивный поиск новых ссылок
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

    def on_account_found(self, email, cat, src, ts):
        row = self.dash_table.rowCount()
        if row >= 25:
            self.dash_table.removeRow(0)
            row -= 1
        self.dash_table.insertRow(row)

        it_e = QTableWidgetItem(email); it_e.setForeground(QColor("#00f3ff"))
        it_c = QTableWidgetItem(cat); it_c.setForeground(QColor("#00ff9d" if "HUMAN" in cat else "#b026ff"))
        it_s = QTableWidgetItem(src[:55]); it_s.setForeground(QColor("#e0e0e0"))
        it_t = QTableWidgetItem(ts); it_t.setForeground(QColor("#8b8b9e"))

        for col, it in enumerate([it_e, it_c, it_s, it_t]):
            self.dash_table.setItem(row, col, it)
        self.update_counters()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
