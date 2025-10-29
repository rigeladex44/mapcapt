# Setup dan Testing di Local Machine (GRATIS!)

Karena Codespace berbayar, mari test di **komputer/laptop Anda**. 100% gratis dan lebih mudah karena bisa lihat browser!

---

## 📋 Requirement

- **Python 3.7+** (check: `python --version` atau `python3 --version`)
- **Git** (untuk clone repository)
- **Internet connection** (untuk install dependencies)

**Sistem Operasi:** Windows, Mac, atau Linux (semua supported!)

---

## 🚀 Setup (5 Menit)

### Step 1: Clone Repository

Buka **Terminal** (Mac/Linux) atau **Command Prompt** (Windows):

```bash
git clone https://github.com/rigeladex44/mapcapt.git
cd mapcapt
```

### Step 2: Checkout Branch dengan Update Terbaru

```bash
git fetch origin
git checkout claude/check-mapcap-repo-011CUbXxHTpLDm47Xa335HJZ
```

**Verify:**
```bash
git branch
# Output harus menunjukkan: * claude/check-mapcap-repo-011CUbXxHTpLDm47Xa335HJZ
```

### Step 3: Install Python Dependencies

```bash
pip install playwright pillow

# Atau jika menggunakan pip3:
pip3 install playwright pillow
```

### Step 4: Install Browser Chromium

```bash
playwright install chromium
```

**Note:** Ini akan download browser Chromium (~100MB). Wait sampai selesai.

### Step 5: Verify Installation

```bash
python -c "from playwright.sync_api import sync_playwright; print('✅ Playwright installed!')"
```

Jika muncul error, coba:
```bash
python3 -c "from playwright.sync_api import sync_playwright; print('✅ Playwright installed!')"
```

---

## 🎯 Testing Scripts (Pilih Salah Satu)

### OPSI A: Full Automation Test (`codegen.py`)

**Fungsi:** Test FULL automation dengan auto CAPTCHA solver

**Steps:**

1. **Edit konfigurasi:**

   Buka `codegen.py` dengan text editor (Notepad++, VSCode, Sublime, dll)

   **Line 44-48:**
   ```python
   # Credentials (GANTI DENGAN AKUN ANDA)
   EMAIL = "email_anda@example.com"  # ← GANTI
   PIN = "123456"                     # ← GANTI

   # NIK untuk testing
   TEST_NIK = "3573045005800001"      # ← NIK valid
   ```

   Save file.

2. **Run script:**

   ```bash
   python codegen.py
   ```

3. **Apa yang terjadi:**

   - Browser Chromium terbuka otomatis
   - Login otomatis
   - Navigate ke form penjualan
   - Isi NIK
   - **Saat CAPTCHA muncul:**
     - Script detect CAPTCHA
     - Coba 4 drag methods
     - Max 6 attempts dengan jarak berbeda
   - Console log detail setiap step

4. **Output:**

   - Console log dengan emoji dan detail
   - Screenshots: `captcha_attempt_*.png`
   - Browser tetap terbuka untuk inspect

**Success indicator:**
```
✅ CAPTCHA BERHASIL DISELESAIKAN!
✅ TRANSAKSI BERHASIL!
```

---

### OPSI B: Inspector Only (`inspector.py`) ⭐ RECOMMENDED FIRST

**Fungsi:** HANYA inspect CAPTCHA element tanpa full automation

**Kenapa pakai ini dulu:**
- ✅ Tidak perlu credentials
- ✅ Tidak execute transaksi
- ✅ Cepat (< 2 menit)
- ✅ Cek apakah selector bisa detect slider

**Steps:**

1. **Run script:**

   ```bash
   python inspector.py
   ```

2. **Apa yang terjadi:**

   - Browser terbuka ke halaman target
   - Script wait 30 detik untuk Anda **login manual** (jika perlu)
   - Setelah 30 detik, script otomatis:
     - Detect CAPTCHA
     - Test 18 slider selectors
     - Report hasil detection
     - Screenshot dengan highlight element
     - Browser tetap terbuka 60 detik untuk inspect manual

3. **Output Console:**

   ```
   ============================================================
   🔍 MAPCAPT INSPECTOR - Element Detection
   ============================================================

   📍 Step 1: Navigating to page...
      (Jika perlu login, silakan login manual)
      Script akan wait 30 detik...

   ⏳ Waiting 30 seconds...
      - Silakan login manual jika diperlukan
      - Navigate ke page yang ada CAPTCHA

   📸 Taking screenshot...
      ✅ Saved: page_before_inspection.png

   ============================================================
   🧩 CAPTCHA DETECTION
   ============================================================
      ✅ CAPTCHA FOUND: text=Cocokan Gambar

   ============================================================
   🔍 SLIDER ELEMENT DETECTION
   ============================================================

      Trying #1: Button with 'slider' class
         Selector: button[class*='slider']
         ✅ FOUND and VISIBLE!
         📋 Details:
            Tag: BUTTON
            Class: slider-button-xyz-123
            ID: slider-btn-1
            Position: X=123, Y=456
            Size: W=50, H=50

   ============================================================
   📊 DETECTION SUMMARY
   ============================================================

   ✅ Found 1 slider element(s)!

   Element #1:
     Selector: button[class*='slider']
     Tag: BUTTON
     Class: slider-button-xyz-123
     ID: slider-btn-1
     Position: (123, 456)

   💡 RECOMMENDED ACTION:
      Use this selector in codegen.py:
      'button[class*='slider']'

   📸 Screenshot with highlighted slider:
      ✅ Saved: slider_detected_highlighted.png
   ```

4. **Generated Files:**

   - `page_before_inspection.png` - Halaman sebelum inspect
   - `captcha_detected_inspection.png` - CAPTCHA modal
   - `slider_detected_highlighted.png` - Slider dengan border merah (jika found)

5. **Next step:**

   - Jika slider **FOUND** ✅ → Lanjut test `codegen.py`
   - Jika slider **NOT FOUND** ❌ → Share screenshot, saya bantu cari selector

---

## 📊 Troubleshooting

### Problem 1: Python command not found

**Error:**
```
'python' is not recognized as an internal or external command
```

**Solusi:**

**Windows:**
1. Install Python dari [python.org](https://www.python.org/downloads/)
2. Saat install, **CENTANG** "Add Python to PATH"
3. Restart terminal/command prompt
4. Try: `python3` instead of `python`

**Mac:**
```bash
brew install python3
# Atau download dari python.org
```

**Linux:**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

### Problem 2: pip not found

**Solusi:**
```bash
# Windows
python -m pip install playwright pillow

# Mac/Linux
python3 -m pip install playwright pillow
```

---

### Problem 3: playwright install chromium gagal

**Error:**
```
Failed to download chromium
```

**Solusi:**
1. Check internet connection
2. Disable antivirus/firewall sementara
3. Atau install manual:
   ```bash
   playwright install --with-deps chromium
   ```

---

### Problem 4: Browser tidak terbuka (headless mode)

**Cek:** Line 51 di `codegen.py` atau `inspector.py`

```python
HEADLESS = False  # Harus False untuk browser visible
```

Jika `HEADLESS = True`, ganti ke `False` dan save.

---

### Problem 5: ModuleNotFoundError: No module named 'playwright'

**Solusi:**
```bash
# Install ulang
pip install --upgrade playwright pillow
playwright install chromium

# Atau pakai pip3
pip3 install --upgrade playwright pillow
python3 -m playwright install chromium
```

---

## 🎯 Recommended Workflow

**Step-by-step untuk hasil terbaik:**

### 1. Test Inspector Dulu (2 menit)

```bash
python inspector.py
```

- Browser terbuka
- Login manual (30 detik)
- Trigger CAPTCHA secara manual (submit form, dll)
- Script detect element otomatis
- Check console output

**Output yang dicari:**
```
✅ Found 1 slider element(s)!
💡 Use this selector: 'button[class*='slider']'
```

### 2. Review Screenshots

- Open `slider_detected_highlighted.png`
- Lihat apakah tombol hijau ter-highlight dengan border merah
- Verify bahwa itu benar slider CAPTCHA

### 3. Test Full Automation (jika inspector success)

```bash
python codegen.py
```

- Edit credentials dulu!
- Run script
- Watch browser automation
- Check console log

**Expected:**
```
✅ CAPTCHA BERHASIL DISELESAIKAN!
```

### 4. Share Hasil

Jika ada masalah, share dengan saya:
- Console output (copy-paste)
- Screenshots (`slider_detected_highlighted.png`)
- Selector yang ditemukan

---

## 💡 Tips

### Tip 1: Gunakan Virtual Environment (Optional tapi Recommended)

```bash
# Create virtual env
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install playwright pillow
playwright install chromium

# Run script
python codegen.py

# Deactivate when done
deactivate
```

**Benefit:** Isolated environment, tidak bentrok dengan package lain

---

### Tip 2: Edit Script dengan IDE yang Bagus

**Recommended:**
- **VSCode** (gratis, powerful) - Download: [code.visualstudio.com](https://code.visualstudio.com/)
- **PyCharm Community** (gratis untuk non-commercial)
- **Sublime Text** (free trial unlimited)

**Kenapa?** Syntax highlighting, autocomplete, easy navigation

---

### Tip 3: Run dengan Verbose Output

Jika butuh lebih banyak debug info:

```bash
# Set environment variable
# Mac/Linux:
export DEBUG=pw:api
python codegen.py

# Windows CMD:
set DEBUG=pw:api
python codegen.py

# Windows PowerShell:
$env:DEBUG="pw:api"
python codegen.py
```

---

## 📞 Need Help?

Jika stuck di step manapun:

1. **Screenshot error message** (console + browser jika ada)
2. **Copy-paste console output**
3. **Mention OS Anda** (Windows/Mac/Linux + version)
4. **Python version:** `python --version`

Share ke saya, saya bantu troubleshoot! 🚀

---

## 🎉 Checklist

Sebelum run script, pastikan:

- [ ] Python 3.7+ installed (`python --version`)
- [ ] Repository cloned dan di branch yang benar
- [ ] Dependencies installed (`pip install playwright pillow`)
- [ ] Chromium installed (`playwright install chromium`)
- [ ] Credentials sudah diisi (untuk `codegen.py`)
- [ ] `HEADLESS = False` (untuk browser visible)

**Jika semua ✅, run:**
```bash
python inspector.py  # Test element detection dulu
```

**Good luck! 🚀**
