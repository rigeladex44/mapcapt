# Testing di Codespace (Headless Mode)

## 🚀 Quick Start

Karena Codespace tidak punya GUI, gunakan versi headless dengan video recording:

### 1. Install Dependencies

```bash
pip install playwright pillow
playwright install chromium
```

### 2. Edit Konfigurasi

File: `codegen_headless.py` line 30-35

```python
# Credentials (GANTI DENGAN AKUN ANDA)
EMAIL = "email_anda@example.com"
PIN = "123456"

# NIK untuk testing
TEST_NIK = "3573045005800001"
```

### 3. Run Script

```bash
python codegen_headless.py
```

---

## 📊 Output yang Dihasilkan

### Console Output

```
============================================================
🤖 MAPCAPT - Auto CAPTCHA Solver (HEADLESS)
============================================================
Email: irma_lpg@digdig.org
Mode: Headless + Video Recording
============================================================

🔵 Step 1: Buka halaman login...
   📸 Screenshot: step1_login_page.png

🔵 Step 2: Isi email...

🔵 Step 3: Isi PIN...
   📸 Screenshot: step3_credentials_filled.png

...

🔵 Step 10: Deteksi CAPTCHA...
   ✅ CAPTCHA TERDETEKSI!
   📸 Screenshot: captcha_detected.png

============================================================
🧩 CAPTCHA ANALYSIS
============================================================

   🔍 Mencari elemen slider...
      Coba selector #1: button[class*='slider']
      ✅ DITEMUKAN: button[class*='slider']
         Tag: BUTTON
         Class: slider-button-xyz
         ID: slider-btn-123

   🎯 Mencoba auto-drag di headless mode...
      Position: X=123, Y=456
      Size: W=50, H=50

      🔄 METHOD: CDP Mouse Drag
         Start: (148, 481)
         Distance: 260px
         ✅ Drag executed
      📸 Screenshot: captcha_after_drag.png

   ✅ CAPTCHA BERHASIL DISELESAIKAN!

✅ TRANSAKSI BERHASIL!
   Tombol 'Ke Beranda' terdeteksi

============================================================
📹 Closing browser and saving video...
============================================================

✅ DONE!

Output files:
  - videos/*.webm (video recording)
  - step*.png (screenshots setiap step)
  - captcha*.png (screenshots captcha)
  - final_result.png (hasil akhir)

============================================================
```

### Files Generated

```
mapcapt/
├── videos/
│   └── video.webm                   # Video recording seluruh proses
├── step1_login_page.png            # Screenshot halaman login
├── step3_credentials_filled.png    # Screenshot after fill credentials
├── step4_after_login.png           # Screenshot after login
├── step5_catat_penjualan.png       # Screenshot menu penjualan
├── step6_nik_filled.png            # Screenshot NIK filled
├── step7_lanjutkan.png             # Screenshot after lanjutkan
├── step8_check_order.png           # Screenshot check order
├── step9_before_captcha.png        # Screenshot before captcha
├── captcha_detected.png            # Screenshot CAPTCHA modal
├── captcha_after_drag.png          # Screenshot after drag attempt
└── final_result.png                # Screenshot hasil akhir
```

---

## 🔍 Cara Analisis Hasil

### 1. Download Screenshots

Di VSCode Codespace:
- Klik file di sidebar (contoh: `captcha_detected.png`)
- Klik kanan → Download

Atau via terminal:
```bash
# Zip semua screenshots
zip -r screenshots.zip *.png videos/

# Download via browser
# Klik file screenshots.zip → Download
```

### 2. Download Video Recording

```bash
# Video ada di folder videos/
ls -lh videos/

# Download untuk review detail
```

Video recording menunjukkan **seluruh proses** secara visual, sangat berguna untuk debugging!

### 3. Analisis CAPTCHA

#### Jika CAPTCHA Terdeteksi:

**Check:** `captcha_detected.png`
- Lihat apakah ada modal CAPTCHA
- Lihat tombol hijau slider
- Cari class/id dari element

**Check:** `captcha_after_drag.png`
- Lihat apakah slider bergerak
- Lihat apakah puzzle sudah cocok atau belum
- Jika belum cocok, hitung berapa pixel seharusnya

#### Jika Slider Tidak Ditemukan:

Console akan print:
```
❌ Slider tidak ditemukan!
📋 DEBUG: Mencari element yang visible...
  • BUTTON: custom-slider-class-xyz
  • BUTTON: another-button-class
  ...
```

Gunakan info ini untuk:
1. Cari class yang tepat
2. Tambahkan selector baru di `codegen.py` line ~119

---

## 🎯 Interpretasi Console Output

### ✅ Success Case

```
✅ CAPTCHA BERHASIL DISELESAIKAN!
✅ TRANSAKSI BERHASIL!
   Tombol 'Ke Beranda' terdeteksi
```

**Artinya:** Script berhasil! Auto-slide bekerja dengan baik.

---

### ⚠️ Slider Found but Puzzle Wrong

```
✅ DITEMUKAN: button[class*='slider']
✅ Drag executed
❌ CAPTCHA masih ada (puzzle tidak cocok)
💡 Check captcha_after_drag.png untuk lihat hasilnya
```

**Artinya:**
- Slider ditemukan ✅
- Drag berfungsi ✅
- Jarak drag tidak tepat ❌

**Solusi:**
1. Download `captcha_after_drag.png`
2. Lihat seberapa jauh slider dari posisi yang benar
3. Adjust distance di `codegen_headless.py` line 160:
   ```python
   distance = 260  # Tambah jika kurang jauh, kurangi jika kejauhan
   ```

---

### ❌ Slider Not Found

```
❌ Slider tidak ditemukan!
📋 DEBUG: Mencari element yang visible...
  • BUTTON: xyz-custom-slider
```

**Artinya:** Selector tidak cocok dengan element di halaman

**Solusi:**
1. Lihat output debug untuk class yang benar
2. Tambahkan selector di line 104-115:
   ```python
   slider_selectors = [
       "button.xyz-custom-slider",  # Tambah di sini
       "button[class*='slider']",
       # ... rest
   ]
   ```

---

## 💡 Tips Debugging di Codespace

### 1. Screenshot adalah Teman Terbaik Anda

Setiap step ada screenshot, gunakan untuk:
- Verify script jalan dengan benar
- Debug error visual
- Analyze CAPTCHA element

### 2. Video Recording untuk Full Context

Video menunjukkan:
- Animasi drag slider
- Timing issues
- Browser behavior

Download dan play untuk lihat **exactly** apa yang terjadi.

### 3. Console Output untuk Quick Check

Tanpa download apapun, console output sudah kasih info:
- Apakah slider ditemukan?
- Method mana yang executed?
- Apakah CAPTCHA solved?

---

## 🔧 Adjust Distance Strategy

Jika puzzle **selalu tidak cocok**, adjust di `codegen_headless.py`:

```python
# Line ~160
distance = 260  # Default

# Jika hasil drag:
# - Kurang jauh → Tambah (contoh: 280, 300)
# - Kejauhan → Kurangi (contoh: 240, 220)
```

Atau buat loop untuk test multiple distances:

```python
# Replace line 160 with:
distances_to_try = [260, 270, 250, 280, 240, 290]

for distance in distances_to_try:
    print(f"\n      🔄 Trying distance: {distance}px")

    # ... drag code ...

    # Check if solved
    try:
        page.wait_for_selector("text=Cocokan Gambar", state="hidden", timeout=2000)
        print(f"      ✅ SUCCESS with distance={distance}!")
        break
    except:
        print(f"      ❌ Failed with distance={distance}")
        # Refresh puzzle if possible
```

---

## 🚀 Advanced: Multi-Attempt Version

Untuk test multiple jarak sekaligus, jalankan:

```bash
# Test dengan 5 jarak berbeda
for dist in 240 250 260 270 280; do
    echo "Testing distance: $dist"
    sed -i "s/distance = [0-9]*/distance = $dist/" codegen_headless.py
    python codegen_headless.py
    mv captcha_after_drag.png captcha_dist_${dist}.png
done
```

Lalu download semua `captcha_dist_*.png` dan compare!

---

## 📞 Next Steps Setelah Test

### Jika Berhasil ✅

1. Catat distance yang tepat
2. Catat selector yang work
3. Merge ke production code (`BOTtunggal_with_captcha.py`)

### Jika Gagal ❌

Share dengan saya:
1. Console output (copy-paste)
2. `captcha_detected.png`
3. `captcha_after_drag.png`
4. Debug element list dari console

Saya bantu analyze dan kasih solusi!

---

## 🎯 Expected Behavior

**Normal flow:**
```
Login → Catat Penjualan → Isi NIK → Lanjutkan →
Check Order → Pay → CAPTCHA muncul → Auto drag →
CAPTCHA solved → Transaksi berhasil
```

**Jika ada step yang gagal**, screenshot akan tunjukkan di mana exactly masalahnya.

---

**Happy testing di Codespace! 🚀**
