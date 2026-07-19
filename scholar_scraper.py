#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import random
import re
import time
import socket
import smtplib
import platform
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, List, Dict, Any, Tuple, Set
from dataclasses import dataclass, field

# Windows için ANSI renk desteğini etkinleştir
if platform.system() == 'Windows':
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    except:
        pass

class Colors:
    # Windows'ta renklerin çalışması için ANSI escape kodları
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

def colored(text: str, color: str = Colors.WHITE, bold: bool = False, dim: bool = False, underline: bool = False) -> str:
    result = ""
    if bold:
        result += Colors.BOLD
    if dim:
        result += Colors.DIM
    if underline:
        result += Colors.UNDERLINE
    result += color + text + Colors.RESET
    return result

class Logger:
    def __init__(self):
        self.log_level = "INFO"
        # Windows'ta renkleri kapatma seçeneği
        self.use_colors = True
        if platform.system() == 'Windows':
            # Windows terminalinde renkler çalışmıyorsa kapat
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # Konsol modunu kontrol et
                mode = ctypes.c_ulong()
                kernel32.GetConsoleMode(kernel32.GetStdHandle(-11), ctypes.byref(mode))
                if not (mode.value & 4):  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
                    self.use_colors = False
            except:
                self.use_colors = False
    
    def _format(self, message: str, color: str, bold: bool = False) -> str:
        timestamp = datetime.now().strftime("%H:%M:%S")
        if self.use_colors:
            time_str = colored(f"[{timestamp}]", Colors.BRIGHT_BLACK, dim=True)
            msg = colored(message, color, bold=bold)
        else:
            time_str = f"[{timestamp}]"
            msg = message
        return f"{time_str} {msg}"
    
    def info(self, message: str):
        print(self._format(message, Colors.BRIGHT_WHITE))
    
    def success(self, message: str):
        print(self._format(message, Colors.BRIGHT_GREEN, bold=True))
    
    def error(self, message: str):
        print(self._format(message, Colors.BRIGHT_RED, bold=True))
    
    def warning(self, message: str):
        print(self._format(message, Colors.BRIGHT_YELLOW, bold=True))
    
    def search(self, message: str):
        print(self._format(message, Colors.BRIGHT_CYAN))
    
    def email(self, message: str):
        print(self._format(message, Colors.BRIGHT_MAGENTA))
    
    def verify(self, message: str):
        print(self._format(message, Colors.BRIGHT_GREEN))
    
    def osint(self, message: str):
        print(self._format(message, Colors.BRIGHT_BLUE))
    
    def save(self, message: str):
        print(self._format(message, Colors.BRIGHT_YELLOW))
    
    def header(self, message: str):
        if self.use_colors:
            print(colored("=" * 70, Colors.BRIGHT_BLACK, dim=True))
            print(colored(f"  {message}", Colors.BRIGHT_WHITE, bold=True))
            print(colored("=" * 70, Colors.BRIGHT_BLACK, dim=True))
        else:
            print("=" * 70)
            print(f"  {message}")
            print("=" * 70)
    
    def subheader(self, message: str):
        if self.use_colors:
            print(colored(f"--- {message} ---", Colors.BRIGHT_BLACK, dim=True))
        else:
            print(f"--- {message} ---")
    
    def progress(self, current: int, total: int, message: str = ""):
        percent = (current / total * 100) if total > 0 else 0
        bar_length = 35
        filled = int(bar_length * current / total) if total > 0 else 0
        bar = "#" * filled + "-" * (bar_length - filled)
        if self.use_colors:
            color = Colors.BRIGHT_GREEN if percent > 80 else Colors.BRIGHT_YELLOW if percent > 50 else Colors.BRIGHT_CYAN
            print(colored(f"  [{bar}] {percent:5.1f}%  {message}", color))
        else:
            print(f"  [{bar}] {percent:5.1f}%  {message}")

log = Logger()

VERSION = "1.0.0"
APP_NAME = "NetSchlr"
COOKIE_FILE = Path("scholar_cookies.json")
SAVED_DIR = Path("saved")
SAVED_DIR.mkdir(exist_ok=True)

CHROME_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

BOT_JS = """
    Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
    Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
    Object.defineProperty(navigator, 'languages', { get: () => ['tr-TR','tr','en-US','en'] });
"""

SYSTEM_EMAILS = [
    'google.com', 'gstatic.com', 'sentry.io', 'schema.org',
    'example.com', 'w3.org', 'microsoft.com', 'apple.com',
    'amazon.com', 'facebook.com', 'twitter.com', 'instagram.com',
    'linkedin.com', 'github.com', 'gitlab.com', 'bitbucket.com',
    'stackoverflow.com', 'reddit.com', 'discord.com', 'slack.com',
    'teams.com', 'zoom.com', 'meet.com', 'outlook.com',
    'hotmail.com', 'live.com', 'msn.com', 'yahoo.com',
    'yandex.com', 'mail.ru', 'protonmail.com', 'tutanota.com'
]

OSINT_PLATFORMS = {
    'linkedin': 'https://www.linkedin.com/in/',
    'twitter': 'https://twitter.com/',
    'researchgate': 'https://www.researchgate.net/profile/',
    'academia': 'https://independent.academia.edu/',
    'github': 'https://github.com/',
    'orcid': 'https://orcid.org/',
    'publons': 'https://publons.com/researcher/',
    'medium': 'https://medium.com/@',
    'stackoverflow': 'https://stackoverflow.com/users/',
    'facebook': 'https://www.facebook.com/',
    'instagram': 'https://www.instagram.com/',
    'youtube': 'https://www.youtube.com/@',
    'tiktok': 'https://www.tiktok.com/@',
    'pinterest': 'https://www.pinterest.com/',
    'reddit': 'https://www.reddit.com/user/',
    'quora': 'https://www.quora.com/profile/',
    'goodreads': 'https://www.goodreads.com/user/show/',
    'personal_website': ''
}

@dataclass
class Researcher:
    name: str = ""
    email: str = ""
    verified: bool = False
    institution: str = ""
    interests: str = ""
    citations: int = 0
    profile_url: str = ""
    orcid: str = ""
    source: str = ""
    linkedin: str = ""
    twitter: str = ""
    researchgate: str = ""
    github: str = ""
    additional_emails: List[str] = field(default_factory=list)
    email_status: str = ""
    email_valid: str = ""
    email_message: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    social_links: Dict[str, str] = field(default_factory=dict)
    dork_results: Dict[str, List[str]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'Name': self.name,
            'Email': self.email,
            'Verified': 'Yes' if self.verified else 'No',
            'Institution': self.institution,
            'Interests': self.interests,
            'Citations': self.citations,
            'Profile URL': self.profile_url,
            'ORCID': self.orcid,
            'Source': self.source,
            'LinkedIn': self.linkedin,
            'Twitter': self.twitter,
            'ResearchGate': self.researchgate,
            'GitHub': self.github,
            'Email_Status': self.email_status,
            'Email_Valid': self.email_valid,
            'Email_Message': self.email_message,
            'Additional Emails': ', '.join(self.additional_emails),
            'Timestamp': self.timestamp
        }

def check_dependencies():
    import importlib.util
    missing = []
    if not importlib.util.find_spec("pandas"):
        missing.append("pandas")
    if not importlib.util.find_spec("playwright"):
        missing.append("playwright")
    if not importlib.util.find_spec("dns"):
        missing.append("dnspython")
    if missing:
        log.error(f"Missing: pip install {' '.join(missing)}")
        if "playwright" in missing:
            log.error("Then: playwright install chromium")
        sys.exit(1)

def save_cookies():
    from playwright.sync_api import sync_playwright
    log.header("COOKIE SETUP")
    log.info("Opening browser...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=CHROME_UA,
            locale="tr-TR",
        )
        ctx.add_init_script(BOT_JS)
        ctx.new_page().goto("https://scholar.google.com", wait_until="domcontentloaded")
        log.warning("Please login to Google Scholar in the browser window.")
        input(colored("\nPress ENTER after login... ", Colors.BRIGHT_YELLOW, bold=True))
        cookies = ctx.cookies()
        COOKIE_FILE.write_text(json.dumps(cookies, ensure_ascii=False, indent=2), encoding="utf-8")
        browser.close()
        log.success(f"Saved {len(cookies)} cookies -> {COOKIE_FILE.resolve()}")

def clean_turkish_chars(text: str) -> str:
    """Türkçe karakterleri İngilizce karşılıklarına dönüştürür"""
    turkish_chars = "çğıöşüÇĞİÖŞÜ"
    english_chars = "cgiosuCGIOSU"
    trans = str.maketrans(turkish_chars, english_chars)
    return text.translate(trans)

def is_system_email(email: str) -> bool:
    if not email:
        return True
    email_lower = email.lower()
    for system in SYSTEM_EMAILS:
        if system in email_lower:
            return True
    return False

def generate_username(name: str) -> str:
    if not name:
        return "user"
    clean_name = clean_turkish_chars(name.strip().lower())
    clean_name = re.sub(r'[^a-z0-9\s]', '', clean_name)
    parts = clean_name.split()
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[-1]}"
    return parts[0] if parts else "user"

def check_url_exists(page, url: str) -> bool:
    try:
        page.goto(url, wait_until='domcontentloaded', timeout=5000)
        time.sleep(0.3)
        return not page.url.startswith('https://www.google.com/')
    except:
        return False

def get_mx_records(domain: str) -> list:
    try:
        import dns.resolver
        records = dns.resolver.resolve(domain, 'MX')
        return sorted([(r.preference, str(r.exchange)) for r in records])
    except:
        return []

def verify_email_smtp(email: str, timeout: int = 5) -> dict:
    result = {
        'email': email,
        'valid_format': False,
        'domain_exists': False,
        'mx_exists': False,
        'smtp_verified': False,
        'status': 'unknown',
        'message': ''
    }
    if not email or '@' not in email:
        result['status'] = 'invalid'
        result['message'] = 'Invalid email format'
        return result
    result['valid_format'] = True
    local_part, domain = email.split('@')
    if not re.match(r'^[a-zA-Z0-9._%+-]+$', local_part):
        result['status'] = 'invalid'
        result['message'] = 'Invalid local part'
        return result
    try:
        socket.gethostbyname(domain)
        result['domain_exists'] = True
    except:
        result['status'] = 'invalid'
        result['message'] = 'Domain does not exist'
        return result
    mx_records = get_mx_records(domain)
    if not mx_records:
        result['status'] = 'invalid'
        result['message'] = 'No MX records found'
        return result
    result['mx_exists'] = True
    try:
        mx_host = str(mx_records[0][1]).rstrip('.')
        server = smtplib.SMTP(mx_host, timeout=timeout)
        server.set_debuglevel(0)
        server.ehlo_or_helo_if_needed()
        server.mail('verify@example.com')
        code, response = server.rcpt(email)
        server.quit()
        if code == 250:
            result['smtp_verified'] = True
            result['status'] = 'valid'
            result['message'] = 'Email exists'
        elif code == 550:
            result['status'] = 'invalid'
            result['message'] = 'Email does not exist'
        else:
            result['status'] = 'unknown'
            result['message'] = f'SMTP response: {code}'
    except smtplib.SMTPServerDisconnected:
        result['status'] = 'unknown'
        result['message'] = 'SMTP server disconnected'
    except smtplib.SMTPConnectError:
        result['status'] = 'unknown'
        result['message'] = 'Could not connect to SMTP server'
    except smtplib.SMTPException as e:
        result['status'] = 'unknown'
        result['message'] = f'SMTP error: {str(e)}'
    except Exception as e:
        result['status'] = 'unknown'
        result['message'] = f'Error: {str(e)}'
    return result

def batch_verify_emails(emails: list, max_workers: int = 5) -> dict:
    results = {}
    total = len([e for e in emails if e])
    if total == 0:
        return results
    log.subheader(f"Verifying {total} emails...")
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_email = {
            executor.submit(verify_email_smtp, email): email
            for email in emails if email
        }
        completed = 0
        for future in as_completed(future_to_email):
            email = future_to_email[future]
            try:
                result = future.result()
                results[email] = result
                completed += 1
                if result['status'] == 'valid':
                    status_str = colored("VALID", Colors.BRIGHT_GREEN, bold=True)
                elif result['status'] == 'invalid':
                    status_str = colored("INVALID", Colors.BRIGHT_RED, bold=True)
                else:
                    status_str = colored("UNKNOWN", Colors.BRIGHT_YELLOW, bold=True)
                print(colored(f"  [{completed}/{total}] ", Colors.BRIGHT_BLACK) + 
                      colored(email, Colors.BRIGHT_WHITE) + 
                      f"  {status_str}")
            except Exception as e:
                results[email] = {
                    'email': email,
                    'status': 'unknown',
                    'message': str(e)
                }
                completed += 1
                print(colored(f"  [{completed}/{total}] ", Colors.BRIGHT_BLACK) + 
                      colored(email, Colors.BRIGHT_WHITE) + 
                      f"  {colored('ERROR', Colors.BRIGHT_RED)}")
    return results

def read_list_page_with_emails(page) -> list[dict]:
    """Google Scholar sayfasından araştırmacı bilgilerini çeker"""
    cards = page.evaluate("""
        () => {
            // Türkçe karakter dönüşümü için yardımcı fonksiyon
            function cleanTurkish(text) {
                if (!text) return text;
                const map = {
                    'ç': 'c', 'Ç': 'C',
                    'ğ': 'g', 'Ğ': 'G',
                    'ı': 'i', 'İ': 'I',
                    'ö': 'o', 'Ö': 'O',
                    'ş': 's', 'Ş': 'S',
                    'ü': 'u', 'Ü': 'U'
                };
                return text.replace(/[çÇğĞıİöÖşŞüÜ]/g, function(match) {
                    return map[match] || match;
                });
            }
            
            return Array.from(document.querySelectorAll('.gsc_1usr')).map(card => {
                const name_el = card.querySelector('.gs_ai_name');
                const inst_el = card.querySelector('.gs_ai_aff');
                const cit_el = card.querySelector('.gs_ai_cby');
                const link_el = card.querySelector('.gs_ai_name a');
                const interest_els = card.querySelectorAll('.gs_ai_one_int');
                const card_text = card.innerText;
                
                // 1. Direkt email formatında ara (örn: adil.denizli@hacettepe.edu.tr)
                let email = '';
                const email_match = card_text.match(/[\\w.+\\-]+@[\\w\\-]+\\.[\\w.]+/);
                if (email_match) {
                    email = email_match[0];
                }
                
                // 2. Domain'i ara - "hacettepe.edu.tr üzerinde doğrulanmış" veya "verified email on"
                let domain = null;
                const domain_patterns = [
                    // Türkçe: "hacettepe.edu.tr üzerinde doğrulanmış e-posta adresine sahip"
                    /([\\w\\-]+\\.\\w+(?:\\.\\w+)?)\\s+üzerinde\\s+doğrulanmış/i,
                    // Türkçe: "hacettepe.edu.tr üzerinden doğrulanmış"
                    /([\\w\\-]+\\.\\w+(?:\\.\\w+)?)\\s+üzerinden\\s+doğrulanmış/i,
                    // İngilizce: "verified email on hacettepe.edu.tr"
                    /verified\\s+email\\s+(?:on|at)\\s+([\\w\\-]+\\.\\w+(?:\\.\\w+)?)/i,
                    // İngilizce: "email verified on hacettepe.edu.tr"
                    /email\\s+verified\\s+(?:on|at)\\s+([\\w\\-]+\\.\\w+(?:\\.\\w+)?)/i,
                    // Genel domain yakalama
                    /([\\w\\-]+\\.\\w+(?:\\.\\w+)?)\\s+(?:üzerinde|üzerinden|on|at)/i
                ];
                
                for (const pattern of domain_patterns) {
                    const match = card_text.match(pattern);
                    if (match) {
                        domain = match[1];
                        break;
                    }
                }
                
                // 3. Eğer email yoksa ve domain varsa, isimden email oluştur
                if (!email && domain) {
                    const name = name_el ? name_el.innerText.trim() : '';
                    if (name) {
                        // Türkçe karakterleri dönüştür ve temizle
                        const clean = cleanTurkish(name.toLowerCase())
                            .replace(/[^a-z\\s]/g, '')
                            .replace(/\\s+/g, ' ')
                            .trim();
                        
                        const parts = clean.split(' ');
                        if (parts.length >= 2) {
                            // İsim.soyisim@domain
                            email = parts[0] + '.' + parts[parts.length-1] + '@' + domain;
                        } else if (parts.length === 1) {
                            email = parts[0] + '@' + domain;
                        }
                    }
                }
                
                // 4. ORCID ara
                let orcid = '';
                const orcid_match = card_text.match(/orcid\\.org\\/(\\d{4}-\\d{4}-\\d{4}-\\d{3}[\\dX])/i);
                if (orcid_match) {
                    orcid = orcid_match[1];
                }
                
                return {
                    name:   name_el  ? name_el.innerText.trim()  : '',
                    institution:  inst_el ? inst_el.innerText.trim() : '',
                    citations: cit_el  ? cit_el.innerText.trim()  : '0',
                    href:   link_el  ? link_el.getAttribute('href') : '',
                    interests: Array.from(interest_els).map(e => e.innerText.trim()),
                    email: email,
                    orcid: orcid
                };
            });
        }
    """)
    return cards or []

def check_block(page, query, max_results, headless) -> bool:
    current = page.url
    html = page.content()
    if "accounts.google.com" in current:
        if not headless:
            log.warning("Login required. Please login and press ENTER.")
            input(colored("Press ENTER after login... ", Colors.BRIGHT_YELLOW, bold=True))
            updated = page.context.cookies()
            COOKIE_FILE.write_text(json.dumps(updated, ensure_ascii=False, indent=2), encoding="utf-8")
            log.success(f"Cookies updated ({len(updated)} items)")
            return True
        else:
            log.error("Login redirect! Run with --visible to login manually.")
            log.info("  1) python netschlr.py --save-cookies")
            return False
    if "sorry/index" in current or "unusual traffic" in html.lower():
        if not headless:
            log.warning("CAPTCHA detected! Please solve it.")
            input(colored("Press ENTER after solving CAPTCHA... ", Colors.BRIGHT_YELLOW, bold=True))
            return True
        else:
            log.error("CAPTCHA detected! Run with --visible to solve.")
            return False
    return True

def search_osint(page, name: str, institution: str = "") -> dict:
    result = {
        'linkedin': '', 'twitter': '', 'researchgate': '', 'academia': '',
        'github': '', 'orcid': '', 'publons': '', 'medium': '',
        'stackoverflow': '', 'facebook': '', 'instagram': '',
        'youtube': '', 'tiktok': '', 'pinterest': '', 'reddit': '',
        'quora': '', 'goodreads': '', 'personal_website': ''
    }
    username = generate_username(name)
    clean_name = re.sub(r'[^a-zA-Z\s]', '', name).strip().replace(' ', '+')
    try:
        search_url = f"https://www.google.com/search?q=%22{clean_name}%22+%22{institution}%22+site:orcid.org"
        page.goto(search_url, wait_until='domcontentloaded', timeout=10000)
        time.sleep(0.5)
        content = page.content()
        orcid_matches = re.findall(r'orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])', content)
        if orcid_matches:
            result['orcid'] = f"https://orcid.org/{orcid_matches[0]}"
    except:
        pass
    for platform, base_url in OSINT_PLATFORMS.items():
        if platform == 'personal_website':
            continue
        if platform == 'orcid':
            continue
        try:
            if platform == 'linkedin':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'twitter':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'researchgate':
                test_url = f"{base_url}{username.replace('.', '-')}"
            elif platform == 'academia':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'github':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'publons':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'medium':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'stackoverflow':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'facebook':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'instagram':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'youtube':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'tiktok':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'pinterest':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'reddit':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'quora':
                test_url = f"{base_url}{username.replace('.', '')}"
            elif platform == 'goodreads':
                test_url = f"{base_url}{username.replace('.', '')}"
            else:
                continue
            if check_url_exists(page, test_url):
                result[platform] = test_url
        except:
            pass
    try:
        search_url = f"https://www.google.com/search?q=%22{clean_name}%22+%22{institution}%22+%22homepage%22+OR+%22personal+website%22"
        page.goto(search_url, wait_until='domcontentloaded', timeout=10000)
        time.sleep(0.5)
        content = page.content()
        url_matches = re.findall(r'https?://[^\s<>"\'"]+', content)
        for url in url_matches:
            if any(x in url for x in ['linkedin', 'twitter', 'facebook', 'instagram']):
                continue
            if len(url) > 20 and len(url) < 100:
                result['personal_website'] = url
                break
    except:
        pass
    return result

def scrape(query: str, max_results: int, headless: bool, own_email: str = "", enable_osint: bool = False, verify_emails: bool = False, progress_callback=None):
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    cookies = None
    if COOKIE_FILE.exists():
        cookies = json.loads(COOKIE_FILE.read_text(encoding="utf-8"))
        log.success(f"Loaded {len(cookies)} cookies")
    else:
        log.warning("No cookies found! Run --save-cookies first.")
    results = []
    all_emails = set()
    page_no = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=CHROME_UA,
            locale="tr-TR",
            timezone_id="Europe/Istanbul",
        )
        ctx.add_init_script(BOT_JS)
        if cookies:
            ctx.add_cookies(cookies)
        page = ctx.new_page()
        list_url = (
            "https://scholar.google.com/citations"
            f"?hl=tr&view_op=search_authors"
            f"&mauthors={query}"
        )
        log.search(f"Search URL: {list_url}")
        while len(results) < max_results:
            log.subheader(f"Page {page_no + 1}")
            try:
                if page_no == 0:
                    page.goto(list_url, wait_until="domcontentloaded", timeout=25000)
                else:
                    next_button = page.query_selector('button.gs_btnPR:not([disabled])')
                    if not next_button:
                        next_button = page.query_selector('button:has-text("Ileri")')
                    if not next_button:
                        next_button = page.query_selector('button[aria-label*="Next"], button[aria-label*="Ileri"]')
                    if not next_button:
                        log.info("No more pages available.")
                        break
                    log.info("Navigating to next page...")
                    next_button.click()
                    time.sleep(random.uniform(2.0, 4.0))
                    page.wait_for_selector('.gsc_1usr', timeout=15000)
                time.sleep(random.uniform(1.5, 3.0))
            except PWTimeout:
                log.error("Page load timeout!")
                break
            except Exception as e:
                log.error(f"Navigation error: {e}")
                break
            if not check_block(page, query, max_results, headless):
                break
            raw_list = read_list_page_with_emails(page)
            if not raw_list:
                log.info("No results on this page.")
                break
            log.info(f"Found {len(raw_list)} researchers on page {page_no + 1}")
            for raw in raw_list:
                if len(results) >= max_results:
                    break
                name = raw.get("name", "")
                institution = raw.get("institution", "")
                citations = int("".join(filter(str.isdigit, raw.get("citations", "0"))) or 0)
                interests = ", ".join(raw.get("interests", []))
                href = raw.get("href", "")
                profile_url = ("https://scholar.google.com" + href) if href.startswith("/") else href
                orcid = raw.get("orcid", "")
                email = raw.get("email", "")
                
                # Eğer email system email ise veya own_email ile aynıysa temizle
                if email and is_system_email(email):
                    email = ""
                if email and email in all_emails:
                    continue
                if email:
                    all_emails.add(email)
                if own_email and email and email.lower() == own_email.lower():
                    email = ""
                
                # Email oluşturulmuşsa veya bulunmuşsa verified true
                verified = True if email else False
                
                result_dict = {
                    "Name": name,
                    "Email": email,
                    "Verified": "Yes" if verified else "No",
                    "Institution": institution,
                    "Interests": interests,
                    "Citations": citations,
                    "Profile URL": profile_url,
                    "ORCID": orcid,
                    "Email_Status": "",
                    "Email_Valid": "",
                    "Email_Message": ""
                }
                if enable_osint:
                    log.osint(f"[{len(results)+1}/{max_results}] {name} - scanning...")
                    osint_data = search_osint(page, name, institution)
                    result_dict.update({
                        "LinkedIn": osint_data.get('linkedin', ''),
                        "Twitter": osint_data.get('twitter', ''),
                        "ResearchGate": osint_data.get('researchgate', ''),
                        "Academia": osint_data.get('academia', ''),
                        "GitHub": osint_data.get('github', ''),
                        "ORCID_URL": osint_data.get('orcid', '') or orcid,
                        "Publons": osint_data.get('publons', ''),
                        "Medium": osint_data.get('medium', ''),
                        "StackOverflow": osint_data.get('stackoverflow', ''),
                        "Facebook": osint_data.get('facebook', ''),
                        "Instagram": osint_data.get('instagram', ''),
                        "YouTube": osint_data.get('youtube', ''),
                        "TikTok": osint_data.get('tiktok', ''),
                        "Pinterest": osint_data.get('pinterest', ''),
                        "Reddit": osint_data.get('reddit', ''),
                        "Quora": osint_data.get('quora', ''),
                        "Goodreads": osint_data.get('goodreads', ''),
                        "Personal_Website": osint_data.get('personal_website', '')
                    })
                    found_links = []
                    if osint_data.get('linkedin'):
                        found_links.append("LinkedIn")
                    if osint_data.get('github'):
                        found_links.append("GitHub")
                    if osint_data.get('researchgate'):
                        found_links.append("ResearchGate")
                    if osint_data.get('orcid'):
                        found_links.append("ORCID")
                    if found_links:
                        log.success(f"    Found: {', '.join(found_links)}")
                else:
                    # Email durumunu göster
                    if email:
                        domain = email.split('@')[1] if '@' in email else ''
                        status = colored(f"FOUND ({domain})", Colors.BRIGHT_GREEN)
                    else:
                        status = colored("NOT FOUND", Colors.BRIGHT_RED)
                    log.email(f"[{len(results)+1}/{max_results}] {name}  <{email}>  {status}")
                results.append(result_dict)
                if progress_callback:
                    progress_callback(len(results), max_results)
            if len(results) >= max_results:
                log.success(f"Reached target: {max_results} researchers")
                break
            page_no += 1
        browser.close()
    if verify_emails and all_emails:
        log.header("EMAIL VERIFICATION")
        verification_results = batch_verify_emails(list(all_emails))
        for row in results:
            email = row.get('Email', '')
            if email and email in verification_results:
                ver = verification_results[email]
                status = ver.get('status', 'unknown')
                row['Email_Status'] = status
                row['Email_Message'] = ver.get('message', '')
                if status == 'valid' or status == 'unknown':
                    row['Email_Valid'] = 'Yes'
                else:
                    row['Email_Valid'] = 'No'
    log.success(f"Scraping complete! {len(results)} researchers, {len(all_emails)} unique emails")
    return results

def save_csv(data, filename):
    import pandas as pd
    if not data:
        log.warning("No data to save.")
        return
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    log.save(f"Saved to: {filename}")
    total = len(df)
    emails = len(df[df['Email'] != ''])
    if 'Email_Valid' in df.columns:
        valid = len(df[df['Email_Valid'] == 'Yes'])
        invalid = len(df[df['Email_Valid'] == 'No'])
        log.info(f"  Total: {total}  |  Emails: {emails}  |  Valid: {valid}  |  Invalid: {invalid}")
    else:
        log.info(f"  Total: {total}  |  Emails: {emails}")

def print_banner():
    banner = colored("""
    NetSchlr v1.0
    Academic Email Extractor
    OSINT + Verification
    """, Colors.BRIGHT_CYAN, bold=True)
    print(banner)
    print()

def get_input(prompt: str, default: str = "", required: bool = False) -> str:
    if default:
        prompt = f"{prompt} [{default}]"
    prompt += ": "
    while True:
        value = input(colored(prompt, Colors.BRIGHT_WHITE, bold=True)).strip()
        if value:
            return value
        if default:
            return default
        if not required:
            return ""
        log.error("This field is required.")

def get_yes_no(prompt: str, default: bool = True) -> bool:
    default_text = "Y/n" if default else "y/N"
    value = input(colored(f"{prompt} ({default_text}): ", Colors.BRIGHT_WHITE, bold=True)).strip().lower()
    if not value:
        return default
    return value in ['y', 'yes', 'evet', 'e', 't']

def run_osint_only():
    log.header("OSINT ONLY MODE")
    csv_files = list(SAVED_DIR.glob("*.csv"))
    if csv_files:
        log.info("Found CSV files:")
        for i, f in enumerate(csv_files, 1):
            print(f"  {i}. {colored(f.name, Colors.BRIGHT_WHITE)}")
        print(f"  {len(csv_files)+1}. {colored('Enter custom path', Colors.BRIGHT_YELLOW)}")
        choice = input(colored(f"\nSelect file (1-{len(csv_files)+1}): ", Colors.BRIGHT_WHITE, bold=True)).strip()
        try:
            idx = int(choice) - 1
            if idx < len(csv_files):
                input_file = csv_files[idx]
            else:
                input_file = Path(get_input("Enter CSV file path", required=True))
        except:
            input_file = Path(get_input("Enter CSV file path", required=True))
    else:
        log.warning("No CSV files found in saved/ directory.")
        input_file = Path(get_input("Enter CSV file path", required=True))
    if not input_file.exists():
        log.error(f"File not found: {input_file}")
        return
    filename = get_input("Output filename (without extension)", f"osint_{input_file.stem}")
    if not filename:
        filename = f"osint_{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_file = SAVED_DIR / f"{filename}.csv"
    visible = get_yes_no("Show browser window", True)
    import pandas as pd
    log.info(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    results = df.to_dict('records')
    log.search(f"Running OSINT on {len(results)} researchers...")
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not visible)
        ctx = browser.new_context()
        page = ctx.new_page()
        for i, row in enumerate(results):
            name = row.get('Name', '')
            institution = row.get('Institution', '')
            if not name:
                continue
            log.osint(f"[{i+1}/{len(results)}] {name} - scanning...")
            osint_data = search_osint(page, name, institution)
            row['LinkedIn'] = osint_data.get('linkedin', '')
            row['Twitter'] = osint_data.get('twitter', '')
            row['ResearchGate'] = osint_data.get('researchgate', '')
            row['Academia'] = osint_data.get('academia', '')
            row['GitHub'] = osint_data.get('github', '')
            row['ORCID_URL'] = osint_data.get('orcid', '') or row.get('ORCID', '')
            row['Publons'] = osint_data.get('publons', '')
            row['Medium'] = osint_data.get('medium', '')
            row['StackOverflow'] = osint_data.get('stackoverflow', '')
            row['Facebook'] = osint_data.get('facebook', '')
            row['Instagram'] = osint_data.get('instagram', '')
            row['YouTube'] = osint_data.get('youtube', '')
            row['TikTok'] = osint_data.get('tiktok', '')
            row['Pinterest'] = osint_data.get('pinterest', '')
            row['Reddit'] = osint_data.get('reddit', '')
            row['Quora'] = osint_data.get('quora', '')
            row['Goodreads'] = osint_data.get('goodreads', '')
            row['Personal_Website'] = osint_data.get('personal_website', '')
            found_links = []
            if osint_data.get('linkedin'):
                found_links.append("LinkedIn")
            if osint_data.get('github'):
                found_links.append("GitHub")
            if osint_data.get('researchgate'):
                found_links.append("ResearchGate")
            if osint_data.get('orcid'):
                found_links.append("ORCID")
            if found_links:
                log.success(f"    Found: {', '.join(found_links)}")
        browser.close()
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    log.success(f"OSINT results saved to: {output_file}")

def run_verify_only():
    log.header("EMAIL VERIFICATION ONLY")
    csv_files = list(SAVED_DIR.glob("*.csv"))
    if csv_files:
        log.info("Found CSV files:")
        for i, f in enumerate(csv_files, 1):
            print(f"  {i}. {colored(f.name, Colors.BRIGHT_WHITE)}")
        print(f"  {len(csv_files)+1}. {colored('Enter custom path', Colors.BRIGHT_YELLOW)}")
        choice = input(colored(f"\nSelect file (1-{len(csv_files)+1}): ", Colors.BRIGHT_WHITE, bold=True)).strip()
        try:
            idx = int(choice) - 1
            if idx < len(csv_files):
                input_file = csv_files[idx]
            else:
                input_file = Path(get_input("Enter CSV file path", required=True))
        except:
            input_file = Path(get_input("Enter CSV file path", required=True))
    else:
        log.warning("No CSV files found in saved/ directory.")
        input_file = Path(get_input("Enter CSV file path", required=True))
    if not input_file.exists():
        log.error(f"File not found: {input_file}")
        return
    filename = get_input("Output filename (without extension)", f"verified_{input_file.stem}")
    if not filename:
        filename = f"verified_{input_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    output_file = SAVED_DIR / f"{filename}.csv"
    import pandas as pd
    log.info(f"Loading data from: {input_file}")
    df = pd.read_csv(input_file)
    results = df.to_dict('records')
    emails = [r.get('Email', '') for r in results if r.get('Email', '')]
    if not emails:
        log.warning("No emails found in the file.")
        return
    verification_results = batch_verify_emails(emails)
    for row in results:
        email = row.get('Email', '')
        if email and email in verification_results:
            ver = verification_results[email]
            status = ver.get('status', 'unknown')
            row['Email_Status'] = status
            row['Email_Message'] = ver.get('message', '')
            if status == 'valid' or status == 'unknown':
                row['Email_Valid'] = 'Yes'
            else:
                row['Email_Valid'] = 'No'
    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    log.header("VERIFICATION SUMMARY")
    valid = len(df[df['Email_Valid'] == 'Yes'])
    invalid = len(df[df['Email_Valid'] == 'No'])
    log.success(f"Valid emails (including unknown): {valid}")
    log.error(f"Invalid emails: {invalid}")
    log.save(f"Saved to: {output_file}")

def main_interactive():
    print_banner()
    log.header("MAIN MENU")
    print(f"  {colored('1.', Colors.BRIGHT_YELLOW)} {colored('Search researchers (new)', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('2.', Colors.BRIGHT_YELLOW)} {colored('OSINT only (existing CSV)', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('3.', Colors.BRIGHT_YELLOW)} {colored('Verify emails only (existing CSV)', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('4.', Colors.BRIGHT_YELLOW)} {colored('Save cookies (first time use)', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('5.', Colors.BRIGHT_YELLOW)} {colored('Exit', Colors.BRIGHT_WHITE)}")
    print()
    choice = input(colored("Select option (1-5): ", Colors.BRIGHT_WHITE, bold=True)).strip()
    if choice == "4":
        save_cookies()
        return
    elif choice == "5":
        log.info("Goodbye!")
        sys.exit(0)
        return
    elif choice == "2":
        run_osint_only()
        return
    elif choice == "3":
        run_verify_only()
        return
    log.header("SEARCH CONFIGURATION")
    query = get_input("Search query", "kimya", required=True)
    try:
        max_results = int(get_input("Max results", "100"))
    except:
        max_results = 100
    
    # Browser gösterme: default YES
    visible = get_yes_no("Show browser window", True)
    
    # OSINT: default NO
    enable_osint = get_yes_no("Enable OSINT scanning (LinkedIn, GitHub, etc.)", False)
    
    # Email verification: default NO
    verify = get_yes_no("Verify emails (SMTP check - slower)", False)
    
    filename = get_input("Output filename (without extension)", f"scholar_{query.replace(' ', '_')[:20]}")
    if not filename:
        filename = f"scholar_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = SAVED_DIR / f"{filename}_{timestamp}.csv"
    log.header("SUMMARY")
    print(f"  {colored('Query:', Colors.BRIGHT_BLACK)} {colored(query, Colors.BRIGHT_WHITE)}")
    print(f"  {colored('Max results:', Colors.BRIGHT_BLACK)} {colored(str(max_results), Colors.BRIGHT_WHITE)}")
    print(f"  {colored('Visible:', Colors.BRIGHT_BLACK)} {colored('Yes' if visible else 'No', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('OSINT:', Colors.BRIGHT_BLACK)} {colored('Yes' if enable_osint else 'No', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('Verify:', Colors.BRIGHT_BLACK)} {colored('Yes' if verify else 'No', Colors.BRIGHT_WHITE)}")
    print(f"  {colored('Output:', Colors.BRIGHT_BLACK)} {colored(str(output_file), Colors.BRIGHT_CYAN)}")
    print()
    confirm = get_yes_no("Start scraping", True)
    if not confirm:
        log.info("Cancelled.")
        return
    data = scrape(
        query=query,
        max_results=max_results,
        headless=not visible,
        own_email="",
        enable_osint=enable_osint,
        verify_emails=verify,
    )
    if data:
        save_csv(data, output_file)
        log.header("FINAL SUMMARY")
        emails_found = sum(1 for r in data if r.get('Email', ''))
        verified = sum(1 for r in data if r.get('Verified', 'No') == 'Yes')
        print(f"  {colored('Total researchers:', Colors.BRIGHT_BLACK)} {colored(str(len(data)), Colors.BRIGHT_WHITE)}")
        print(f"  {colored('Emails found:', Colors.BRIGHT_BLACK)} {colored(str(emails_found), Colors.BRIGHT_GREEN)}")
        print(f"  {colored('Verified (Scholar):', Colors.BRIGHT_BLACK)} {colored(str(verified), Colors.BRIGHT_GREEN)}")
        if verify:
            valid = sum(1 for r in data if r.get('Email_Valid', '') == 'Yes')
            invalid = sum(1 for r in data if r.get('Email_Valid', '') == 'No')
            print(f"  {colored('Valid (SMTP):', Colors.BRIGHT_BLACK)} {colored(str(valid), Colors.BRIGHT_GREEN)}")
            print(f"  {colored('Invalid (SMTP):', Colors.BRIGHT_BLACK)} {colored(str(invalid), Colors.BRIGHT_RED)}")
        if enable_osint:
            linkedin = sum(1 for r in data if r.get('LinkedIn', ''))
            github = sum(1 for r in data if r.get('GitHub', ''))
            researchgate = sum(1 for r in data if r.get('ResearchGate', ''))
            orcid = sum(1 for r in data if r.get('ORCID_URL', ''))
            print(f"  {colored('LinkedIn:', Colors.BRIGHT_BLACK)} {colored(str(linkedin), Colors.BRIGHT_CYAN)}")
            print(f"  {colored('GitHub:', Colors.BRIGHT_BLACK)} {colored(str(github), Colors.BRIGHT_CYAN)}")
            print(f"  {colored('ResearchGate:', Colors.BRIGHT_BLACK)} {colored(str(researchgate), Colors.BRIGHT_CYAN)}")
            print(f"  {colored('ORCID:', Colors.BRIGHT_BLACK)} {colored(str(orcid), Colors.BRIGHT_CYAN)}")
        log.save(f"Saved to: {output_file}")
    else:
        log.warning("No data collected.")

def main():
    try:
        check_dependencies()
        main_interactive()
    except KeyboardInterrupt:
        print()
        log.warning("Cancelled by user.")
        sys.exit(0)
    except Exception as e:
        log.error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
