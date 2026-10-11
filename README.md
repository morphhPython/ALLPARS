<p align="center">
  <h1 align="center">🌐 ALLPARS </h1>
  <p align="center">
    <b>Advanced OSINT, Email Harvesting & Smart Outreach Suite</b><br>
    <i>Crawler • AI Validator • Smart Mailer • Lo-Fi Radio</i>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python" alt="Python">
    <img src="https://img.shields.io/badge/PyQt6-Glass%20UI-green?style=for-the-badge&logo=qt" alt="PyQt6">
    <img src="https://img.shields.io/badge/License-Public%20Property-red?style=for-the-badge" alt="License">
  </p>
</p>

## 📖 About the Project

**ALLPARS** is a powerful, all-in-one OSINT and email harvesting ecosystem created and maintained by a single developer ([@morphhPython](https://github.com/morphhPython)). 

Designed for researchers, marketers, and OSINT specialists, it combines a multi-threaded recursive crawler, an AI-powered email validator, and a smart outreach mailer into one beautiful, glassmorphic desktop application. Whether you need to scrape thousands of emails using search engine dorks or run a safe, AI-personalized outreach campaign, ALLPARS handles it autonomously.

> **⚠️ Disclaimer:** This tool is intended for educational purposes, authorized OSINT research, and legitimate B2B outreach. Always respect privacy laws (GDPR, CCPA) / Terms of Service.

---

## 🚀 Core Features

### 🕷️ Recursive Crawler & Dork Engine
*   **Multi-Threaded Spider:** High-speed concurrent harvesting with polite rate-limiting and domain-level delays.
*   **Dork Generator:** Built-in support for generating and scraping via **Google, DuckDuckGo, Bing, and Yandex** dorks.
*   **Deep Regex Extraction:** Advanced regular expressions that filter out fake emails, image extensions, and CSS/JS artifacts.

### 🛡️ AI-Powered Mail Validator
*   **Honeypot & Spam-Trap Detection:** AI and heuristic analysis to identify and block spam-traps before you send a single email.
*   **MX & DNS Verification:** Real-time DNS resolver checks to ensure the domain accepts incoming mail.
*   **Geo & Activity Profiling:** Automatic country detection (via TLD/Domain mapping) and last-active estimation.
*   **Disposable Filter:** Automatically flags and drops temporary email services (e.g., Mailinator, Yopmail).

### ✉️ Smart Mailer with Anti-Spam Shield
*   **Pre-Flight Safety Block:** The mailer physically blocks you from sending emails to addresses flagged as `TRAP` or `INVALID` by the validator.
*   **AI Text Generation:** Integrated AI assistance to write personalized, high-converting outreach letter templates.
*   **Multi-Account SMTP Vault:** Securely manage multiple sender accounts (`accounts.txt`) with automatic provider detection (Gmail, Yandex, Mail.ru, Outlook, etc.).
*   **RFC5322 Compliance:** Proper headers, Message-IDs, and HTML/Plain-text multipart formatting to maximize inbox delivery rates.

### 🎨 Premium "Clean Glass" GUI
*   **Glassmorphism & Real Blur:** True frosted-glass UI with dynamic background blur, light/dark theme switching, and vector-based icons.
*   **Live Dashboard:** Real-time statistics, country distribution, and animated spectrum visualizers.
*   **Database Management:** Built-in SQLite database with instant search, filtering, and 1-click exports to **CSV, JSON, and TXT**.

### 📻 Built-in Lo-Fi Radio
*   Stay focused while harvesting! Integrated 24/7 Lo-Fi, Chillhop, and Cyberpunk radio stations with a live audio spectrum visualizer and volume control.

📞 Contacts & Community
Created with ❤️ by morphhPython
GitHub: github.com/morphhPython
Telegram (Personal): @oersus
Telegram (Community/Club): @recessclub
If you find a bug, have a feature request, or want to contribute, feel free to open an Issue or reach out via Telegram!
