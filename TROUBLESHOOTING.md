# 🔧 TROUBLESHOOTING GUIDE - Bot Merchant CAPTCHA

## 🆘 MASALAH UMUM & SOLUSI

---

### ❌ Problem 1: Bot Tidak Detect CAPTCHA

**Gejala:**
- CAPTCHA muncul tapi bot langsung submit
- Transaksi gagal tanpa notifikasi CAPTCHA
- Log: "Tidak ada CAPTCHA terdeteksi"

**Penyebab:**
- Selector CAPTCHA tidak cocok
- CAPTCHA muncul terlalu lambat
- Website update struktur HTML

**Solusi:**

1. **Cek di Browser:**
   ```python
   # Buka browser dan inspect element CAPTCHA
   # Lihat class atau id yang digunakan
   ```

2. **Tambah Selector Custom:**
   Edit file bot, cari fungsi `wait_for_captcha_solution`, tambah selector:
   ```python
   captcha_selectors = [
       "[class*='captcha']",
       "[id*='captcha']",
       ".slide-verify",
       ".slider-verify",
       # TAMBAHKAN SELECTOR BARU DI SINI
       ".your-custom-captcha-class",
       "#your-captcha-id",
   ]
   ```

3. **Tingkatkan Wait Time:**
   Tambah delay sebelum cek CAPTCHA:
   ```python
   # Di dalam proses_nik, sebelum wait_for_captcha_solution
   time.sleep(2)  # Tunggu CAPTCHA muncul
   ```

---

### ⏰ Problem 2: Timeout Terus

**Gejala:**
- Notifikasi CAPTCHA muncul
- User sudah solve tapi bot timeout
- "⏱️ Timeout CAPTCHA untuk NIK xxx"

**Penyebab:**
- CAPTCHA_TIMEOUT terlalu pendek
- Koneksi internet lambat
- User solve terlalu lama

**Solusi:**

1. **Tingkatkan Timeout:**
   Edit `.env`:
   ```env
   CAPTCHA_TIMEOUT=180  # 3 menit
   # atau
   CAPTCHA_TIMEOUT=300  # 5 menit
   ```

2. **Cek Koneksi:**
   ```bash
   ping google.com
   # Pastikan ping < 100ms
   ```

3. **Speed Up Solve:**
   - Siapkan mental sebelum CAPTCHA muncul
   - Fokus ke browser saat notifikasi
   - Practice slide puzzle

---

### 🔴 Problem 3: CAPTCHA DONE Tidak Respon

**Gejala:**
- Tekan tombol "CAPTCHA DONE"
- Bot tidak lanjut
- Tetap stuck di CAPTCHA

**Penyebab:**
- Flag file tidak terbuat
- Bot polling error
- Sync issue

**Solusi:**

1. **Manual Create Flag:**
   ```bash
   # Di terminal/cmd
   touch captcha_solved_BOTtunggal.flag
   # Ganti BOTtunggal dengan nama script Anda
   ```

2. **Restart Bot:**
   ```bash
   # Ctrl+C untuk stop
   python BOTtunggal_with_captcha.py
   ```

3. **Cek Log:**
   ```bash
   tail -f BOTtunggal.log
   # Lihat apakah ada error saat tekan tombol
   ```

4. **Alternative Command:**
   Kirim text manual di Telegram:
   ```
   /captcha_done
   ```
   atau
   ```
   done
   ```

---

### 🌐 Problem 4: Browser Langsung Close

**Gejala:**
- Browser terbuka sebentar lalu tutup
- Tidak bisa lihat CAPTCHA
- Error di log

**Penyebab:**
- HEADLESS=1 (browser tersembunyi)
- Error saat startup
- Missing dependencies

**Solusi:**

1. **Set HEADLESS=0:**
   ```env
   HEADLESS=0
   ```

2. **Install Dependencies:**
   ```bash
   pip install playwright requests python-dotenv
   playwright install chromium
   ```

3. **Test Browser Manual:**
   ```python
   # test_browser.py
   from playwright.sync_api import sync_playwright
   
   with sync_playwright() as p:
       browser = p.chromium.launch(headless=False)
       page = browser.new_page()
       page.goto("https://google.com")
       input("Press Enter to close...")
       browser.close()
   ```

---

### 📱 Problem 5: Telegram Tidak Respon

**Gejala:**
- Tekan tombol tidak ada respon
- Bot tidak kirim notifikasi
- No feedback

**Penyebab:**
- BOT_TOKEN salah
- ALLOWED_CHAT_ID salah
- Webhook masih aktif
- Network issue

**Solusi:**

1. **Verify Token:**
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/getMe
   # Harus return info bot
   ```

2. **Get Chat ID:**
   - Kirim pesan ke bot @userinfobot
   - Copy chat ID Anda
   - Update di .env

3. **Delete Webhook:**
   ```bash
   curl https://api.telegram.org/bot<YOUR_TOKEN>/deleteWebhook
   ```

4. **Test Connection:**
   ```python
   # test_telegram.py
   import requests
   BOT_TOKEN = "your_token"
   CHAT_ID = "your_chat_id"
   
   r = requests.post(
       f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
       data={"chat_id": CHAT_ID, "text": "Test"}
   )
   print(r.json())
   ```

---

### 🔐 Problem 6: Login Gagal dengan CAPTCHA

**Gejala:**
- Stuck di halaman login
- CAPTCHA login tidak terdeteksi
- Loop login terus

**Penyebab:**
- CAPTCHA login berbeda dengan CAPTCHA transaksi
- Credentials salah
- Website anti-bot detection

**Solusi:**

1. **Manual Login Pertama:**
   ```python
   # Set HEADLESS=0
   # Login manual sekali
   # Biarkan cookies tersimpan
   # Login berikutnya akan lebih lancar
   ```

2. **Use Session Cookies:**
   Modifikasi bot untuk save cookies:
   ```python
   # Setelah login sukses
   context.storage_state(path="auth.json")
   
   # Saat startup berikutnya
   context = browser.new_context(storage_state="auth.json")
   ```

3. **Delay Before Login:**
   ```python
   page.goto(login_url)
   time.sleep(5)  # Tunggu halaman load penuh
   page.fill_email()...
   ```

---

### 💾 Problem 7: NIK Hilang/Tidak Tersimpan

**Gejala:**
- Input NIK via Telegram
- Bot confirm OK
- Tapi tidak diproses

**Penyebab:**
- File permission error
- Disk full
- Encoding issue

**Solusi:**

1. **Cek File Permission:**
   ```bash
   ls -la nik*.txt
   # Harus -rw-r--r--
   
   chmod 644 nik*.txt
   ```

2. **Cek Disk Space:**
   ```bash
   df -h
   # Pastikan ada space
   ```

3. **Manual Check:**
   ```bash
   cat nik.txt
   # Lihat isinya
   
   cat nik.queue
   # Cek queue
   ```

4. **Force Write:**
   Edit bot, tambah flush:
   ```python
   with NIK_FILE.open("a", encoding="utf-8") as f:
       f.write(nik + "\n")
       f.flush()  # Force write
   ```

---

### 🔄 Problem 8: Bot Stuck di Tengah Proses

**Gejala:**
- Proses berhenti tiba-tiba
- Tidak ada notifikasi error
- Log tidak update

**Penyebab:**
- Network timeout
- Website hang
- Memory leak

**Solusi:**

1. **Check Bot Status:**
   ```bash
   ps aux | grep python
   # Cari process bot
   
   kill -9 <PID>  # Force kill
   python bot.py  # Restart
   ```

2. **Recovery Mode:**
   ```bash
   # Cek queue file
   cat nik.queue
   # NIK yang tersisa akan auto-proses saat restart
   ```

3. **Add Heartbeat:**
   Modifikasi bot tambah logging:
   ```python
   while RUN_EVENT.is_set():
       logging.info(f"Heartbeat: {datetime.now()}")
       time.sleep(60)
   ```

---

### 🌍 Problem 9: Multiple CAPTCHA Berbeda

**Gejala:**
- Kadang slide puzzle
- Kadang image selection
- Kadang checkbox
- Bot detect salah

**Penyebab:**
- Website pakai multiple CAPTCHA provider
- Random CAPTCHA type

**Solusi:**

1. **Generic Detection:**
   ```python
   # Detect any CAPTCHA element
   captcha_found = (
       page.locator("[class*='captcha']").count() > 0 or
       page.locator("iframe[src*='captcha']").count() > 0 or
       page.locator(".g-recaptcha").count() > 0
   )
   ```

2. **Always Notify:**
   Saat ragu, selalu notif user:
   ```python
   if captcha_might_exist:
       tg_send("⚠️ Possible CAPTCHA, please check browser")
       wait_for_captcha_solution()
   ```

---

### 📊 Problem 10: Performance Lambat

**Gejala:**
- Bot jalan sangat lambat
- Response time tinggi
- RAM/CPU tinggi

**Penyebab:**
- Banyak bot running
- Memory leak
- Heavy logging

**Solusi:**

1. **Limit Bot Instance:**
   ```bash
   # Jangan run > 3 bot bersamaan
   # Tiap bot ~500MB RAM
   ```

2. **Clear Cache:**
   ```python
   # Tambah di reset_state
   import gc
   gc.collect()
   ```

3. **Optimize Logging:**
   ```python
   # Set level WARNING instead of INFO
   logging.basicConfig(level=logging.WARNING)
   ```

4. **Resource Monitor:**
   ```bash
   top -p $(pgrep -f bot.py)
   # Monitor RAM/CPU usage
   ```

---

## 🎯 DIAGNOSTIC CHECKLIST

Saat ada masalah, cek satu per satu:

- [ ] `.env` file ada dan terisi benar
- [ ] `HEADLESS=0` untuk CAPTCHA
- [ ] `BOT_TOKEN` dan `ALLOWED_CHAT_ID` benar
- [ ] Dependencies terinstall (`pip list`)
- [ ] Chromium terinstall (`playwright install`)
- [ ] Network stabil (ping test)
- [ ] Disk space cukup (`df -h`)
- [ ] File permission OK (`ls -la`)
- [ ] Log file ada error? (`tail BOTtunggal.log`)
- [ ] Bot process running? (`ps aux | grep python`)

---

## 🆘 EMERGENCY RECOVERY

Jika semua gagal:

```bash
# 1. Backup data
cp nik.txt nik.txt.backup
cp nik.queue nik.queue.backup
cp BOTtunggal.log BOTtunggal.log.backup

# 2. Clean reset
rm *.flag
rm *.queue

# 3. Fresh start
python BOTtunggal_with_captcha.py

# 4. Test 1 NIK dulu
# Input 1 NIK via Telegram
# Pastikan jalan normal

# 5. Restore if needed
# Jika masih error, revert ke backup
```

---

## 📞 NEED HELP?

Jika masih stuck setelah coba semua solusi:

1. **Kumpulkan Info:**
   - Screenshot error
   - Copy last 50 baris log
   - Describe exact steps yang dilakukan

2. **Contact Support:**
   - Telegram: @rigeelm
   - Kirim info di atas

3. **Alternative:**
   - Pakai mode manual (original bot)
   - Request IP whitelist ke pusat
   - Use bulk upload feature (jika ada)

---

**Good luck! 🍀**
