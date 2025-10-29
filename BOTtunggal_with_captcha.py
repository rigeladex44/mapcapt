# -*- coding: utf-8 -*-
"""
BOT1.py — Versi MANUAL-ONLY (via tombol) + CAPTCHA SUPPORT
- Tidak ada preset credential; semua login pakai tombol LOGIN lalu kirim "email|pin"
- Tambah NIK via tombol INPUT NIK lalu kirim list NIK (multi-baris)
- Tombol lain: STOP, CEK STOK, DEL (hapus antrean), STATUS
- CAPTCHA: Manual solving via notifikasi Telegram
"""
import os
import re
import time
import threading
import json
import sys
import logging
import traceback
from pathlib import Path

import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout

# ===================== LOGGING =====================
def setup_logging():
    script_name = Path(__file__).stem
    log_file = f"{script_name}.log"
    if logging.getLogger().hasHandlers():
        logging.getLogger().handlers.clear()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[logging.FileHandler(log_file, mode='a', encoding='utf-8'),
                  logging.StreamHandler(sys.stdout)]
    )
    logging.info(f"Logging dimulai untuk {script_name}")
setup_logging()

# ===================== ENV & KONFIG =====================
SCRIPT_NAME = Path(__file__).stem
ENV_FILE = os.getenv("ENV_FILE") or f"{SCRIPT_NAME}.env"

def _clean(s: str) -> str:
    return (s or "").strip().strip('"').strip("'")

try:
    if not Path(ENV_FILE).exists():
        raise FileNotFoundError(f"File env '{ENV_FILE}' tidak ditemukan.")
    load_dotenv(ENV_FILE, override=True)
    BOT_TOKEN = _clean(os.getenv("BOT_TOKEN", ""))
    ALLOWED_CHAT_ID = _clean(os.getenv("ALLOWED_CHAT_ID", ""))
    HEADLESS = _clean(os.getenv("HEADLESS", "1")).lower() not in ("0", "false", "no")
    
    # OPSI BARU: Timeout maksimal untuk menunggu CAPTCHA diselesaikan (detik)
    CAPTCHA_TIMEOUT = int(_clean(os.getenv("CAPTCHA_TIMEOUT", "120")))
    
    if not BOT_TOKEN: raise ValueError("BOT_TOKEN belum di-set di env")
    if not ALLOWED_CHAT_ID: raise ValueError("ALLOWED_CHAT_ID belum di-set di env")
except (FileNotFoundError, ValueError) as e:
    logging.critical(f"Error konfigurasi fatal: {e}")
    sys.exit(1)

mnum = re.search(r"(\d+)$", SCRIPT_NAME)
BOT_NUM = mnum.group(1) if mnum else ""
NIK_FILE = Path(os.getenv("NIK_FILE") or (f"nik{BOT_NUM}.txt" if BOT_NUM else f"nik_{SCRIPT_NAME}.txt"))
BASE_URL = "https://subsiditepatlpg.mypertamina.id"
QUEUE_FILE = NIK_FILE.with_suffix(".queue")
CEK_FLAG = Path(f"cek_{SCRIPT_NAME}.flag")
CAPTCHA_FLAG = Path(f"captcha_solved_{SCRIPT_NAME}.flag")

# ===================== STATE GLOBAL =====================
RUN_EVENT = threading.Event()
NAMA_PANGKALAN = ""
LAST_UPDATE_ID = None
LOGIN_EMAIL = ""
LOGIN_PIN = ""
WAITING_CRED = False
WAITING_NIK = False
WAITING_CAPTCHA = False
CURRENT_NIK_PROCESSING = ""

# ===================== TELEGRAM =====================
def tg_send(text: str):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": ALLOWED_CHAT_ID, "text": text},
            timeout=20,
        )
    except Exception as e:
        logging.warning(f"Gagal kirim TG: {e}")

def tg_send_menu(text: str, html: bool = False, per_row: int = 3):
    rows = [
        [{"text": "LOGIN"}, {"text": "STOP"}],
        [{"text": "CEK STOK"}, {"text": "HAPUS"}],
        [{"text": "STATUS"}, {"text": "INPUT NIK"}],
        [{"text": "CAPTCHA DONE"}],  # Tombol baru untuk konfirmasi CAPTCHA
    ]
    kb = {
        "keyboard": rows,
        "resize_keyboard": True,
        "is_persistent": True,
        "one_time_keyboard": False,
        "input_field_placeholder": "HENGKYY GANTENG...!",
    }
    payload = {"chat_id": ALLOWED_CHAT_ID, "reply_markup": json.dumps(kb), "text": text}
    if html:
        payload["parse_mode"] = "HTML"; payload["disable_web_page_preview"] = True
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=payload, timeout=20)
    except Exception as e:
        logging.warning(f"Gagal kirim menu TG: {e}")

def ensure_token_ok():
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
                     params={"drop_pending_updates": True}, timeout=10)
    except Exception:
        pass
    r = requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/getMe", timeout=10)
    if not (r.ok and r.json().get("ok")):
        raise ConnectionError(f"TOKEN invalid: {r.text}")

# ===================== UTIL FILE =====================
def read_lines(p: Path) -> list[str]:
    if not p.exists(): return []
    try:
        return [ln.strip() for ln in p.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except Exception as e:
        logging.error(f"Gagal membaca file {p}: {e}"); return []

def write_lines(p: Path, lines: list[str]):
    try:
        p.write_text(("\n".join(lines) + ("\n" if lines else "")), encoding="utf-8")
    except Exception as e:
        logging.error(f"Gagal menulis ke file {p}: {e}")

def parse_credential_line(s:str):
    parts = s.split("|",1)
    if len(parts)!=2: return None,None
    email, pin = parts[0].strip(), parts[1].strip()
    return (email,pin) if (email and pin) else (None,None)

def reset_state():
    global NAMA_PANGKALAN, LOGIN_EMAIL, LOGIN_PIN, WAITING_CRED, WAITING_NIK, WAITING_CAPTCHA, CURRENT_NIK_PROCESSING
    logging.info("Resetting bot state...")
    RUN_EVENT.clear()
    NAMA_PANGKALAN = ""
    LOGIN_EMAIL = ""
    LOGIN_PIN = ""
    WAITING_CRED = False
    WAITING_NIK = False
    WAITING_CAPTCHA = False
    CURRENT_NIK_PROCESSING = ""
    CAPTCHA_FLAG.unlink(missing_ok=True)

# ===================== CAPTCHA HANDLER =====================
def wait_for_captcha_solution(page, nik: str, idx: int) -> bool:
    """
    Fungsi untuk menunggu user menyelesaikan CAPTCHA via Telegram.
    Returns True jika CAPTCHA berhasil diselesaikan, False jika timeout/gagal.
    """
    global WAITING_CAPTCHA, CURRENT_NIK_PROCESSING
    
    try:
        # Cek apakah ada CAPTCHA di halaman
        captcha_selectors = [
            "[class*='captcha']",
            "[id*='captcha']",
            "canvas[class*='captcha']",
            ".slide-verify",
            ".slider-verify",
            "text=/.*captcha.*/i",
            "text=/.*verifikasi.*/i",
        ]
        
        captcha_found = False
        for selector in captcha_selectors:
            try:
                if page.locator(selector).first.is_visible(timeout=2000):
                    captcha_found = True
                    logging.info(f"CAPTCHA terdeteksi dengan selector: {selector}")
                    break
            except:
                continue
        
        if not captcha_found:
            logging.info("Tidak ada CAPTCHA terdeteksi, lanjut proses.")
            return True
        
        # Jika ada CAPTCHA, minta user solve
        WAITING_CAPTCHA = True
        CURRENT_NIK_PROCESSING = nik
        CAPTCHA_FLAG.unlink(missing_ok=True)
        
        # Kirim notifikasi ke Telegram
        tg_send_menu(
            f"🔐 CAPTCHA TERDETEKSI!\n"
            f"━━━━━━━━━━━━━━━━━\n"
            f"NIK #{idx}: {nik}\n\n"
            f"Silakan selesaikan CAPTCHA di browser,\n"
            f"lalu tekan tombol 'CAPTCHA DONE'\n\n"
            f"⏱️ Timeout: {CAPTCHA_TIMEOUT} detik"
        )
        
        # Tunggu flag dari user atau timeout
        start_time = time.time()
        while time.time() - start_time < CAPTCHA_TIMEOUT:
            if CAPTCHA_FLAG.exists():
                CAPTCHA_FLAG.unlink(missing_ok=True)
                WAITING_CAPTCHA = False
                logging.info(f"CAPTCHA berhasil diselesaikan untuk NIK {nik}")
                tg_send(f"✅ CAPTCHA solved! Melanjutkan NIK {nik}...")
                time.sleep(1)  # Beri waktu setelah CAPTCHA selesai
                return True
            
            if not RUN_EVENT.is_set():
                logging.warning("Bot dihentikan saat menunggu CAPTCHA")
                WAITING_CAPTCHA = False
                return False
            
            time.sleep(1)
        
        # Timeout
        WAITING_CAPTCHA = False
        logging.warning(f"Timeout menunggu CAPTCHA untuk NIK {nik}")
        tg_send(f"⏱️ Timeout CAPTCHA untuk NIK {nik}. Dilewati.")
        return False
        
    except Exception as e:
        WAITING_CAPTCHA = False
        logging.error(f"Error saat handle CAPTCHA: {e}")
        return False

# ===================== SITE HELPERS =====================
def kembali_ke_beranda(page):
    try:
        if "/verification-nik" in page.url and page.locator("[data-testid='btnCheckNik']").is_visible():
            return
        logging.info("Kembali ke beranda verifikasi NIK...")
        page.goto(f"{BASE_URL}/merchant/app/verification-nik", timeout=20000)
        page.wait_for_selector("[data-testid='btnCheckNik']", timeout=10000)
    except Exception:
        logging.warning("Gagal kembali ke beranda, mencoba refresh.")
        try: page.reload()
        except Exception: pass

def klik_masuk_robust(page):
    btn = page.get_by_role("button", name=re.compile(r"^\s*Masuk\s*$", re.I)).first
    btn.wait_for(state="visible", timeout=10000)
    try: btn.wait_for(state="enabled", timeout=5000)
    except Exception: pass
    try: btn.scroll_into_view_if_needed()
    except Exception: pass
    for _ in range(3):
        try:
            btn.click()
        except Exception:
            try: page.keyboard.press("Enter")
            except Exception: pass
            try: btn.click(force=True)
            except Exception: pass
        time.sleep(0.3)
        try:
            page.wait_for_selector(
                "[data-testid='btnCheckNik'], a[href*='/merchant/app/'], nav:has-text('Merchant')",
                timeout=1500
            )
            return
        except Exception:
            pass

def login_dengan_retry(page, email, pin):
    global NAMA_PANGKALAN
    for attempt in range(1, 4):
        try:
            logging.info(f"Percobaan login ke-{attempt} untuk {email}")
            page.goto(f"{BASE_URL}/merchant-login", timeout=30000)
        except Exception as e:
            logging.warning(f"Gagal membuka halaman login: {e}")
            continue
        
        page.get_by_role("textbox", name="Nomor ponsel atau email").fill(email)
        page.get_by_role("textbox", name="PIN").fill(pin); time.sleep(1.2)
        
        # CEK CAPTCHA SAAT LOGIN
        if not wait_for_captcha_solution(page, "LOGIN", 0):
            logging.warning("CAPTCHA login gagal/timeout")
            continue
        
        klik_masuk_robust(page)
        page.wait_for_selector("[data-testid='btnCheckNik']", timeout=15000)
        
        try:
            page.wait_for_timeout(2000)
            selectors = [
                "[data-testid*='nama']",
                ".merchant-name", 
                "text=/Pangkalan/",
                "text=/^[A-Z][A-Z\s]+$/",
            ]
            
            for selector in selectors:
                try:
                    element = page.locator(selector).first
                    if element.is_visible():
                        nama = element.inner_text()
                        if nama and len(nama.strip()) > 2:
                            NAMA_PANGKALAN = nama.strip()
                            kembali_ke_beranda(page)
                            tg_send_menu(f"✅ Login berhasil\nPangkalan: {NAMA_PANGKALAN}\nSiap memproses NIK…")
                            return True
                except Exception as e:
                    logging.warning(f"Gagal ambil nama pangkalan dengan selector {selector}: {e}")
            
            NAMA_PANGKALAN = email
            kembali_ke_beranda(page)
            tg_send_menu(f"✅ Login berhasil\nPangkalan: {NAMA_PANGKALAN}\nSiap memproses NIK…")
            return True
        except Exception as e:
            logging.warning(f"Exception saat mengambil nama pangkalan: {e}")
            return False
    tg_send("❌ Gagal login setelah 3x percobaan."); return False

def proses_nik(page, nik, idx) -> bool:
    """
    MODIFIKASI: Tambah CAPTCHA handling di setiap step yang mungkin ada CAPTCHA
    """
    try:
        page.get_by_role("combobox", name="Masukkan 16 digit NIK").fill(nik)
        
        # CEK CAPTCHA SETELAH ISI NIK (sebelum klik cek)
        if not wait_for_captcha_solution(page, nik, idx):
            tg_send(f"{idx}. {nik} ┆❌ CAPTCHA gagal/timeout")
            kembali_ke_beranda(page)
            return False
        
        page.get_by_test_id("btnCheckNik").click(); time.sleep(1.6)
        
        if page.locator("text=melebihi batas kewajaran pembelian LPG").is_visible():
            tg_send(f"{idx}. {nik} ┆❌ NIK Limit"); kembali_ke_beranda(page); return False
        
        if page.locator("text=Lanjut Transaksi").is_visible():
            # CEK CAPTCHA SEBELUM LANJUT TRANSAKSI
            if not wait_for_captcha_solution(page, nik, idx):
                tg_send(f"{idx}. {nik} ┆❌ CAPTCHA gagal/timeout")
                kembali_ke_beranda(page)
                return False
            
            page.get_by_role("button", name="Lanjut Transaksi").click(); time.sleep(1.5)
        
        if page.locator("text=stok tabung yang dapat dijual kosong").is_visible():
            tg_send("❌ Proses dihentikan — stok habis."); RUN_EVENT.clear(); return False
        
        page.wait_for_selector("[data-testid='actionIcon2']", timeout=10000)
        page.get_by_test_id("actionIcon2").click(); time.sleep(2)
        
        # CEK CAPTCHA SEBELUM CHECK ORDER
        if not wait_for_captcha_solution(page, nik, idx):
            tg_send(f"{idx}. {nik} ┆❌ CAPTCHA gagal/timeout")
            kembali_ke_beranda(page)
            return False
        
        page.get_by_test_id("btnCheckOrder").click(); time.sleep(1.5)
        
        # CEK CAPTCHA SEBELUM PAY
        if not wait_for_captcha_solution(page, nik, idx):
            tg_send(f"{idx}. {nik} ┆❌ CAPTCHA gagal/timeout")
            kembali_ke_beranda(page)
            return False
        
        page.get_by_test_id("btnPay").click(); time.sleep(2)
        
        if page.locator("text=Ke Beranda").is_visible():
            time.sleep(0.8); page.get_by_role("link", name="Ke Beranda").click()
        else:
            kembali_ke_beranda(page)
        
        tg_send(f"{idx}. {nik} ┆✅ Berhasil"); return True
        
    except Exception:
        logging.error(f"Error proses NIK {nik}:\n{traceback.format_exc()}")
        tg_send(f"{idx}. {nik} ┆❌ Gagal (submit)"); kembali_ke_beranda(page); return False
    finally:
        try:
            if page.locator("text=telah transaksi 10 NIK").is_visible():
                tg_send("☕️ Server butuh jeda 1 menit…"); time.sleep(60)
        except Exception:
            pass

def cek_stok(page):
    try:
        page.goto(f"{BASE_URL}/merchant/app/manage-product", timeout=20000); page.wait_for_timeout(1500)
        label = page.locator("text=Stok LPG 3kg saat ini").first
        if not label.is_visible(): raise Exception("Teks stok tidak ditemukan")
        stok = label.locator("xpath=..").locator("span").last.inner_text().strip()
        tg_send(f"⚠️ SISA STOK SAAT INI\n[{NAMA_PANGKALAN or 'Pangkalan'}]\n❯ {stok}")
    except Exception as e:
        logging.error(f"Gagal cek stok: {e}"); tg_send(f"Gagal cek stok: {e}")
    finally:
        kembali_ke_beranda(page)

# ===================== WORKER =====================
def worker_loop():
    global LOGIN_EMAIL, LOGIN_PIN
    while True:
        RUN_EVENT.wait()
        if not RUN_EVENT.is_set():
            continue

        logging.info("Worker aktif; membuka sesi Playwright…")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=HEADLESS)
                context = browser.new_context()
                page = context.new_page()
                try:
                    if not login_dengan_retry(page, LOGIN_EMAIL, LOGIN_PIN):
                        time.sleep(5); reset_state()
                        tg_send_menu("Login gagal. Bot di-reset.")
                        continue

                    while RUN_EVENT.is_set():
                        if CEK_FLAG.exists():
                            CEK_FLAG.unlink(missing_ok=True); cek_stok(page)

                        daftar = read_lines(QUEUE_FILE) if QUEUE_FILE.exists() else []
                        if not daftar:
                            incoming = read_lines(NIK_FILE)
                            if incoming:
                                logging.info(f"Memindahkan {len(incoming)} NIK ke antrean.")
                                try:
                                    NIK_FILE.replace(QUEUE_FILE)
                                except Exception:
                                    time.sleep(0.2)
                                    from shutil import copyfile
                                    copyfile(NIK_FILE, QUEUE_FILE)
                                    write_lines(NIK_FILE, [])
                                daftar = read_lines(QUEUE_FILE)

                        if daftar:
                            total_awal = len(daftar)
                            processed_ok, processed_fail = [], []
                            logging.info(f"Memproses {total_awal} NIK dari antrean…")

                            while RUN_EVENT.is_set() and daftar:
                                nik = daftar.pop(0)
                                idx = total_awal - len(daftar)

                                if 'login' in page.url:
                                    logging.warning("Sesi berakhir, login ulang…")
                                    if not login_dengan_retry(page, LOGIN_EMAIL, LOGIN_PIN):
                                        logging.error("Login ulang gagal; hentikan batch.")
                                        daftar.insert(0, nik); break

                                ok = proses_nik(page, nik, idx)
                                (processed_ok if ok else processed_fail).append(nik)
                                write_lines(QUEUE_FILE, daftar)
                                time.sleep(0.8)

                            if not daftar and QUEUE_FILE.exists():
                                QUEUE_FILE.unlink(missing_ok=True)
                                total = len(processed_ok) + len(processed_fail)
                                if total > 0:
                                    lines = [
                                        f"✅ [{NAMA_PANGKALAN}] NIK diproses",
                                        "━━━━━━━━━━━━━━━━━",
                                        f"Total   : {total}",
                                        f"Berhasil: {len(processed_ok)}",
                                        f"Gagal   : {len(processed_fail)}",
                                    ]
                                    if processed_fail:
                                        max_show = 30
                                        show = processed_fail[:max_show]
                                        lines.append("NIK gagal:")
                                        lines.extend([f"{i+1}. {n}" for i, n in enumerate(show)])
                                        if len(processed_fail) > max_show:
                                            lines.append(f"(+{len(processed_fail)-max_show} lainnya)")
                                    tg_send_menu("\n".join(lines))
                        time.sleep(1.5)

                except Exception:
                    logging.critical(f"ERROR KRITIS sesi browser:\n{traceback.format_exc()}")
                    tg_send("⚠️ Error serius, sesi dihentikan. Cek log.")
                    reset_state()
                finally:
                    try: context.close(); browser.close()
                    except Exception: pass

        except Exception:
            logging.critical(f"ERROR FATAL Playwright/Worker:\n{traceback.format_exc()}")
            tg_send("⚠️ Error fatal di worker. Bot di-reset.")
            reset_state()

# ===================== POLLING (TOMBOL MANUAL SAJA) =====================
HELP_TEXT = (
    "Hallo!:\n"
    "• Jangan di spam!\n"
    "\n"
    "Jika bot tidak respon atau eror\n"
    "Hubungi @rigeelm"
)

def normalize_cmd(s: str) -> str:
    s_strip = (s or "").strip()
    if s_strip.startswith("/"): return s_strip.lower()
    alias = {
        "login": "/login", "stop": "/stop",
        "cek": "/cek", "cek stok": "/cek",
        "hapus": "/del", "status": "/status",
        "input nik": "/nik",
        "captcha done": "/captcha_done",
        "done": "/captcha_done",
    }
    return alias.get(s_strip.lower(), s_strip)

def bot_polling_loop():
    global LAST_UPDATE_ID, WAITING_CRED, WAITING_NIK, LOGIN_EMAIL, LOGIN_PIN
    base = f"https://api.telegram.org/bot{BOT_TOKEN}"
    tg_send_menu(f"🤖 BOT MERCHANT APP ON!.\n{HELP_TEXT}")
    while True:
        try:
            r = requests.get(
                f"{base}/getUpdates",
                params={"timeout": 50, "offset": (LAST_UPDATE_ID + 1) if LAST_UPDATE_ID else None},
                timeout=60,
            )
            data = r.json() if 'application/json' in r.headers.get('content-type', '') else {}
            for upd in data.get("result", []):
                LAST_UPDATE_ID = upd.get("update_id", LAST_UPDATE_ID)
                msg = upd.get("message") or upd.get("edited_message") or {}
                text_raw = (msg.get("text") or "").strip()
                chat_id = str((msg.get("chat") or {}).get("id") or "")
                if chat_id != ALLOWED_CHAT_ID: continue

                text = normalize_cmd(text_raw)
                low = text.lower()

                # ——— CAPTCHA DONE ———
                if low in ("/captcha_done", "captcha done", "done"):
                    if WAITING_CAPTCHA:
                        CAPTCHA_FLAG.touch()
                        tg_send("✅ Konfirmasi CAPTCHA diterima!")
                    else:
                        tg_send("Tidak ada CAPTCHA yang sedang menunggu.")
                    continue

                # ——— Flow tunggu akun ———
                if WAITING_CRED and not low.startswith("/"):
                    em, pn = parse_credential_line(text_raw)
                    if em and pn:
                        LOGIN_EMAIL, LOGIN_PIN = em, pn
                        WAITING_CRED = False
                        tg_send("✅ Akun diterima.\nProses login…\n\nSABAAR!")
                        RUN_EVENT.set()
                    else:
                        tg_send("Format salah.\nKirim:\nemail|pin")
                    continue

                # ——— Flow tunggu NIK ———
                if WAITING_NIK and not low.startswith("/"):
                    lines = text_raw.splitlines()
                    nik_list = []
                    for ln in lines:
                        digits = "".join(c for c in ln if c.isdigit())
                        if len(digits) >= 12:
                            nik_list.append(digits)
                    if nik_list:
                        with NIK_FILE.open("a", encoding="utf-8") as f:
                            f.write("\n".join(nik_list) + "\n")
                        tg_send(f"✅ {len(nik_list)} NIK berhasil diinput..")
                    else:
                        tg_send("Tidak ada NIK valid yang ditemukan.")
                    WAITING_NIK = False
                    continue

                # ——— Tombol/alias ———
                if low in ("/start",):
                    tg_send_menu("Bot siap.\n" + HELP_TEXT)

                elif low in ("/login", "login"):
                    if RUN_EVENT.is_set():
                        tg_send_menu("Bot sedang berjalan. Tekan STOP dulu jika ingin ganti akun.")
                    else:
                        WAITING_CRED = True
                        tg_send_menu("Kirim akun:\nemail|pin")

                elif low in ("/stop", "stop"):
                    reset_state()
                    tg_send_menu("🚫 Bot dihentikan & semua sesi di-reset.")

                elif low in ("/del", "hapus"):
                    write_lines(NIK_FILE, [])
                    if QUEUE_FILE.exists(): QUEUE_FILE.unlink(missing_ok=True)
                    tg_send("📁 Data NIK & antrean dikosongkan.")

                elif low in ("/cek", "cek", "cek stok", "/cek stok"):
                    if RUN_EVENT.is_set():
                        CEK_FLAG.touch()
                        tg_send("🔃 Proses cek stok tabung…")
                    else:
                        tg_send("Bot tidak berjalan. LOGIN dulu.")

                elif low in ("/status", "status"):
                    antre_in, antre_q = len(read_lines(NIK_FILE)), len(read_lines(QUEUE_FILE))
                    status_text = 'RUN' if RUN_EVENT.is_set() else 'STOP'
                    captcha_status = f"⏳ Tunggu CAPTCHA ({CURRENT_NIK_PROCESSING})" if WAITING_CAPTCHA else "✓ Normal"
                    tg_send_menu(
                        f"Status BOT: {status_text}\n"
                        f"Pangkalan: {NAMA_PANGKALAN or 'Mbooh!'}\n"
                        f"Status NIK: {antre_in} Proses, {antre_q} Antri\n"
                        f"CAPTCHA: {captcha_status}\n\n"
                        f"SILAHKAN HAPUS DULU JIKA ADA NIK ANTRI!"
                    )

                elif low in ("/nik", "input nik"):
                    WAITING_NIK = True
                    tg_send_menu("📁Silahkan kirim NIK.\nContoh:\n3510xxxxxxxxxxxx\n3578xxxxxxxxxxxx")

                # ——— Shortcut: jika user langsung kirim email|pin ———
                elif "|" in text_raw and not low.startswith("/") and not RUN_EVENT.is_set():
                    em, pn = parse_credential_line(text_raw)
                    if em and pn:
                        LOGIN_EMAIL, LOGIN_PIN = em, pn
                        WAITING_CRED = False
                        tg_send("✅ Akun diterima.\nProses login…\n\nSABAAAR!")
                        RUN_EVENT.set()
                    else:
                        tg_send("Format salah.\nKirim:\nemail|pin")

        except requests.exceptions.RequestException as e:
            logging.warning(f"Koneksi polling error: {e}. Coba lagi..."); time.sleep(10)
        except Exception:
            logging.error(f"ERROR KRITIS bot_polling_loop:\n{traceback.format_exc()}"); time.sleep(5)

# ===================== MAIN =====================
if __name__ == "__main__":
    try:
        ensure_token_ok()
        threading.Thread(target=bot_polling_loop, daemon=True).start()
        threading.Thread(target=worker_loop, daemon=True).start()
        tg_send_menu(f"🤖 BOT [{SCRIPT_NAME}] ONLINE.\n{HELP_TEXT}")
        while True:
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot dihentikan."); sys.exit(0)
    except Exception:
        logging.critical(f"ERROR FATAL startup:\n{traceback.format_exc()}"); sys.exit(1)
