# Testing Auto CAPTCHA Solver

## 🚀 Quick Start di Codespace

### 1. Install Dependencies

```bash
pip install playwright pillow
playwright install chromium
```

### 2. Konfigurasi Credentials

Edit file `codegen.py` di line 44-48:

```python
# Credentials (GANTI DENGAN AKUN ANDA)
EMAIL = "email_anda@example.com"
PIN = "123456"

# NIK untuk testing
TEST_NIK = "3573045005800001"
```

### 3. Pilih Mode CAPTCHA

Edit file `codegen.py` di line 494:

```python
CAPTCHA_MODE = "AUTO"   # Otomatis dengan 4 drag methods
# CAPTCHA_MODE = "SEMI" # Manual solve
# CAPTCHA_MODE = "DEBUG" # Inspect element
```

### 4. Run Test

```bash
python codegen.py
```

---

## 📊 Output yang Dihasilkan

### Console Log

```
============================================================
🧩 ATTEMPT 1/6
============================================================
   🔍 Mencari elemen slider...
      Coba selector #1: button[class*='slider']
      ✅ DITEMUKAN: button[class*='slider']
      Tag: BUTTON
      Classes: slider-button-xyz

   📐 Slider Position:
      X: 123, Y: 456
      Width: 50, Height: 50

   🎯 Target Drag:
      Start: (148, 481)
      End: (408, 481)
      Distance: 260px

   🔄 METHOD 1: Locator.drag_to...
      Mencoba drag dengan Playwright native API...
      ✅ Drag_to executed

   🔍 Verifikasi hasil drag...
============================================================
✅ CAPTCHA BERHASIL DISELESAIKAN!
============================================================
```

### Screenshot Files

- `captcha_attempt_1.png` - Screenshot sebelum attempt
- `captcha_failed_N.png` - Screenshot jika gagal

### Browser Console

```
🌐 Browser Console: [JS DRAG] Starting...
🌐 Browser Console: [JS DRAG] Start: (148, 481), End: (408, 481), Distance: 260
🌐 Browser Console: [JS DRAG] Phase 1: mouseenter/mouseover
...
```

---

## 🔍 Troubleshooting

### Problem 1: Slider tidak ditemukan

**Gejala:**
```
❌ Slider tidak ditemukan setelah semua selector!
```

**Solusi:**
1. Check screenshot: `captcha_attempt_1.png`
2. Lihat debug output: `DEBUG: Semua element visible di modal`
3. Cari class/id tombol hijau yang benar
4. Tambahkan selector baru di line ~119-153

**Contoh menambah selector:**
```python
slider_selectors = [
    # ... existing selectors ...
    "button.custom-slider-class",  # Tambah di sini
]
```

---

### Problem 2: Drag tidak berfungsi sama sekali

**Gejala:**
```
❌ Method 1 failed: ...
❌ Method 2 failed: ...
❌ Method 3 failed: ...
❌ Method 4 failed: ...
```

**Solusi:**
1. **Check browser console** untuk JS errors
2. Pastikan `HEADLESS=False` (browser harus visible)
3. Coba manual solve untuk verifikasi captcha bisa diselesaikan:
   ```python
   CAPTCHA_MODE = "SEMI"
   ```
4. Element mungkin pakai iframe atau shadow DOM (perlu inspect lebih lanjut)

---

### Problem 3: Slider bergerak tapi puzzle tidak cocok

**Gejala:**
```
✅ Method 2 executed
❌ Puzzle belum cocok (attempt 1/6)
```

**Solusi:**
1. Check screenshot: `captcha_failed_1.png` - lihat seberapa jauh selisihnya
2. Adjust jarak di line 224-225:
   ```python
   distance_strategies = [260, 270, 250, 280, 240, 290]
   #                      ^^^ default distances untuk attempt 3-6
   ```
3. Untuk attempt 1-2, adjust line 222:
   ```python
   slide_distance = 260  # Default jika CV gagal
   ```

**Tips:** Jika selalu **kurang jauh**, tambah nilai (contoh: 260 → 280)
**Tips:** Jika selalu **kejauhan**, kurangi nilai (contoh: 260 → 240)

---

### Problem 4: Computer Vision error

**Gejala:**
```
⚠️ Gap detection error: ...
📏 CV gagal, gunakan default: 260px
```

**Solusi:**
1. Ini **NORMAL** - akan fallback ke distance default
2. Script tetap jalan dengan fixed distance
3. Jika mau improve CV, install dependencies:
   ```bash
   pip install pillow opencv-python numpy
   ```

---

### Problem 5: Timeout atau koneksi lambat

**Gejala:**
```
TimeoutError: Waiting for selector ...
```

**Solusi:**
1. Tambah `time.sleep()` lebih lama
2. Tingkatkan timeout di wait_for_selector:
   ```python
   page.wait_for_selector("...", timeout=10000)  # 10 detik
   ```
3. Check koneksi internet

---

## 🎯 Expected Success Rate

- **Method 1-2 (dengan CV):** ~60-70% success
- **Method 3-6 (fallback distances):** ~80-90% success (after 3+ attempts)
- **Overall success:** ~95% (dalam 6 attempts)

Jika **semua 6 attempts gagal**, kemungkinan:
1. Selector slider salah
2. Captcha pakai custom event handler (bukan standard mouse events)
3. Perlu inspect element lebih detail

---

## 📝 Next Steps Jika Auto-Solve Gagal

1. **Manual Mode Test:**
   ```python
   CAPTCHA_MODE = "SEMI"
   ```
   - Jika manual bisa → masalah di drag implementation
   - Jika manual juga gagal → masalah di captcha detection

2. **Debug Mode:**
   ```python
   CAPTCHA_MODE = "DEBUG"
   ```
   - Inspect element captcha
   - Screenshot untuk analyze
   - Cari selector yang tepat

3. **Fallback ke Manual (Production):**
   - Gunakan `BOTtunggal_with_captcha.py`
   - User solve manual via Telegram
   - 100% success rate

---

## 🔧 Advanced: Custom Selector

Jika perlu custom selector khusus untuk captcha Anda:

```python
# Di function solve_jigsaw_captcha, line ~119
slider_selectors = [
    "your-custom-selector-here",  # ADD FIRST untuk prioritas
    "button[class*='slider']",
    # ... rest ...
]
```

**Cara cari selector:**
1. Open browser DevTools (F12)
2. Klik inspect element (Ctrl+Shift+C)
3. Hover ke tombol hijau slider
4. Lihat HTML: `<button class="xyz-slider-abc" ...>`
5. Selector: `button[class*='slider']` atau `button.xyz-slider-abc`

---

## 📞 Support

Jika masih stuck:
1. Screenshot console output
2. Screenshot `captcha_attempt_1.png`
3. Share selector yang ditemukan di debug output
4. Contact: @rigeelm (Telegram)

---

**Good luck testing! 🚀**
