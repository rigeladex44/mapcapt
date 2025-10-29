"""
MAPCAPT - Auto CAPTCHA Solver with Enhanced Debugging
======================================================

USAGE:
1. Install dependencies:
   pip install playwright pillow
   playwright install chromium

2. Configure credentials di bawah (line ~20-25)

3. Run script:
   python codegen.py

4. Mode CAPTCHA (line ~350):
   - AUTO: Coba auto-solve dengan 4 methods + CV
   - SEMI: Pause untuk manual solve
   - DEBUG: Screenshot dan inspect

5. Check output:
   - Console log dengan detail setiap step
   - Screenshot: captcha_attempt_N.png, captcha_failed_N.png
   - Browser console: [JS DRAG] logs

TROUBLESHOOTING:
- Jika slider tidak ditemukan: Check screenshot dan selector debug output
- Jika drag tidak jalan: Check browser console untuk JS errors
- Jika puzzle tidak cocok: Adjust distance_strategies (line ~220-225)

"""
import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect
from PIL import Image
import io


def run(playwright: Playwright) -> None:
    # ============================================================
    # KONFIGURASI - EDIT DI SINI
    # ============================================================

    # Credentials (GANTI DENGAN AKUN ANDA)
    EMAIL = "irma_lpg@digdig.org"
    PIN = "401001"

    # NIK untuk testing
    TEST_NIK = "3573045005800001"

    # Browser settings
    HEADLESS = False  # False = terlihat, True = headless

    # ============================================================

    print("\n" + "="*60)
    print("🤖 MAPCAPT - Auto CAPTCHA Solver")
    print("="*60)
    print(f"Email: {EMAIL}")
    print(f"Headless: {HEADLESS}")
    print("="*60 + "\n")

    # PENTING: Jangan gunakan slow_mo karena bisa interferensi dengan drag
    browser = playwright.chromium.launch(headless=HEADLESS)
    context = browser.new_context()
    page = context.new_page()

    # Enable console logging untuk debug
    page.on("console", lambda msg: print(f"🌐 Browser Console: {msg.text}"))

    print("🔵 Step 1: Buka halaman login...")
    page.goto("https://subsiditepatlpg.mypertamina.id/merchant-login")

    print("🔵 Step 2: Isi email...")
    page.get_by_role("textbox", name="Nomor Ponsel atau Email").fill(EMAIL)
    time.sleep(2)

    print("🔵 Step 3: Isi PIN...")
    page.get_by_role("textbox", name="PIN").fill(PIN)
    
    print("🔵 Step 4: Klik tombol MASUK...")
    page.get_by_role("button", name="MASUK").click()
    time.sleep(2)
    
    print("🔵 Step 5: Klik Catat Penjualan...")
    page.locator("div").filter(has_text=re.compile(r"^Catat Penjualan$")).first.click()
    time.sleep(2)

    print(f"🔵 Step 6: Isi NIK ({TEST_NIK})...")
    page.get_by_role("combobox", name="Masukkan 16 digit NIK").fill(TEST_NIK)
    
    print("🔵 Step 7: Klik LANJUTKAN PENJUALAN...")
    page.get_by_role("button", name="LANJUTKAN PENJUALAN").click()
    time.sleep(1)
    
    print("🔵 Step 8: Klik btnCheckOrder...")
    page.get_by_test_id("btnCheckOrder").click()
    time.sleep(1)
    
    print("🔵 Step 9: Klik btnPay...")
    page.get_by_test_id("btnPay").click()
    time.sleep(2)

    ##CAPTCHA JIGSAW PUZZLE - COMPUTER VISION ENHANCED##
    def detect_puzzle_gap(page):
        """Deteksi posisi gap puzzle dengan image analysis"""
        try:
            # Screenshot captcha area
            captcha_image = page.locator("text=Cocokan Gambar untuk Proses Keamanan").locator("xpath=../..").screenshot()
            img = Image.open(io.BytesIO(captcha_image))
            
            # Convert to grayscale untuk analysis
            gray = img.convert('L')
            width, height = gray.size
            
            # Cari area yang paling gelap/berbeda (gap puzzle biasanya lebih gelap)
            pixels = list(gray.getdata())
            
            # Hitung brightness average per column
            col_brightness = []
            for x in range(width):
                col_sum = sum(pixels[y * width + x] for y in range(height))
                col_brightness.append(col_sum / height)
            
            # Find gap (area dengan brightness paling rendah/berbeda)
            avg_brightness = sum(col_brightness) / len(col_brightness)
            
            # Gap biasanya di 50-80% area
            search_start = int(width * 0.3)
            search_end = int(width * 0.8)
            
            min_bright = min(col_brightness[search_start:search_end])
            gap_x = col_brightness.index(min_bright, search_start)
            
            # Convert to distance from start
            gap_distance = gap_x - 50  # Offset dari posisi awal slider
            
            print(f"   🔍 Gap detected at X={gap_x}, distance={gap_distance}px")
            return gap_distance if 150 < gap_distance < 350 else None
            
        except Exception as e:
            print(f"   ⚠️ Gap detection error: {e}")
            return None
    
    def solve_jigsaw_captcha(page, max_attempts=6):
        """
        Menyelesaikan jigsaw puzzle captcha dengan multiple drag strategies
        Modal: "Cocokan Gambar untuk Proses Keamanan Penjualan"
        """
        for attempt in range(1, max_attempts + 1):
            try:
                print(f"\n{'='*60}")
                print(f"🧩 ATTEMPT {attempt}/{max_attempts}")
                print(f"{'='*60}")

                # Tunggu modal captcha muncul
                captcha_modal = page.locator("text=Cocokan Gambar untuk Proses Keamanan").first
                if not captcha_modal.is_visible(timeout=3000):
                    print("✅ Captcha tidak muncul, lanjut...")
                    return True

                time.sleep(2)

                # Screenshot untuk debugging
                try:
                    page.screenshot(path=f"captcha_attempt_{attempt}.png")
                    print(f"📸 Screenshot: captcha_attempt_{attempt}.png")
                except:
                    pass

                # STRATEGI 1: Cari tombol hijau dengan berbagai cara (EXPANDED)
                slider_element = None
                slider_selectors = [
                    # Button selectors
                    "button[class*='slider']",
                    "button[class*='Slider']",
                    "button[id*='slider']",
                    "button:has(svg)",

                    # Div selectors
                    "div[class*='slider-button']",
                    "div[class*='sliderButton']",
                    "div[class*='captcha-slider']",
                    "div[class*='drag-button']",
                    "div[class*='dragButton']",

                    # Span selectors
                    "span[class*='slider']",
                    "span[class*='drag']",

                    # Generic draggable
                    "[draggable='true']",
                    "[role='slider']",

                    # RC Captcha patterns
                    "[class*='rc-slider']",
                    "[class*='rc-anchor-center-item']",
                    ".rc-slider-handle",

                    # Text-based
                    "div:has-text('Geser')",
                    "button:has-text('Geser')",

                    # Icon-based (green button with arrow)
                    "button svg[class*='arrow']",
                    "button svg[class*='icon']",
                ]

                print("   🔍 Mencari elemen slider...")
                for idx, selector in enumerate(slider_selectors, 1):
                    try:
                        print(f"      Coba selector #{idx}: {selector}")
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=500):
                            slider_element = elem
                            print(f"   ✅ DITEMUKAN: {selector}")

                            # Debug info
                            try:
                                tag = elem.evaluate("el => el.tagName")
                                classes = elem.evaluate("el => el.className")
                                print(f"      Tag: {tag}")
                                print(f"      Classes: {classes}")
                            except:
                                pass
                            break
                    except Exception as e:
                        print(f"      ✗ Gagal: {str(e)[:50]}")
                        continue
                
                if not slider_element:
                    print("   ❌ Slider tidak ditemukan setelah semua selector!")
                    print("   💡 TIP: Inspect element captcha dan cari selector yang tepat")

                    # Dump semua element yang terlihat untuk debugging
                    try:
                        print("\n   📋 DEBUG: Semua element visible di modal:")
                        all_elements = page.locator("*").all()
                        visible_count = 0
                        for el in all_elements[:50]:  # Max 50
                            try:
                                if el.is_visible():
                                    tag = el.evaluate("el => el.tagName")
                                    classes = el.evaluate("el => el.className") or "[no class]"
                                    id_attr = el.evaluate("el => el.id") or "[no id]"
                                    if any(keyword in str(classes).lower() for keyword in ['slider', 'drag', 'button', 'captcha']):
                                        print(f"      • {tag}: class='{classes[:50]}' id='{id_attr}'")
                                        visible_count += 1
                                    if visible_count >= 10:
                                        break
                            except:
                                continue
                    except:
                        pass

                    continue

                slider_box = slider_element.bounding_box()
                if not slider_box:
                    print("   ⚠️ Tidak bisa dapatkan bounding box slider")
                    continue

                print(f"\n   📐 Slider Position:")
                print(f"      X: {slider_box['x']}, Y: {slider_box['y']}")
                print(f"      Width: {slider_box['width']}, Height: {slider_box['height']}")

                # STRATEGI 2: Deteksi gap dengan computer vision (attempt 1 & 2)
                # Atau fallback ke fixed distances
                if attempt <= 2:
                    detected_distance = detect_puzzle_gap(page)
                    if detected_distance:
                        slide_distance = detected_distance
                        print(f"   🎯 Menggunakan CV detection: {slide_distance}px")
                    else:
                        slide_distance = 260
                        print(f"   📏 CV gagal, gunakan default: {slide_distance}px")
                else:
                    distance_strategies = [250, 270, 230, 290, 210, 300]
                    slide_distance = distance_strategies[min(attempt - 3, len(distance_strategies) - 1)]
                    print(f"   📏 Jarak drag attempt {attempt}: {slide_distance}px")

                # STRATEGI 3: Advanced Multi-Method Drag (paling mirip manual)
                start_x = slider_box['x'] + slider_box['width'] / 2
                start_y = slider_box['y'] + slider_box['height'] / 2
                end_x = start_x + slide_distance

                print(f"\n   🎯 Target Drag:")
                print(f"      Start: ({int(start_x)}, {int(start_y)})")
                print(f"      End: ({int(end_x)}, {int(start_y)})")
                print(f"      Distance: {slide_distance}px")

                drag_success = False

                # METHOD 1: Locator.drag_to dengan source & target position
                print("\n   🔄 METHOD 1: Locator.drag_to...")
                try:
                    print("      Mencoba drag dengan Playwright native API...")
                    slider_element.drag_to(
                        page.locator("body"),
                        source_position={"x": slider_box['width'] / 2, "y": slider_box['height'] / 2},
                        target_position={"x": end_x, "y": start_y}
                    )
                    print("      ✅ Drag_to executed")
                    drag_success = True
                    time.sleep(2)
                except Exception as e1:
                    print(f"      ❌ Method 1 failed: {str(e1)[:100]}")
                
                # METHOD 2: CDP-level mouse events (jika method 1 gagal)
                if not drag_success:
                    print("\n   🔄 METHOD 2: CDP Mouse Commands...")
                    try:
                        print(f"      Hover ke start position ({int(start_x)}, {int(start_y)})...")
                        page.mouse.move(start_x, start_y)
                        time.sleep(0.5)

                        print("      Mouse down (press)...")
                        page.mouse.down()
                        time.sleep(0.3)

                        print(f"      Dragging {slide_distance}px dengan 25 steps...")
                        steps = 25
                        for i in range(1, steps + 1):
                            current_x = start_x + (slide_distance * i / steps)
                            page.mouse.move(current_x, start_y)
                            time.sleep(0.02)
                            if i % 5 == 0:
                                print(f"         Step {i}/{steps}: x={int(current_x)}")

                        print("      Mouse up (release)...")
                        time.sleep(0.3)
                        page.mouse.up()
                        print("      ✅ CDP mouse drag executed")
                        drag_success = True
                        time.sleep(2)
                    except Exception as e2:
                        print(f"      ❌ Method 2 failed: {str(e2)[:100]}")
                
                # METHOD 3: JavaScript with proper event sequencing
                if not drag_success:
                    print("\n   🔄 METHOD 3: JavaScript Enhanced Events...")
                    try:
                        print("      Injecting JavaScript drag handler...")
                        js_drag = """
                        async (element, distance) => {
                            console.log('[JS DRAG] Starting...');
                            const rect = element.getBoundingClientRect();
                            const startX = rect.left + rect.width / 2;
                            const startY = rect.top + rect.height / 2;
                            const endX = startX + distance;

                            console.log(`[JS DRAG] Start: (${startX}, ${startY}), End: (${endX}, ${startY}), Distance: ${distance}`);

                            function sleep(ms) {
                                return new Promise(resolve => setTimeout(resolve, ms));
                            }

                            function fireEvent(type, x, y, buttons = 0) {
                                const evt = new MouseEvent(type, {
                                    view: window,
                                    bubbles: true,
                                    cancelable: true,
                                    clientX: x,
                                    clientY: y,
                                    screenX: x,
                                    screenY: y,
                                    button: 0,
                                    buttons: buttons,
                                    detail: type === 'click' ? 1 : 0
                                });
                                const target = type.includes('down') || type.includes('up') || type.includes('move') ? element : document;
                                target.dispatchEvent(evt);
                                console.log(`[JS DRAG] ${type} at (${x}, ${y})`);
                            }

                            // Sequence seperti manual drag
                            console.log('[JS DRAG] Phase 1: mouseenter/mouseover');
                            fireEvent('mouseenter', startX, startY);
                            await sleep(50);
                            fireEvent('mouseover', startX, startY);
                            await sleep(50);

                            console.log('[JS DRAG] Phase 2: mousedown');
                            fireEvent('mousedown', startX, startY, 1);
                            await sleep(100);

                            // Move with smooth steps
                            console.log('[JS DRAG] Phase 3: dragging...');
                            const steps = 20;
                            for (let i = 1; i <= steps; i++) {
                                const x = startX + (distance * i / steps);
                                fireEvent('mousemove', x, startY, 1);
                                await sleep(15);
                            }

                            console.log('[JS DRAG] Phase 4: mouseup');
                            await sleep(100);
                            fireEvent('mouseup', endX, startY, 0);
                            await sleep(50);
                            fireEvent('click', endX, startY, 0);

                            console.log('[JS DRAG] Completed!');
                            return 'Success';
                        }
                        """
                        result = page.evaluate(js_drag, slider_element, slide_distance)
                        print(f"      ✅ JavaScript result: {result}")
                        drag_success = True
                        time.sleep(2)
                    except Exception as e3:
                        print(f"      ❌ Method 3 failed: {str(e3)[:100]}")
                
                # METHOD 4: Simple hover + click and drag (fallback terakhir)
                if not drag_success:
                    print("\n   🔄 METHOD 4: Simple Hover + Hold + Move...")
                    try:
                        print("      Hover to element...")
                        slider_element.hover()
                        time.sleep(0.5)

                        print("      Hold and drag...")
                        page.mouse.down()
                        time.sleep(0.3)

                        # Move relative from current position
                        for step in range(1, 26):
                            offset = (slide_distance / 25) * step
                            page.mouse.move(start_x + offset, start_y)
                            time.sleep(0.02)

                        page.mouse.up()
                        print("      ✅ Method 4 executed")
                        drag_success = True
                        time.sleep(2)
                    except Exception as e4:
                        print(f"      ❌ Method 4 failed: {str(e4)[:100]}")

                if not drag_success:
                    print("\n   ❌ Semua 4 method drag gagal!")
                    print("   💡 Slider mungkin menggunakan custom event handler")
                    continue

                # VERIFIKASI: Cek apakah berhasil
                print("\n   🔍 Verifikasi hasil drag...")
                time.sleep(1)

                try:
                    # Cek apakah modal captcha hilang
                    page.wait_for_selector("text=Cocokan Gambar untuk Proses Keamanan", state="hidden", timeout=3000)
                    print("\n" + "="*60)
                    print("✅ CAPTCHA BERHASIL DISELESAIKAN!")
                    print("="*60)
                    return True
                except:
                    print(f"   ❌ Puzzle belum cocok (attempt {attempt}/{max_attempts})")

                    # Screenshot hasil attempt
                    try:
                        page.screenshot(path=f"captcha_failed_{attempt}.png")
                        print(f"   📸 Screenshot: captcha_failed_{attempt}.png")
                    except:
                        pass

                    # Refresh puzzle untuk attempt berikutnya
                    try:
                        ganti_btn = page.locator("text=Ganti").first
                        if ganti_btn.is_visible(timeout=1000):
                            print("   🔄 Refresh puzzle untuk attempt berikutnya...")
                            ganti_btn.click()
                            time.sleep(2)
                    except:
                        print("   ⚠️ Tombol 'Ganti' tidak ditemukan")

                    continue
                    
            except Exception as e:
                print(f"⚠️ Error pada attempt {attempt}: {e}")
                import traceback
                traceback.print_exc()
                time.sleep(1)
                continue
        
        print("❌ GAGAL menyelesaikan captcha setelah semua percobaan")
        return False
    
    print("\n🔵 Step 10: Menyelesaikan JIGSAW CAPTCHA...")

    # ============================================================
    # MODE CAPTCHA - PILIH SALAH SATU
    # ============================================================
    # "AUTO"  = Auto-solve dengan 4 drag methods + Computer Vision
    # "SEMI"  = Pause untuk manual solve, lanjut otomatis
    # "DEBUG" = Pause dan screenshot untuk inspect element
    # ============================================================
    CAPTCHA_MODE = "AUTO"  # ← EDIT DI SINI
    # ============================================================

    print(f"\n⚙️  Mode CAPTCHA: {CAPTCHA_MODE}\n")
    
    if CAPTCHA_MODE == "SEMI":
        print("\n" + "="*70)
        print("🤝 MODE SEMI-MANUAL AKTIF")
        print("="*70)
        print("Bot akan PAUSE saat captcha muncul.")
        print("")
        print("INSTRUKSI:")
        print("1. Geser tombol hijau MANUAL sampai puzzle cocok")
        print("2. Tunggu sampai modal captcha hilang")
        print("3. Tekan 'Resume' di Playwright Inspector")
        print("4. Bot akan lanjut otomatis setelah captcha selesai")
        print("="*70 + "\n")
        
        # Tunggu captcha muncul
        time.sleep(3)
        try:
            if page.locator("text=Cocokan Gambar untuk Proses Keamanan").is_visible(timeout=2000):
                print("🧩 Captcha detected! Silakan solve MANUAL...")
                print("   Geser tombol hijau sampai puzzle cocok, lalu tekan 'Resume'\n")
                
                # Screenshot untuk referensi
                page.screenshot(path="captcha_manual.png")
                print("📸 Screenshot: captcha_manual.png")
                
                # PAUSE - user solve manual
                page.pause()
                
                # Setelah resume, verifikasi captcha hilang
                try:
                    page.wait_for_selector("text=Cocokan Gambar untuk Proses Keamanan", state="hidden", timeout=2000)
                    print("✅ Captcha berhasil diselesaikan (manual)!")
                except:
                    print("⚠️ Captcha mungkin masih ada, tapi lanjut...")
        except:
            pass
    
    elif CAPTCHA_MODE == "AUTO":
        # Panggil fungsi jigsaw captcha solver
        if not solve_jigsaw_captcha(page):
            print("❌ AUTO-SOLVE GAGAL - Switching ke manual...")
            print("\n⏸️ Silakan solve captcha MANUAL, lalu tekan 'Resume'")
            page.pause()
        else:
            print("✅ Captcha berhasil diselesaikan (auto)!")
    
    elif CAPTCHA_MODE == "DEBUG":
        print("\n🔍 DEBUG MODE - Inspect captcha element")
        time.sleep(2)
        page.screenshot(path="captcha_debug.png")
        print("📸 Screenshot: captcha_debug.png")
        page.pause()
    
    print("\n🔵 Step 11: Lanjut setelah captcha...")
    time.sleep(2)
    
    # Tunggu dan handle berbagai kemungkinan setelah captcha
    try:
        # Kemungkinan 1: Ada tombol "Ke Beranda"
        if page.locator("text=Ke Beranda").is_visible(timeout=5000):
            print("✅ Transaksi berhasil - tombol 'Ke Beranda' muncul")
            page.get_by_role("link", name="Ke Beranda").click()
            print("✅ Kembali ke beranda")
            time.sleep(2)
        
        # Kemungkinan 2: Ada modal sukses atau konfirmasi lain
        elif page.locator("text=berhasil, text=sukses").first.is_visible(timeout=3000):
            print("✅ Modal sukses terdeteksi")
            time.sleep(1)
        
        # Kemungkinan 3: Sudah langsung kembali ke halaman sebelumnya
        else:
            print("⚠️ Tidak ada konfirmasi jelas, cek URL...")
            print(f"📍 URL saat ini: {page.url}")
            
            # List semua button dan link yang terlihat
            print("\n📋 Elemen yang terlihat di halaman:")
            try:
                buttons = page.locator("button").all()
                for i, btn in enumerate(buttons[:10]):  # Max 10 button
                    if btn.is_visible():
                        text = btn.inner_text()[:50] if btn.inner_text() else "[No text]"
                        print(f"  Button {i+1}: {text}")
            except:
                pass
            
            time.sleep(2)
    except Exception as e:
        print(f"⚠️ Warning saat tunggu konfirmasi: {e}")
        print(f"📍 URL saat ini: {page.url}")
    
    print("✅ TRANSAKSI SELESAI!")
    
    # Tunggu sebentar agar bisa dilihat hasilnya
    print("\n⏳ Tunggu 10 detik sebelum tutup browser...")
    time.sleep(10)

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
