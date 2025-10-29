# 📝 CHANGELOG - Bot Merchant App v2.0 (CAPTCHA Support)

## 🆕 Versi 2.0 - CAPTCHA Manual Solving Support

### Tanggal: 29 Oktober 2025

---

## ✨ Fitur Baru

### 1. **CAPTCHA Detection & Handling**
- ✅ Deteksi otomatis berbagai jenis CAPTCHA (slide puzzle, checkbox, etc)
- ✅ Notifikasi Telegram saat CAPTCHA muncul
- ✅ Pause otomatis menunggu user solve CAPTCHA
- ✅ Resume otomatis setelah konfirmasi
- ✅ Timeout handling untuk mencegah hang

### 2. **Tombol "CAPTCHA DONE"**
- Tombol baru di keyboard Telegram
- Konfirmasi cepat setelah solve CAPTCHA
- Support alias: "done", "captcha done", "/captcha_done"

### 3. **Enhanced Status Monitoring**
- Status menampilkan info CAPTCHA (normal/waiting)
- Menampilkan NIK yang sedang diproses CAPTCHA
- Real-time monitoring workflow

### 4. **Konfigurasi CAPTCHA_TIMEOUT**
- Setting di .env untuk atur timeout CAPTCHA
- Default: 120 detik (2 menit)
- Fleksibel sesuai kecepatan user

---

## 🔧 Perubahan Teknis

### Modified Functions:

1. **`wait_for_captcha_solution(page, nik, idx)`** - NEW
   - Fungsi utama untuk handle CAPTCHA
   - Auto-detect dengan multiple selectors
   - Flag-based communication dengan Telegram polling
   - Timeout handling

2. **`proses_nik(page, nik, idx)`** - MODIFIED
   - Tambah CAPTCHA check di setiap step kritis:
     * Setelah isi NIK
     * Sebelum "Lanjut Transaksi"
     * Sebelum "Check Order"
     * Sebelum "Pay"

3. **`login_dengan_retry(page, email, pin)`** - MODIFIED
   - Tambah CAPTCHA check saat login
   - Handle CAPTCHA login failure

4. **`bot_polling_loop()`** - MODIFIED
   - Handle command `/captcha_done`
   - Update status display dengan info CAPTCHA

5. **`reset_state()`** - MODIFIED
   - Tambah cleanup WAITING_CAPTCHA flag
   - Cleanup CAPTCHA_FLAG file
   - Reset CURRENT_NIK_PROCESSING

6. **`tg_send_menu()`** - MODIFIED
   - Tambah tombol "CAPTCHA DONE" di keyboard

---

## 📁 File Baru

1. **`captcha_solved_[SCRIPT_NAME].flag`**
   - Flag file untuk komunikasi CAPTCHA solved
   - Auto-cleanup setelah digunakan

2. **`BOTtunggal.env.example`**
   - Template konfigurasi dengan setting CAPTCHA
   - Dokumentasi lengkap setiap parameter

3. **`README_CAPTCHA.md`**
   - Dokumentasi lengkap fitur CAPTCHA
   - Troubleshooting guide
   - Workflow diagram

4. **`QUICK_START.md`**
   - Panduan cepat untuk new user
   - Setup dalam 5 menit

---

## 🆚 Perbandingan Versi

| Fitur | v1.0 (Original) | v2.0 (CAPTCHA) |
|-------|----------------|----------------|
| Auto login | ✅ | ✅ |
| Auto input NIK | ✅ | ✅ |
| Multi-account | ✅ | ✅ |
| Telegram control | ✅ | ✅ |
| CAPTCHA handling | ❌ | ✅ |
| Manual pause/resume | ❌ | ✅ |
| CAPTCHA timeout | ❌ | ✅ |
| Enhanced monitoring | ❌ | ✅ |

---

## 🔄 Migration Guide (v1.0 → v2.0)

### Step 1: Backup
```bash
cp BOTtunggal.py BOTtunggal.py.backup
cp BOTtunggal.env BOTtunggal.env.backup
```

### Step 2: Replace Script
```bash
cp BOTtunggal_with_captcha.py BOTtunggal.py
```

### Step 3: Update .env
Tambahkan di `BOTtunggal.env`:
```env
HEADLESS=0
CAPTCHA_TIMEOUT=120
```

### Step 4: Test
```bash
python BOTtunggal.py
```

### Step 5: Verify
- Login 1 akun
- Input 1-2 NIK untuk test
- Pastikan CAPTCHA detection bekerja
- Test tombol "CAPTCHA DONE"

---

## ⚠️ Breaking Changes

**NONE** - Backward compatible!
- Semua fitur v1.0 masih berfungsi normal
- .env lama masih bisa dipakai (CAPTCHA_TIMEOUT optional)
- Workflow lama tetap jalan tanpa masalah

---

## 🐛 Known Issues & Limitations

1. **Browser Visibility Required**
   - CAPTCHA manual require `HEADLESS=0`
   - Cannot solve CAPTCHA in headless mode

2. **Single-threaded CAPTCHA**
   - Hanya support 1 CAPTCHA solve at a time
   - Multi-browser parallel belum supported

3. **CAPTCHA Selector Dependency**
   - Tergantung pada struktur HTML website
   - Jika website update, perlu adjust selector

4. **Network Dependency**
   - Butuh koneksi stabil untuk Telegram polling
   - Flag-based sync bisa delay jika network lag

---

## 🔮 Future Improvements (Roadmap)

### v2.1 (Planned)
- [ ] Screenshot CAPTCHA auto-send ke Telegram
- [ ] Multiple CAPTCHA type detection
- [ ] Better error recovery
- [ ] Retry mechanism untuk failed CAPTCHA

### v2.2 (Planned)
- [ ] CAPTCHA solve statistics
- [ ] Average solve time tracking
- [ ] Performance metrics

### v3.0 (Future)
- [ ] Multi-browser parallel processing
- [ ] Optional CAPTCHA solving service integration
- [ ] Web dashboard for monitoring

---

## 📊 Performance Impact

### Tanpa CAPTCHA (v1.0):
- ~2 menit per NIK
- 30 NIK = 60 menit

### Dengan CAPTCHA (v2.0):
- ~3-5 menit per NIK (tergantung frekuensi CAPTCHA)
- 30 NIK = 90-150 menit
- **Overhead**: +50-150% waktu

### Catatan:
- Jika CAPTCHA muncul setiap 5-10 transaksi: overhead minimal (~20%)
- Jika CAPTCHA muncul setiap transaksi: overhead maksimal (~150%)

---

## 🙏 Credits

- **Original Bot**: BOTtunggal.py
- **CAPTCHA Support**: v2.0 Update
- **Testing**: Real-world merchant transactions
- **Support**: @rigeelm

---

## 📞 Support & Feedback

Jika menemukan bug atau ada saran improvement:
1. Check log file: `BOTtunggal.log`
2. Screenshot error message
3. Contact: @rigeelm (Telegram)

---

**Happy Automating! 🚀**
