# 🚀 QUICK START GUIDE

## Setup Cepat (5 Menit)

### 1. Install
```bash
pip install playwright requests python-dotenv
playwright install chromium
```

### 2. Konfigurasi
Copy `BOTtunggal.env.example` ke `BOTtunggal.env` lalu isi:
```env
BOT_TOKEN=token_dari_botfather
ALLOWED_CHAT_ID=chat_id_anda
HEADLESS=0
CAPTCHA_TIMEOUT=120
```

### 3. Jalankan
```bash
python BOTtunggal_with_captcha.py
```

## Cara Pakai

### Via Telegram:

1️⃣ **LOGIN**
- Tekan tombol `LOGIN`
- Kirim: `email@example.com|123456`

2️⃣ **INPUT NIK**
- Tekan tombol `INPUT NIK`
- Kirim list NIK (1 per baris):
```
3510xxxxxxxxxxxx
3578xxxxxxxxxxxx
3501xxxxxxxxxxxx
```

3️⃣ **SOLVE CAPTCHA**
- Bot akan kirim notif: "🔐 CAPTCHA TERDETEKSI!"
- Buka browser → Selesaikan slide puzzle
- Tekan tombol `CAPTCHA DONE` di Telegram
- Bot otomatis lanjut

4️⃣ **CEK STATUS**
- Tekan tombol `STATUS` kapan saja

5️⃣ **STOP**
- Tekan tombol `STOP` untuk hentikan bot

## Tombol-Tombol

| Tombol | Fungsi |
|--------|--------|
| LOGIN | Login dengan akun baru |
| STOP | Hentikan bot & reset |
| CEK STOK | Cek stok tabung |
| HAPUS | Hapus semua NIK |
| STATUS | Lihat status bot |
| INPUT NIK | Input NIK baru |
| CAPTCHA DONE | Konfirmasi CAPTCHA selesai |

## Tips

✅ **WAJIB** set `HEADLESS=0` agar browser terlihat
✅ Jangan tutup browser saat proses berjalan
✅ Koneksi internet harus stabil
✅ 1 CAPTCHA biasanya muncul per 5-10 transaksi

## Workflow Multi-Akun

```
Login Akun 1 → Input NIK → Solve CAPTCHA → Selesai
   ↓
STOP
   ↓
Login Akun 2 → Input NIK → Solve CAPTCHA → Selesai
   ↓
STOP
   ↓
...dan seterusnya
```

## Troubleshooting

❌ **Bot tidak respon CAPTCHA DONE**
→ Cek log file, restart bot

❌ **Timeout terus**
→ Tingkatkan `CAPTCHA_TIMEOUT` di .env

❌ **Browser langsung close**
→ Set `HEADLESS=0`

## Support
📧 Telegram: @rigeelm
📄 Docs lengkap: README_CAPTCHA.md
