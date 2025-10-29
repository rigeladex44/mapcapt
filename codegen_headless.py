"""
MAPCAPT - Auto CAPTCHA Solver (HEADLESS MODE)
==============================================

Versi untuk testing di Codespace/Server tanpa GUI
- Headless mode enabled
- Video recording untuk debugging
- Screenshot setiap step
- Detailed console logging

USAGE:
1. pip install playwright pillow
2. playwright install chromium
3. Edit credentials di line 44-48
4. python codegen_headless.py
5. Check output: video.webm dan screenshots

"""
import re
import time
from playwright.sync_api import Playwright, sync_playwright
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

    # ============================================================

    print("\n" + "="*60)
    print("🤖 MAPCAPT - Auto CAPTCHA Solver (HEADLESS)")
    print("="*60)
    print(f"Email: {EMAIL}")
    print(f"Mode: Headless + Video Recording")
    print("="*60 + "\n")

    # Launch with video recording
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        record_video_dir="./videos",
        record_video_size={"width": 1280, "height": 720}
    )
    page = context.new_page()

    # Enable console logging
    page.on("console", lambda msg: print(f"🌐 Browser Console: {msg.text}"))

    try:
        print("🔵 Step 1: Buka halaman login...")
        page.goto("https://subsiditepatlpg.mypertamina.id/merchant-login", timeout=30000)
        page.screenshot(path="step1_login_page.png")
        print("   📸 Screenshot: step1_login_page.png")

        print("🔵 Step 2: Isi email...")
        page.get_by_role("textbox", name="Nomor Ponsel atau Email").fill(EMAIL)
        time.sleep(2)

        print("🔵 Step 3: Isi PIN...")
        page.get_by_role("textbox", name="PIN").fill(PIN)
        page.screenshot(path="step3_credentials_filled.png")
        print("   📸 Screenshot: step3_credentials_filled.png")

        print("🔵 Step 4: Klik tombol MASUK...")
        page.get_by_role("button", name="MASUK").click()
        time.sleep(3)
        page.screenshot(path="step4_after_login.png")
        print("   📸 Screenshot: step4_after_login.png")

        print("🔵 Step 5: Klik Catat Penjualan...")
        page.locator("div").filter(has_text=re.compile(r"^Catat Penjualan$")).first.click()
        time.sleep(2)
        page.screenshot(path="step5_catat_penjualan.png")
        print("   📸 Screenshot: step5_catat_penjualan.png")

        print(f"🔵 Step 6: Isi NIK ({TEST_NIK})...")
        page.get_by_role("combobox", name="Masukkan 16 digit NIK").fill(TEST_NIK)
        page.screenshot(path="step6_nik_filled.png")
        print("   📸 Screenshot: step6_nik_filled.png")

        print("🔵 Step 7: Klik LANJUTKAN PENJUALAN...")
        page.get_by_role("button", name="LANJUTKAN PENJUALAN").click()
        time.sleep(2)
        page.screenshot(path="step7_lanjutkan.png")
        print("   📸 Screenshot: step7_lanjutkan.png")

        print("🔵 Step 8: Klik btnCheckOrder...")
        page.get_by_test_id("btnCheckOrder").click()
        time.sleep(2)
        page.screenshot(path="step8_check_order.png")
        print("   📸 Screenshot: step8_check_order.png")

        print("🔵 Step 9: Klik btnPay...")
        page.get_by_test_id("btnPay").click()
        time.sleep(3)
        page.screenshot(path="step9_before_captcha.png")
        print("   📸 Screenshot: step9_before_captcha.png")

        print("\n🔵 Step 10: Deteksi CAPTCHA...")

        # Check if CAPTCHA exists
        captcha_found = False
        try:
            if page.locator("text=Cocokan Gambar untuk Proses Keamanan").is_visible(timeout=5000):
                captcha_found = True
                print("   ✅ CAPTCHA TERDETEKSI!")
                page.screenshot(path="captcha_detected.png")
                print("   📸 Screenshot: captcha_detected.png")
        except:
            print("   ℹ️  Tidak ada CAPTCHA")

        if captcha_found:
            print("\n" + "="*60)
            print("🧩 CAPTCHA ANALYSIS")
            print("="*60)

            # Analyze captcha elements
            print("\n   🔍 Mencari elemen slider...")

            slider_selectors = [
                "button[class*='slider']",
                "button[class*='Slider']",
                "button[id*='slider']",
                "button:has(svg)",
                "div[class*='slider-button']",
                "div[class*='sliderButton']",
                "div[class*='captcha-slider']",
                "div[class*='drag-button']",
                "[draggable='true']",
                "[role='slider']",
            ]

            slider_element = None
            for idx, selector in enumerate(slider_selectors, 1):
                try:
                    print(f"      Coba selector #{idx}: {selector}")
                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=500):
                        slider_element = elem
                        print(f"      ✅ DITEMUKAN: {selector}")

                        # Get element info
                        try:
                            tag = elem.evaluate("el => el.tagName")
                            classes = elem.evaluate("el => el.className")
                            elem_id = elem.evaluate("el => el.id")
                            print(f"         Tag: {tag}")
                            print(f"         Class: {classes}")
                            print(f"         ID: {elem_id}")
                        except:
                            pass
                        break
                except Exception as e:
                    print(f"      ✗ Gagal: {str(e)[:50]}")

            if not slider_element:
                print("\n   ❌ Slider tidak ditemukan!")
                print("   💡 Check captcha_detected.png untuk inspect element")

                # Dump all visible elements
                print("\n   📋 DEBUG: Mencari element yang visible...")
                try:
                    all_buttons = page.locator("button").all()
                    visible_count = 0
                    for btn in all_buttons[:20]:
                        try:
                            if btn.is_visible():
                                classes = btn.evaluate("el => el.className") or "[no class]"
                                print(f"      • BUTTON: {classes[:60]}")
                                visible_count += 1
                                if visible_count >= 10:
                                    break
                        except:
                            continue
                except Exception as e:
                    print(f"      Error dump: {e}")

            else:
                # Try drag in headless mode
                print("\n   🎯 Mencoba auto-drag di headless mode...")

                box = slider_element.bounding_box()
                if box:
                    print(f"      Position: X={box['x']}, Y={box['y']}")
                    print(f"      Size: W={box['width']}, H={box['height']}")

                    start_x = box['x'] + box['width'] / 2
                    start_y = box['y'] + box['height'] / 2
                    distance = 260

                    print(f"\n      🔄 METHOD: CDP Mouse Drag")
                    print(f"         Start: ({int(start_x)}, {int(start_y)})")
                    print(f"         Distance: {distance}px")

                    try:
                        page.mouse.move(start_x, start_y)
                        time.sleep(0.3)
                        page.mouse.down()
                        time.sleep(0.2)

                        # Smooth drag
                        steps = 25
                        for i in range(1, steps + 1):
                            current_x = start_x + (distance * i / steps)
                            page.mouse.move(current_x, start_y)
                            time.sleep(0.02)

                        time.sleep(0.2)
                        page.mouse.up()
                        print("         ✅ Drag executed")
                        time.sleep(2)

                        page.screenshot(path="captcha_after_drag.png")
                        print("      📸 Screenshot: captcha_after_drag.png")

                        # Check if solved
                        try:
                            page.wait_for_selector("text=Cocokan Gambar untuk Proses Keamanan", state="hidden", timeout=3000)
                            print("\n   ✅ CAPTCHA BERHASIL DISELESAIKAN!")
                        except:
                            print("\n   ❌ CAPTCHA masih ada (puzzle tidak cocok)")
                            print("   💡 Check captcha_after_drag.png untuk lihat hasilnya")

                    except Exception as e:
                        print(f"      ❌ Drag failed: {e}")

        print("\n🔵 Step 11: Tunggu konfirmasi...")
        time.sleep(3)
        page.screenshot(path="final_result.png")
        print("   📸 Screenshot: final_result.png")

        # Check for success indicators
        try:
            if page.locator("text=Ke Beranda").is_visible(timeout=3000):
                print("\n✅ TRANSAKSI BERHASIL!")
                print("   Tombol 'Ke Beranda' terdeteksi")
            else:
                print("\nℹ️  Status transaksi tidak jelas")
                print(f"   Current URL: {page.url}")
        except:
            print("\nℹ️  Tidak ada konfirmasi jelas")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        try:
            page.screenshot(path="error_screenshot.png")
            print("📸 Error screenshot: error_screenshot.png")
        except:
            pass

    finally:
        print("\n" + "="*60)
        print("📹 Closing browser and saving video...")
        print("="*60)

        # Close context to save video
        context.close()
        browser.close()

        print("\n✅ DONE!")
        print("\nOutput files:")
        print("  - videos/*.webm (video recording)")
        print("  - step*.png (screenshots setiap step)")
        print("  - captcha*.png (screenshots captcha)")
        print("  - final_result.png (hasil akhir)")
        print("\n" + "="*60)


if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)
