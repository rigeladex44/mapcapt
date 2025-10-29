# 📘 DOKUMENTASI BOT MERCHANT APP + CAPTCHA SUPPORT

## 🆕 PERUBAHAN UTAMA

### 1. Fitur Baru: CAPTCHA Manual Solving
Bot sekarang akan:
- ✅ Otomatis **mendeteksi** CAPTCHA di halaman
- ✅ **Memberi notifikasi** ke Telegram saat CAPTCHA muncul
- ✅ **Menunggu** Anda menyelesaikan CAPTCHA
- ✅ **Melanjutkan** proses setelah Anda konfirmasi

### 2. Tombol Baru: "CAPTCHA DONE"
- Tekan tombol ini setelah Anda selesaikan CAPTCHA slide puzzle
- Bot akan langsung melanjutkan proses

### 3. Konfigurasi Baru di .env
```env
# File: BOTtunggal.env (atau sesuai nama script Anda)

BOT_TOKEN=123456789:ABC-DEF...
ALLOWED_CHAT_ID=987654321
HEADLESS=0                    # 0 = browser terlihat, 1 = headless
CAPTCHA_TIMEOUT=120           # Maksimal 120 detik (2 menit) untuk solve CAPTCHA
```

---

## 📋 CARA KERJA

### Workflow Normal (Tanpa CAPTCHA)
```
1. Login → Isi NIK → Submit → ✅ Berhasil
```

### Workflow dengan CAPTCHA
```
1. Login → Isi NIK
2. 🔐 CAPTCHA TERDETEKSI!
3. Bot kirim notifikasi Telegram:
   "🔐 CAPTCHA TERDETEKSI!
    NIK #5: 3510xxxxxxxxxxxx
    
    Silakan selesaikan CAPTCHA di browser,
    lalu tekan tombol 'CAPTCHA DONE'
    
    ⏱️ Timeout: 120 detik"

4. Anda buka browser → Slide puzzle CAPTCHA
5. Setelah selesai → Tekan "CAPTCHA DONE" di Telegram
6. Bot lanjut → Submit → ✅ Berhasil
```

---

## 🚀 CARA INSTALL & JALANKAN

### 1. Install Dependencies
```bash
pip install playwright requests python-dotenv
playwright install chromium
```

### 2. Setup File .env
Buat file `BOTtunggal.env` (sesuaikan nama dengan script):
```env
BOT_TOKEN=your_telegram_bot_token
ALLOWED_CHAT_ID=your_telegram_chat_id
HEADLESS=0
CAPTCHA_TIMEOUT=120
```

### 3. Jalankan Bot
```bash
python BOTtunggal_with_captcha.py
```

---

## 💡 TIPS PENGGUNAAN

### 1. Browser Headless vs Visible
**Untuk CAPTCHA, WAJIB pakai `HEADLESS=0`** agar Anda bisa lihat & solve CAPTCHA!

```env
HEADLESS=0  # Browser terlihat (RECOMMENDED untuk CAPTCHA)
HEADLESS=1  # Browser tersembunyi (TIDAK bisa solve CAPTCHA manual)
```

### 2. Timeout CAPTCHA
Sesuaikan dengan kecepatan Anda menyelesaikan CAPTCHA:

```env
CAPTCHA_TIMEOUT=120  # 2 menit (default, cukup untuk slide puzzle)
CAPTCHA_TIMEOUT=180  # 3 menit (jika jaringan lambat)
CAPTCHA_TIMEOUT=60   # 1 menit (jika Anda cepat)
```

### 3. Multi-Account Processing
Bot ini sudah support multi-akun. Workflow:

1. LOGIN dengan akun 1
2. INPUT NIK untuk akun 1
3. Proses selesai
4. STOP
5. LOGIN dengan akun 2
6. INPUT NIK untuk akun 2
7. Dan seterusnya...

### 4. Monitoring Status
Tekan tombol **STATUS** untuk cek:
- Status bot (RUN/STOP)
- Nama pangkalan yang sedang login
- Jumlah NIK dalam proses & antrian
- Status CAPTCHA (normal atau sedang menunggu)

---

## 🔍 DETEKSI CAPTCHA

Bot akan mencari elemen CAPTCHA dengan berbagai selector:
- `[class*='captcha']`
- `[id*='captcha']`
- `.slide-verify`
- `.slider-verify`
- Teks yang mengandung "captcha" atau "verifikasi"

**Jika CAPTCHA tidak terdeteksi otomatis**, Anda bisa:
1. Lihat di log file apa ada error
2. Modifikasi `captcha_selectors` di fungsi `wait_for_captcha_solution()`

---

## 📊 FLOW DIAGRAM

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   LOGIN     │◄───────┐
└──────┬──────┘        │
       │               │
       ▼               │
   [CAPTCHA?]──YES──►[WAIT]──TIMEOUT──►[SKIP NIK]
       │                │
       NO              DONE
       │                │
       ▼                ▼
┌─────────────┐   ┌──────────┐
│  ISI FORM   │   │ LANJUT   │
└──────┬──────┘   └────┬─────┘
       │               │
       ▼               │
   [CAPTCHA?]──YES─────┘
       │
       NO
       │
       ▼
┌─────────────┐
│   SUBMIT    │
└──────┬──────┘
       │
       ▼
   [BERHASIL]
```

---

## 🐛 TROUBLESHOOTING

### Problem 1: Bot tidak detect CAPTCHA
**Solusi:**
- Pastikan `HEADLESS=0`
- Tambahkan selector CAPTCHA spesifik untuk website Anda
- Cek log file untuk melihat error

### Problem 2: Timeout terus
**Solusi:**
- Tingkatkan `CAPTCHA_TIMEOUT` di .env
- Pastikan koneksi internet stabil
- Gunakan browser yang sudah login sebelumnya (cookies)

### Problem 3: CAPTCHA Done tidak respon
**Solusi:**
- Cek apakah bot masih running (cek log)
- Restart bot
- Pastikan tidak ada typo saat tekan tombol

### Problem 4: Browser langsung close
**Solusi:**
- Ganti `HEADLESS=0` agar browser tetap terbuka
- Tambah `time.sleep()` sebelum close browser (untuk debugging)

---

## 📁 STRUKTUR FILE

```
project/
│
├── BOTtunggal_with_captcha.py   # Script utama
├── BOTtunggal.env                # Konfigurasi
├── BOTtunggal.log                # Log file
├── nik.txt                       # Input NIK
├── nik.queue                     # Antrian NIK
├── cek_BOTtunggal.flag           # Flag cek stok
└── captcha_solved_BOTtunggal.flag # Flag CAPTCHA selesai
```

---

## 🔐 KEAMANAN

1. **JANGAN SHARE** file .env (ada token & chat ID)
2. **JANGAN COMMIT** .env ke Git
3. Gunakan `.gitignore`:
```
*.env
*.log
nik*.txt
nik*.queue
*.flag
```

---

## 📞 SUPPORT

Jika ada error atau pertanyaan:
- Check log file: `BOTtunggal.log`
- Contact: @rigeelm (Telegram)

---

## 📈 STATISTIK & MONITORING

Bot akan memberikan laporan setelah selesai batch:

```
✅ [PANGKALAN MAJU JAYA] NIK diproses
━━━━━━━━━━━━━━━━━
Total   : 50
Berhasil: 45
Gagal   : 5
NIK gagal:
1. 3510xxxxxxxxxxxx
2. 3578xxxxxxxxxxxx
3. 3501xxxxxxxxxxxx
4. 3502xxxxxxxxxxxx
5. 3503xxxxxxxxxxxx
```

---

## 🎯 REKOMENDASI WORKFLOW HARIAN

### Untuk 3-5 Akun dengan 20-50 NIK per Akun:

**PAGI (08:00 - 10:00)**
1. Siapkan semua file NIK per akun
2. Login akun 1
3. Input semua NIK akun 1
4. Pantau & solve CAPTCHA yang muncul
5. Selesai → Stop → Login akun 2
6. Ulangi untuk semua akun

**Estimasi Waktu:**
- Tanpa CAPTCHA: ~2 menit per NIK
- Dengan CAPTCHA: ~3-5 menit per NIK (tergantung frekuensi)

**Tips:**
- Buka browser di monitor kedua (jika ada)
- Jangan multitasking saat solve CAPTCHA
- Gunakan koneksi internet stabil

---

## 🔄 UPDATE & MAINTENANCE

### Jika Website Update:
1. Cek selector yang berubah
2. Update di fungsi `proses_nik()` atau `login_dengan_retry()`
3. Test dengan 1 NIK dulu sebelum batch

### Jika CAPTCHA Makin Ketat:
1. Pertimbangkan request IP whitelist ke pusat
2. Atau request akun khusus tanpa CAPTCHA
3. Dokumentasikan untuk eskalasi

---

**SELAMAT MENGGUNAKAN! 🚀**
