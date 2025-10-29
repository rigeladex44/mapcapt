import re
import time
from playwright.sync_api import Playwright, sync_playwright, expect
from PIL import Image
import io


def run(playwright: Playwright) -> None:
    # PENTING: Jangan gunakan slow_mo karena bisa interferensi dengan drag
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    
    # Enable console logging
    page.on("console", lambda msg: print(f"🌐 Browser: {msg.text}"))
    
    print("🔵 Step 1: Buka halaman login...")
    page.goto("https://subsiditepatlpg.mypertamina.id/merchant-login")
    
    print("🔵 Step 2: Isi email...")
    page.get_by_role("textbox", name="Nomor Ponsel atau Email").fill("irma_lpg@digdig.org")
    time.sleep(2)
    
    print("🔵 Step 3: Isi PIN...")
    page.get_by_role("textbox", name="PIN").fill("401001")
    
    print("🔵 Step 4: Klik tombol MASUK...")
    page.get_by_role("button", name="MASUK").click()
    time.sleep(2)
    
    print("🔵 Step 5: Klik Catat Penjualan...")
    page.locator("div").filter(has_text=re.compile(r"^Catat Penjualan$")).first.click()
    time.sleep(2)
    
    print("🔵 Step 6: Isi NIK...")
    page.get_by_role("combobox", name="Masukkan 16 digit NIK").fill("3573045005800001")
    
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
                print(f"🧩 Attempt {attempt}/{max_attempts}: Mencoba selesaikan jigsaw captcha...")
                
                # Tunggu modal captcha muncul
                captcha_modal = page.locator("text=Cocokan Gambar untuk Proses Keamanan").first
                if not captcha_modal.is_visible(timeout=3000):
                    print("✅ Captcha tidak muncul, lanjut...")
                    return True
                
                time.sleep(2)
                
                # STRATEGI 1: Cari tombol hijau dengan berbagai cara
                slider_element = None
                slider_selectors = [
                    "button[class*='slider']",  # Button dengan class slider
                    "div[class*='slider-button']",  # Div slider button
                    "div[class*='captcha-slider']",  # Captcha slider
                    "[class*='rc-slider-captcha-slider']",  # RC slider
                    "button:has(svg)",  # Button dengan icon SVG (tombol hijau)
                    "div:has-text('Geser ke kanan')",  # Div dengan text geser
                ]
                
                print("   🔍 Mencari elemen slider...")
                for selector in slider_selectors:
                    try:
                        elem = page.locator(selector).first
                        if elem.is_visible(timeout=500):
                            slider_element = elem
                            print(f"   ✓ Ditemukan: {selector}")
                            break
                    except:
                        continue
                
                if not slider_element:
                    print("   ⚠️ Slider tidak ditemukan, skip attempt ini")
                    continue
                
                slider_box = slider_element.bounding_box()
                if not slider_box:
                    print("   ⚠️ Tidak bisa dapatkan bounding box slider")
                    continue
                
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
                    distance_strategies = [250, 270, 230, 290, 210, 280]
                    slide_distance = distance_strategies[min(attempt - 3, len(distance_strategies) - 1)]
                    print(f"   📏 Jarak drag attempt {attempt}: {slide_distance}px")
                
                # STRATEGI 3: Advanced Multi-Method Drag (paling mirip manual)
                start_x = slider_box['x'] + slider_box['width'] / 2
                start_y = slider_box['y'] + slider_box['height'] / 2
                end_x = start_x + slide_distance
                
                drag_success = False
                
                # METHOD 1: Locator.drag_to dengan source & target position
                print("   🎯 Method 1: Locator.drag_to...")
                try:
                    slider_element.drag_to(
                        page.locator("body"),
                        source_position={"x": slider_box['width'] / 2, "y": slider_box['height'] / 2},
                        target_position={"x": end_x, "y": start_y}
                    )
                    print("   ✓ Drag_to berhasil")
                    drag_success = True
                    time.sleep(2)
                except Exception as e1:
                    print(f"   ✗ Method 1 gagal: {e1}")
                
                # METHOD 2: CDP-level mouse events (jika method 1 gagal)
                if not drag_success:
                    print("   🎯 Method 2: CDP Mouse Commands...")
                    try:
                        # Hover first
                        page.mouse.move(start_x, start_y)
                        time.sleep(0.3)
                        
                        # Press and hold
                        page.mouse.down()
                        time.sleep(0.2)
                        
                        # Move to target with multiple steps (smooth like human)
                        steps = 25
                        for i in range(1, steps + 1):
                            current_x = start_x + (slide_distance * i / steps)
                            page.mouse.move(current_x, start_y)
                            time.sleep(0.015)
                        
                        # Release
                        time.sleep(0.2)
                        page.mouse.up()
                        print("   ✓ CDP mouse drag berhasil")
                        drag_success = True
                        time.sleep(2)
                    except Exception as e2:
                        print(f"   ✗ Method 2 gagal: {e2}")
                
                # METHOD 3: JavaScript with proper event sequencing
                if not drag_success:
                    print("   🎯 Method 3: JavaScript Enhanced Events...")
                    try:
                        js_drag = """
                        async (element, distance) => {
                            const rect = element.getBoundingClientRect();
                            const startX = rect.left + rect.width / 2;
                            const startY = rect.top + rect.height / 2;
                            const endX = startX + distance;
                            
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
                                (type.includes('down') || type.includes('up') || type.includes('move')) 
                                    ? element.dispatchEvent(evt) 
                                    : document.dispatchEvent(evt);
                            }
                            
                            // Sequence seperti manual drag
                            fireEvent('mouseenter', startX, startY);
                            await sleep(50);
                            fireEvent('mouseover', startX, startY);
                            await sleep(50);
                            fireEvent('mousedown', startX, startY, 1);
                            await sleep(100);
                            
                            // Move with smooth steps
                            const steps = 20;
                            for (let i = 1; i <= steps; i++) {
                                const x = startX + (distance * i / steps);
                                fireEvent('mousemove', x, startY, 1);
                                await sleep(15);
                            }
                            
                            await sleep(100);
                            fireEvent('mouseup', endX, startY, 0);
                            await sleep(50);
                            fireEvent('click', endX, startY, 0);
                            
                            return 'Success';
                        }
                        """
                        result = page.evaluate(js_drag, slider_element, slide_distance)
                        print(f"   ✓ {result}")
                        drag_success = True
                        time.sleep(2)
                    except Exception as e3:
                        print(f"   ✗ Method 3 gagal: {e3}")
                
                if not drag_success:
                    print("   ❌ Semua method drag gagal, skip...")
                    continue
                
                # VERIFIKASI: Cek apakah berhasil
                try:
                    page.wait_for_selector("text=Cocokan Gambar untuk Proses Keamanan", state="hidden", timeout=3000)
                    print("✅ CAPTCHA BERHASIL DISELESAIKAN!")
                    return True
                except:
                    print(f"   ❌ Belum cocok, mencoba jarak lain...")
                    
                    # Refresh puzzle untuk attempt berikutnya
                    try:
                        ganti_btn = page.locator("text=Ganti").first
                        if ganti_btn.is_visible(timeout=1000):
                            print("   🔄 Refresh puzzle...")
                            ganti_btn.click()
                            time.sleep(2)
                    except:
                        # Jika tombol Ganti tidak ada, mungkin perlu reload modal
                        pass
                    
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
    
    # MODE CAPTCHA:
    # "AUTO" = Coba auto-solve dengan CV + multi-strategy (3 drag methods)
    # "SEMI" = Pause, user solve manual, lanjut auto
    # "DEBUG" = Pause untuk inspect
    CAPTCHA_MODE = "AUTO"  # ← Set AUTO untuk test geser otomatis
    
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
