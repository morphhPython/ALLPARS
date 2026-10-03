import subprocess
import sys
import os
import time
import random
import re
import threading
import queue
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QProgressBar,
                             QTextEdit, QFrame, QGraphicsDropShadowEffect, QStackedWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QObject
from PyQt6.QtGui import QPainter, QColor, QFont, QLinearGradient, QBrush, QPen, QRadialGradient
import requests  # оставлен как запасной транспорт

# ==========================================
# АВТОУСТАНОВКА ЗАВИСИМОСТЕЙ
# ==========================================
def install_deps():
    libs = ['PyQt6', 'requests', 'curl_cffi']
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"Ставлю {lib}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

install_deps()

# curl_cffi — «браузер-обманка»: имитирует реальный TLS/HTTP2 отпечаток Chrome,
# поэтому Cloudflare/Akamai пропускают запросы там, где обычный requests блокируется.
try:
    from curl_cffi import requests as curl_requests
except ImportError:
    curl_requests = None

# ==========================================
# СИГНАЛЫ ДЛЯ ВЗАИМОДЕЙСТВИЯ С GUI
# ==========================================
class ParserSignals(QObject):
    log_signal = pyqtSignal(str, str, object)
    account_signal = pyqtSignal(str, str)
    progress_signal = pyqtSignal(int)
    status_signal = pyqtSignal(str, bool)
    domain_signal = pyqtSignal(str)
    auto_iter_signal = pyqtSignal(str)

# ==========================================
# QSS СТИЛИ
# ==========================================
QSS = """
QMainWindow { background-color: #050508; }
QWidget#sidebar { background-color: rgba(15, 10, 25, 0.6); border-right: 1px solid rgba(138, 43, 226, 0.15); }
QPushButton#navBtn { font-family: "Segoe UI", sans-serif; font-size: 13px; font-weight: 500; color: #6a6a80; background-color: transparent; border: none; border-radius: 12px; padding: 14px 20px; text-align: left; min-height: 48px; }
QPushButton#navBtn:hover { color: #b0b0c0; background-color: rgba(138, 43, 226, 0.08); }
QPushButton#navBtn.active { color: #ffffff; background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:1 #b026ff); font-weight: 600; }
QWidget#card { background-color: rgba(20, 15, 35, 0.5); border: 1px solid rgba(138, 43, 226, 0.12); border-radius: 20px; }
QPushButton#actionBtn { font-family: "Segoe UI", sans-serif; font-size: 12px; font-weight: 600; color: #ffffff; background-color: rgba(138, 43, 226, 0.2); border: 1px solid rgba(138, 43, 226, 0.4); border-radius: 14px; padding: 16px 32px; min-height: 52px; letter-spacing: 0.5px; }
QPushButton#actionBtn:hover { background-color: rgba(138, 43, 226, 0.35); border-color: rgba(138, 43, 226, 0.7); }
QPushButton#actionBtn:pressed { background-color: rgba(138, 43, 226, 0.5); }
QPushButton#actionBtn:disabled { color: #3a3a4a; background-color: rgba(255, 255, 255, 0.02); border-color: rgba(255, 255, 255, 0.05); }
QPushButton#stopBtn { background-color: rgba(255, 42, 109, 0.2); border-color: rgba(255, 42, 109, 0.4); }
QPushButton#stopBtn:hover { background-color: rgba(255, 42, 109, 0.35); border-color: rgba(255, 42, 109, 0.7); }
QProgressBar { background-color: rgba(0, 0, 0, 0.4); border: 1px solid rgba(138, 43, 226, 0.1); border-radius: 10px; height: 10px; text-align: center; }
QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8A2BE2, stop:0.5 #00f3ff, stop:1 #8A2BE2); border-radius: 10px; }
QTextEdit { font-family: "Consolas", "Courier New", monospace; font-size: 11px; color: #00ff9d; background-color: rgba(0, 0, 0, 0.6); border: 1px solid rgba(138, 43, 226, 0.1); border-radius: 16px; padding: 16px; }
QTableWidget { background-color: rgba(0, 0, 0, 0.4); border: 1px solid rgba(138, 43, 226, 0.1); border-radius: 12px; gridline-color: rgba(255, 255, 255, 0.03); font-family: "Consolas", monospace; font-size: 11px; color: #e0e0e0; selection-background-color: rgba(138, 43, 226, 0.3); }
QTableWidget::item { padding: 10px; border-bottom: 1px solid rgba(255, 255, 255, 0.03); }
QHeaderView::section { background-color: transparent; color: #6a6a80; padding: 12px; border: none; border-bottom: 1px solid rgba(138, 43, 226, 0.2); font-family: "Segoe UI", sans-serif; font-weight: bold; font-size: 11px; letter-spacing: 1px; }
QLabel#statValue { font-family: "Segoe UI", sans-serif; font-size: 32px; font-weight: 700; color: #00f3ff; }
QLabel#statLabel { font-family: "Segoe UI", sans-serif; font-size: 11px; color: #6a6a80; letter-spacing: 1px; text-transform: uppercase; }
QLabel#statusText { font-family: "Consolas", monospace; font-size: 11px; color: #4a4a5a; letter-spacing: 2px; }
"""

# ==========================================
# ФОНОВЫЕ ОРБЫ
# ==========================================
class OrbBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.orbs = [
            {"x": 200, "y": 150, "r": 180, "color": QColor(138, 43, 226, 60), "vx": 0.3, "vy": 0.2},
            {"x": 800, "y": 400, "r": 220, "color": QColor(0, 243, 255, 40), "vx": -0.2, "vy": 0.3},
            {"x": 500, "y": 600, "r": 150, "color": QColor(176, 38, 255, 50), "vx": 0.2, "vy": -0.2},
            {"x": 1200, "y": 200, "r": 200, "color": QColor(138, 43, 226, 45), "vx": -0.3, "vy": 0.1},
        ]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)
        self.timer.start(30)

    def animate(self):
        for orb in self.orbs:
            orb["x"] += orb["vx"]
            orb["y"] += orb["vy"]
            if orb["x"] < -orb["r"] or orb["x"] > self.width() + orb["r"]: orb["vx"] *= -1
            if orb["y"] < -orb["r"] or orb["y"] > self.height() + orb["r"]: orb["vy"] *= -1
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(5, 5, 8))
        for orb in self.orbs:
            gradient = QRadialGradient(orb["x"], orb["y"], orb["r"])
            gradient.setColorAt(0, orb["color"])
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(int(orb["x"] - orb["r"]), int(orb["y"] - orb["r"]),
                              int(orb["r"] * 2), int(orb["r"] * 2))
        painter.end()

# ==========================================
# БОКОВАЯ НАВИГАЦИЯ
# ==========================================
class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(240)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 40, 20, 40)
        layout.setSpacing(8)

        logo = QLabel("MORPHH")
        logo.setFont(QFont("Arial Black", 20, QFont.Weight.Black))
        logo.setStyleSheet("color: #00f3ff; background: transparent; padding: 20px 0;")
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo)

        sub = QLabel("CucurelaMailpars.xyz")
        sub.setFont(QFont("Segoe UI", 9))
        sub.setStyleSheet("color: #6a6a80; background: transparent; padding-bottom: 30px;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(sub)

        self.buttons = {}
        nav_items = [
            ("dashboard", "⌂  Dashboard"),
            ("parser", "▶  Parser"),
            ("auto", "  Auto Mode"),
            ("stats", "  Statistics"),
        ]

        for key, text in nav_items:
            btn = QPushButton(text)
            btn.setObjectName("navBtn")
            btn.clicked.connect(lambda checked, k=key: self.on_nav(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        layout.addStretch()

        ver = QLabel("v2.5 • Extractor")
        ver.setFont(QFont("Consolas", 9))
        ver.setStyleSheet("color: #3a3a4a; background: transparent; padding: 10px 0;")
        ver.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(ver)

        self.active_key = None
        self.on_nav("dashboard")

    def on_nav(self, key):
        if self.active_key:
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

# ==========================================
# ГЛАВНОЕ ОКНО
# ==========================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CucurelaMailpars.xyz")

        self.running = False
        self.signals = ParserSignals()

        # ЛЮБЫЕ ДОМЕНЫ: собираем все валидные адреса вида имя@домен.зона.
        # Хвост (?!\.png|jpg...) отсекает картинки/файлы вроде nasa-logo@2x.png,
        # а (?![a-z0-9]) — обрывы на букву/цифру.
        self.email_regex = re.compile(
            r'[a-zA-Z0-9][a-zA-Z0-9._%+\-]*@[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?'
            r'(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9\-]*[a-zA-Z0-9])?)*\.[a-zA-Z]{2,63}'
            r'(?![a-z0-9])(?!\.(?:png|jpe?g|gif|webp|svg|ico|bmp|tiff?|css|js|mp4|mp3|zip))',
            re.IGNORECASE)
        # Белый список доменных зон: отсявает "почты" вроде logo@2x.png,
        # где ".png" притворяется зоной.
        self.valid_tlds = {
            'com','net','org','info','biz','edu','gov','mil','io','co','me','tv','cc','xyz','app','dev',
            'ru','su','ua','by','kz','uz','ge','am','az','md','ee','lv','lt','pl','de','at','ch','fr',
            'it','es','pt','nl','be','dk','se','no','fi','is','uk','ie','eu','cz','sk','hu','ro','bg','rs',
            'hr','si','ba','mk','al','gr','tr','cy','mt','lu','li','va','sm','ad','mc','fo','gl','ax',
            'scot','wales','cymru','eng','bzh','cat','asia','africa','int','arpa',
            'club','online','site','store','shop','tech','space','website','live','world','email','cloud',
            'agency','company','solutions','services','media','news','blog','wiki','design','studio','digital',
            'network','hosting','domains','zone','link','click','fun','buzz','icu','top','vip','pro','name',
            'mobi','tel','travel','jobs','post','aero','museum','coop','example',
            'jp','cn','kr','in','id','th','vn','my','sg','ph','nz','au','ca','mx','br','ar','cl',
        }
        # Ссылки из href="", src='' (абсолютные и относительные) + голые http(s)-адреса в тексте/js
        self.url_regex = re.compile(r'''(?:href|src|action)\s*=\s*["']\s*(https?://[^\s"'<>]+|[^"'\s<>]*)["']''')
        self.bare_url_regex = re.compile(r'''(?<!["'\w])(https?://[^\s"'<>()\[\]{}]+)''')
        # Прежние сиды сохранены как legacy_seed_urls (не удалены по прежнему требованию).
        self.legacy_seed_urls = [
            "https://ycombinator.com",
            "https://reddit.com",
            "github.com"
            ]
        # НОВЫЙ АВТОМАТИЧЕСКИЙ СТАРТОВЫЙ СПИСОК (пользователю ничего вводить не надо):
        # страницы контактов госорганов/фондов — там гарантированно публикуют почты,
        # плюс общешрамовые хабы для разгона обхода по всему интернету.
        self.seed_urls = [
            "https://www.cisa.gov/contact-us",
            "https://www.fcc.gov/about-fcc/office-inspector-general-contact-us",
            "https://www.ftc.gov/about-ftc/contact",
            "https://medlineplus.gov/contactinformation.html",
            "https://www.usa.gov/about-the-site",
            "https://www.epa.gov/contact",
            "https://www.irs.gov/help/telephone-assistance",
            "https://www.nsf.gov/about/",
            "https://www.europarl.europa.eu/portal/en/contact",
            "https://www.un.org/en/about-us/contact-us",
            "https://www.wikipedia.org",
            "https://web.archive.org",
            "https://news.ycombinator.com",
            "https://lite.cnn.com",
            "https://www.nasa.gov/nasa-office-of-inspector-general/",
            "https://directory.fsf.org/wiki/Main_Page",
            "https://en.wikipedia.org/wiki/Wikipedia:Contact_us",
        ] + self.legacy_seed_urls
        self.known_domains = set()      # все найденные домены сайтов (для счётчика)
        self.seen_emails = set()        # дедупликация базы
        self.link_cap = 8000            # потолок очереди ссылок (чтобы не раздуть RAM)
        self.bg = OrbBackground(self)
        self.bg.setGeometry(0, 0, self.width(), self.height())
        main = QWidget(self)
        main.setStyleSheet("background: transparent;")
        main_layout = QHBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.content = QStackedWidget()
        self.content.setStyleSheet("background: transparent;")
        self.page_dashboard = self.create_dashboard_page()
        self.page_parser = self.create_parser_page()
        self.page_auto = self.create_auto_page()
        self.page_stats = self.create_stats_page()
        self.content.addWidget(self.page_dashboard)
        self.content.addWidget(self.page_parser)
        self.content.addWidget(self.page_auto)
        self.content.addWidget(self.page_stats)
        self.sidebar = Sidebar(main)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content, 1)
        self.setCentralWidget(main)

        self.signals.log_signal.connect(self.write_log_safe)
        self.signals.account_signal.connect(self.add_to_recent_table)
        self.signals.progress_signal.connect(self.progress_dash.setValue)
        self.signals.status_signal.connect(self.set_status_safe)
        self.signals.domain_signal.connect(self.stat_domain.setText)
        self.signals.auto_iter_signal.connect(self.auto_iter.setText)

        self.showFullScreen()
        self.setStyleSheet(QSS)
        self.setWindowOpacity(0)
        self.anim = QPropertyAnimation(self, b"windowOpacity")
        self.anim.setDuration(800)
        self.anim.setStartValue(0.0)
        self.anim.setEndValue(1.0)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()
        self.update_total_ui()

    def switch_page(self, key):
        pages = {"dashboard": 0, "parser": 1, "auto": 2, "stats": 3}
        if key in pages:
            self.content.setCurrentIndex(pages[key])
            if key == "stats":
                self.update_total_ui()

    # ==========================================
    # ИЗМЕНЕННЫЙ ДЕСКРИПТОР ВЫХОДНОГО ФАЙЛА
    # ==========================================
    def get_file_path(self):
        """Возвращает путь к целевому файлу сбора базы"""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), "BazaPochtRassilka.txt")

    def _is_real_email(self, email):
        """Проверка: реальный ли это адрес, а не имя файла картинки (logo@2x.png)."""
        if '@' not in email:
            return False
        domain = email.rsplit('@', 1)[-1]
        tld = domain.rsplit('.', 1)[-1].lower()
        return tld in self.valid_tlds

    def _load_existing_base(self):
        """Загружает уже собранную базу в память, чтобы не дублировать адреса."""
        p = self.get_file_path()
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    for line in f:
                        e = line.strip().lower()
                        if e:
                            self.seen_emails.add(e)
            except Exception:
                pass

    @staticmethod
    def _normalize_url(u):
        """Нормализация: без фрагментов #..., без хвостовых знаков препинания."""
        u = u.split("#")[0].rstrip(".,;:'\")>]}")
        return u

    def _extract_links(self, html, base_url):
        """Достаёт ВСЕ ссылки из href/src/action и голого текста, возвращает полные url."""
        from urllib.parse import urljoin, urlparse
        out = []
        raws = [m.group(1) for m in self.url_regex.finditer(html)]
        raws += [m.group(1) for m in self.bare_url_regex.finditer(html)]
        for raw in raws:
            if not raw:
                continue
            absu = self._normalize_url(urljoin(base_url, raw.strip()))
            try:
                pr = urlparse(absu)
            except Exception:
                continue
            if pr.scheme not in ("http", "https"):
                continue
            host = (pr.hostname or "").lower()
            if not host or "." not in host:
                continue
            port = pr.port
            if port and port not in (80, 443):
                continue
            path_l = (pr.path or "/").lower()
            # не качаем бинарники/архивы
            if path_l.endswith((".zip", ".gz", ".tar", ".bz2", ".7z", ".rar", ".exe", ".dmg",
                                ".iso", ".pdf", ".png", ".jpg", ".jpeg", ".gif", ".webp",
                                ".svg", ".ico", ".css", ".js", ".mp4", ".mp3", ".woff", ".woff2")):
                continue
            out.append(absu)
        return out

    def get_total_count(self):
        p = self.get_file_path()
        if os.path.exists(p):
            with open(p, "r", encoding="utf-8") as f:
                return len([l for l in f.readlines() if l.strip()])
        return 0

    def update_total_ui(self):
        count = self.get_total_count()
        self.stat_total.setText(str(count))
        self.stats_total_lbl.setText(str(count))
        self.stats_path_lbl.setText(f"Path: {self.get_file_path()}")

    def add_to_recent_table(self, email, source_url):
        row = self.recent_table.rowCount()
        if row >= 15:
            self.recent_table.removeRow(0)
            row -= 1
        self.recent_table.insertRow(row)
        email_item = QTableWidgetItem(email)
        email_item.setForeground(QColor(0, 243, 255))
        self.recent_table.setItem(row, 0, email_item)
        src_item = QTableWidgetItem(source_url)
        src_item.setForeground(QColor(176, 38, 255))
        self.recent_table.setItem(row, 1, src_item)
        time_item = QTableWidgetItem(time.strftime("%H:%M:%S"))
        time_item.setForeground(QColor(106, 106, 128))
        self.recent_table.setItem(row, 2, time_item)
        self.recent_table.scrollToBottom()
        self.update_total_ui()

    def create_dashboard_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        header = QLabel("Dashboard")
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        sub = QLabel("System overview and global target harvesting")
        sub.setFont(QFont("Segoe UI", 12))
        sub.setStyleSheet("color: #6a6a80; margin-bottom: 20px;")
        layout.addWidget(sub)
        stats_row = QHBoxLayout()
        stats_row.setSpacing(20)
        card1 = QWidget()
        card1.setObjectName("card")
        l1 = QVBoxLayout(card1)
        l1.setContentsMargins(24, 24, 24, 24)
        self.stat_total = QLabel("0")
        self.stat_total.setObjectName("statValue")
        l1.addWidget(self.stat_total)
        lbl1 = QLabel("Harvested Mails")
        lbl1.setObjectName("statLabel")
        l1.addWidget(lbl1)
        stats_row.addWidget(card1)
        card2 = QWidget()
        card2.setObjectName("card")
        l2 = QVBoxLayout(card2)
        l2.setContentsMargins(24, 24, 24, 24)
        self.stat_status = QLabel("IDLE")
        self.stat_status.setObjectName("statValue")
        self.stat_status.setStyleSheet("color: #8A2BE2;")
        l2.addWidget(self.stat_status)
        lbl2 = QLabel("Crawler Engine")
        lbl2.setObjectName("statLabel")
        l2.addWidget(lbl2)
        stats_row.addWidget(card2)
        card3 = QWidget()
        card3.setObjectName("card")
        l3 = QVBoxLayout(card3)
        l3.setContentsMargins(24, 24, 24, 24)
        self.stat_domain = QLabel("---")
        self.stat_domain.setObjectName("statValue")
        self.stat_domain.setStyleSheet("color: #00ff9d; font-size: 16px;")
        l3.addWidget(self.stat_domain)
        lbl3 = QLabel("Current Target URL")
        lbl3.setObjectName("statLabel")
        l3.addWidget(lbl3)
        stats_row.addWidget(card3)
        layout.addLayout(stats_row)
        actions_card = QWidget()
        actions_card.setObjectName("card")
        al = QVBoxLayout(actions_card)
        al.setContentsMargins(32, 32, 32, 32)
        al.setSpacing(20)
        lbl_act = QLabel("Control Deck")
        lbl_act.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_act.setStyleSheet("color: #ffffff;")
        al.addWidget(lbl_act)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        self.btn_dash_run = QPushButton("▶  Run Single Session")
        self.btn_dash_run.setObjectName("actionBtn")
        self.btn_dash_run.clicked.connect(self.start_parsing)
        btn_row.addWidget(self.btn_dash_run)
        self.btn_dash_auto = QPushButton("∞  Enable Infinite Crawl")
        self.btn_dash_auto.setObjectName("actionBtn")
        self.btn_dash_auto.clicked.connect(self.start_auto)
        btn_row.addWidget(self.btn_dash_auto)
        self.btn_dash_stop = QPushButton("■  Kill Process")
        self.btn_dash_stop.setObjectName("stopBtn")
        self.btn_dash_stop.setProperty("class", "actionBtn")
        self.btn_dash_stop.clicked.connect(self.stop_all)
        self.btn_dash_stop.setEnabled(False)
        btn_row.addWidget(self.btn_dash_stop)
        al.addLayout(btn_row)
        self.progress_dash = QProgressBar()
        self.progress_dash.setValue(0)
        al.addWidget(self.progress_dash)
        self.status_dash = QLabel("SYSTEM IDLE")
        self.status_dash.setObjectName("statusText")
        al.addWidget(self.status_dash)
        layout.addWidget(actions_card)
        recent_card = QWidget()
        recent_card.setObjectName("card")
        rl = QVBoxLayout(recent_card)
        rl.setContentsMargins(24, 24, 24, 24)
        rl.setSpacing(16)
        lbl_recent = QLabel("Extracted Base (Live Feed)")
        lbl_recent.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_recent.setStyleSheet("color: #ffffff;")
        rl.addWidget(lbl_recent)
        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels(["TARGET EMAIL", "SOURCE DOMAIN/URL", "TIMESTAMP"])
        self.recent_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.recent_table.setShowGrid(False)
        self.recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        rl.addWidget(self.recent_table)
        layout.addWidget(recent_card)
        return page

    def create_parser_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        header = QLabel("Parser Logs")
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        term_card = QWidget()
        term_card.setObjectName("card")
        tl = QVBoxLayout(term_card)
        tl.setContentsMargins(24, 24, 24, 24)
        tl.setSpacing(16)
        self.log_parser = QTextEdit()
        self.log_parser.setReadOnly(True)
        tl.addWidget(self.log_parser, 1)
        layout.addWidget(term_card, 1)
        return page

    def create_auto_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        header = QLabel("Infinite Engine")
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        ctrl_card = QWidget()
        ctrl_card.setObjectName("card")
        cl = QVBoxLayout(ctrl_card)
        cl.setContentsMargins(32, 32, 32, 32)
        cl.setSpacing(20)
        self.auto_status = QLabel("INFINITE MODE: OFF")
        self.auto_status.setFont(QFont("Consolas", 18, QFont.Weight.Bold))
        self.auto_status.setStyleSheet("color: #8A2BE2;")
        cl.addWidget(self.auto_status)
        self.auto_iter = QLabel("Links In Queue: 0")
        self.auto_iter.setFont(QFont("Consolas", 12))
        self.auto_iter.setStyleSheet("color: #6a6a80;")
        cl.addWidget(self.auto_iter)
        btn_row = QHBoxLayout()
        btn_row.setSpacing(16)
        self.btn_auto_start = QPushButton("  Launch Infinite")
        self.btn_auto_start.setObjectName("actionBtn")
        self.btn_auto_start.clicked.connect(self.start_auto)
        btn_row.addWidget(self.btn_auto_start)
        self.btn_auto_stop = QPushButton("■  Stop")
        self.btn_auto_stop.setObjectName("stopBtn")
        self.btn_auto_stop.setProperty("class", "actionBtn")
        self.btn_auto_stop.clicked.connect(self.stop_all)
        self.btn_auto_stop.setEnabled(False)
        btn_row.addWidget(self.btn_auto_stop)
        cl.addLayout(btn_row)
        layout.addWidget(ctrl_card)
        log_card = QWidget()
        log_card.setObjectName("card")
        ll = QVBoxLayout(log_card)
        ll.setContentsMargins(24, 24, 24, 24)
        self.log_auto = QTextEdit()
        self.log_auto.setReadOnly(True)
        ll.addWidget(self.log_auto, 1)
        layout.addWidget(log_card, 1)
        return page

    def create_stats_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(24)
        header = QLabel("Database Statistics")
        header.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        header.setStyleSheet("color: #ffffff;")
        layout.addWidget(header)
        stats_card = QWidget()
        stats_card.setObjectName("card")
        sl = QVBoxLayout(stats_card)
        sl.setContentsMargins(40, 40, 40, 40)
        sl.setSpacing(24)
        self.stats_total_lbl = QLabel("0")
        self.stats_total_lbl.setObjectName("statValue")
        self.stats_total_lbl.setStyleSheet("color: #00f3ff; font-size: 64px;")
        sl.addWidget(self.stats_total_lbl)
        lbl_st = QLabel("Total Records Harvested In Local TXT")
        lbl_st.setObjectName("statLabel")
        sl.addWidget(lbl_st)
        self.stats_path_lbl = QLabel("Path: ---")
        self.stats_path_lbl.setFont(QFont("Consolas", 11))
        self.stats_path_lbl.setStyleSheet("color: #4a4a5a; margin-top: 20px;")
        sl.addWidget(self.stats_path_lbl)
        layout.addWidget(stats_card)
        layout.addStretch()
        return page

    def write_log_safe(self, msg, tag, widget_type):
        widget = self.log_auto if widget_type == "auto" else self.log_parser
        ts = time.strftime("%H:%M:%S")
        colors = {"info": "#00f3ff", "err": "#ff2a6d", "warn": "#ffcc00", "success": "#00ff9d"}
        color = colors.get(tag, "#a0a0b0")
        widget.append(f'<span style="color:{color};">[{ts}] {msg}</span>')

    def set_status_safe(self, text, running):
        self.status_dash.setText(text)
        self.status_dash.setStyleSheet(f"color: {'#00f3ff' if running else '#4a4a5a'}; font-family: Consolas; font-size: 11px; letter-spacing: 2px;")
        self.stat_status.setText("ACTIVE" if running else "IDLE")
        self.stat_status.setStyleSheet(f"color: {'#00ff9d' if running else '#8A2BE2'};")
        self.btn_dash_run.setEnabled(not running)
        self.btn_dash_auto.setEnabled(not running)
        self.btn_dash_stop.setEnabled(running)
        self.btn_auto_start.setEnabled(not running)
        self.btn_auto_stop.setEnabled(running)
        if running:
            self.auto_status.setText("ENGINE: CRAWLING")
            self.auto_status.setStyleSheet("color: #00ff9d;")
        else:
            self.auto_status.setText("ENGINE: STOPPED")
            self.auto_status.setStyleSheet("color: #8A2BE2;")

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
        """Загрузка страницы: сначала через curl_cffi (имитация Chrome), при сбое — обычный requests."""
        if curl_requests is not None:
            try:
                return curl_requests.get(url, impersonate="chrome", timeout=8, allow_redirects=True)
            except Exception:
                pass  # падаем на запасной транспорт
        headers = {"User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")}
        return requests.get(url, headers=headers, timeout=8, allow_redirects=True)

    def _execute_harvest(self, url_queue, max_pages=None, log_widget="parser"):
        visited = set()
        pages_processed = 0
        file_path = self.get_file_path()
        self._load_existing_base()
        # Запасаемся стартовыми ссылками: если очередь пуста или движок её «съел»,
        # он подпитывается сидами и работает дальше (максимально широкий обход).
        def _seed_variants(u):
            u = self._normalize_url(u)
            v = {u}
            if u.endswith('/'):
                v.add(u[:-1])
            if u.startswith('https://'):
                v.add('http://' + u[len('https://'):])
            return v
        seed_snapshot = [self._normalize_url(s) for s in self.seed_urls]

        while self.running:
            if max_pages and pages_processed >= max_pages:
                break
            if url_queue.empty():
                for s in seed_snapshot:
                    if not (_seed_variants(s) & visited):
                        url_queue.put(s)
                if url_queue.empty():
                    break
            try:
                current_url = url_queue.get_nowait()
            except queue.Empty:
                continue
            url_key = current_url.rstrip('/')
            if url_key in visited:
                continue
            visited.add(url_key)
            self.signals.domain_signal.emit(current_url[:40] + "...")
            self.signals.log_signal.emit(f"Запрос к источнику: {current_url}", "info", log_widget)
            try:
                r = self._fetch_page(current_url)
                pages_processed += 1
                if max_pages:
                    self.signals.progress_signal.emit(int((pages_processed / max_pages) * 100))
                if r.status_code == 200:
                    html = r.text
                    # учёт всех найденных доменов сайтов
                    from urllib.parse import urlparse
                    try:
                        host = (urlparse(current_url).hostname or "").lower()
                        if host:
                            self.known_domains.add(host)
                    except Exception:
                        pass
                    found_mails = set(m.lower() for m in self.email_regex.findall(html)
                                      if self._is_real_email(m))
                    new_mails = [m for m in found_mails if m not in self.seen_emails]
                    if new_mails:
                        self.signals.log_signal.emit(f"Найдено {len(new_mails)} НОВЫХ адресов на странице", "success", log_widget)
                        with open(file_path, "a", encoding="utf-8") as f:
                            for email in new_mails:
                                self.seen_emails.add(email)
                                f.write(f"{email}\n")
                                self.signals.account_signal.emit(email, current_url.split("//")[-1].split("/")[0])
                    # Собираем ВСЕ ссылки со страницы в любую точку интернета
                    if url_queue.qsize() < self.link_cap:
                        for link in self._extract_links(html, current_url):
                            if link.rstrip('/') not in visited and url_queue.qsize() < self.link_cap:
                                url_queue.put(link)
                    self.signals.auto_iter_signal.emit(
                        f"Queue: {url_queue.qsize()} | Visited: {len(visited)} | "
                        f"Domains: {len(self.known_domains)} | Base: {len(self.seen_emails)}")
            except Exception as e:
                self.signals.log_signal.emit(f"Ошибка чтения {current_url[:30]}: {str(e)[:30]}", "err", log_widget)
            time.sleep(0.5)

    def _run_single_session(self):
        url_queue = queue.Queue()
        for url in self.seed_urls:
            url_queue.put(url)
        self.signals.log_signal.emit("Запуск ограниченной сессии сбора данных...", "info", "parser")
        self._execute_harvest(url_queue, max_pages=60, log_widget="parser")
        self.running = False
        self.signals.status_signal.emit("SYSTEM IDLE", False)
        self.signals.progress_signal.emit(100)
        self.signals.log_signal.emit("Ограниченная сессия успешно завершена.", "success", "parser")

    def _run_infinite_session(self):
        url_queue = queue.Queue()
        for url in self.seed_urls:
            url_queue.put(url)
        self.signals.log_signal.emit("СТАРТ БЕСКОНЕЧНОГО ДВИЖКА OSINT...", "info", "auto")
        self._execute_harvest(url_queue, max_pages=None, log_widget="auto")
        self.running = False
        self.signals.status_signal.emit("SYSTEM IDLE", False)
        self.signals.progress_signal.emit(0)
        self.signals.log_signal.emit("Бесконечный сбор остановлен оператором.", "warn", "auto")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
