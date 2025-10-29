"""
MAPCAPT Inspector - Dry Run Element Detection
==============================================

Script ini HANYA untuk inspect CAPTCHA element tanpa execute full automation.
Berguna untuk quick check apakah selector bisa detect slider.

USAGE:
1. pip install playwright
2. playwright install chromium
3. Edit URL di line 20 (atau gunakan default)
4. python inspector.py

OUTPUT:
- Console log: element detection results
- Screenshot: captcha_inspection.png
- Tidak ada automation/transaction
"""

from playwright.sync_api import sync_playwright
import time


def inspect_captcha():
    # ============================================================
    # KONFIGURASI
    # ============================================================
    # Default: halaman dengan CAPTCHA (setelah login manual)
    # Atau ganti dengan URL direct ke halaman yang ada CAPTCHA
    TARGET_URL = "https://subsiditepatlpg.mypertamina.id/merchant/app/verification-nik"

    # Mode
    HEADLESS = False  # False = browser visible untuk inspect
    # ============================================================

    print("\n" + "="*60)
    print("🔍 MAPCAPT INSPECTOR - Element Detection")
    print("="*60)
    print(f"Target: {TARGET_URL}")
    print(f"Mode: {'Headless' if HEADLESS else 'Visible Browser'}")
    print("="*60 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context()
        page = context.new_page()

        try:
            print("📍 Step 1: Navigating to page...")
            print("   (Jika perlu login, silakan login manual di browser yang terbuka)")
            print("   Script akan wait 30 detik untuk Anda login manual...\n")

            page.goto(TARGET_URL, timeout=30000)

            # Wait for manual login if needed
            print("⏳ Waiting 30 seconds...")
            print("   - Jika ada login page, silakan login manual")
            print("   - Jika sudah login, navigate ke page yang ada CAPTCHA")
            print("   - Script akan otomatis lanjut setelah 30 detik\n")

            time.sleep(30)

            print("📸 Taking screenshot...")
            page.screenshot(path="page_before_inspection.png")
            print("   ✅ Saved: page_before_inspection.png\n")

            # =========================================================
            # CAPTCHA DETECTION
            # =========================================================
            print("\n" + "="*60)
            print("🧩 CAPTCHA DETECTION")
            print("="*60)

            captcha_indicators = [
                "text=Cocokan Gambar untuk Proses Keamanan",
                "text=Cocokan Gambar",
                "text=Verifikasi",
                "text=Captcha",
                "[class*='captcha']",
                "[id*='captcha']",
            ]

            captcha_found = False
            for indicator in captcha_indicators:
                try:
                    if page.locator(indicator).first.is_visible(timeout=2000):
                        print(f"   ✅ CAPTCHA FOUND: {indicator}")
                        captcha_found = True
                        break
                except:
                    print(f"   ✗ Not found: {indicator}")

            if not captcha_found:
                print("\n   ⚠️  CAPTCHA NOT DETECTED")
                print("   💡 Tips:")
                print("      - Pastikan sudah di halaman yang memunculkan CAPTCHA")
                print("      - Trigger CAPTCHA secara manual (submit form, dll)")
                print("      - Run script ini lagi setelah CAPTCHA muncul")

                print("\n📸 Taking final screenshot...")
                page.screenshot(path="no_captcha_found.png")
                print("   ✅ Saved: no_captcha_found.png")

                browser.close()
                return

            # CAPTCHA found, proceed to inspect
            print("\n" + "="*60)
            print("🔍 SLIDER ELEMENT DETECTION")
            print("="*60 + "\n")

            page.screenshot(path="captcha_detected_inspection.png")
            print("📸 Saved: captcha_detected_inspection.png\n")

            slider_selectors = [
                # Button selectors
                ("button[class*='slider']", "Button with 'slider' class"),
                ("button[class*='Slider']", "Button with 'Slider' class"),
                ("button[id*='slider']", "Button with 'slider' id"),
                ("button:has(svg)", "Button containing SVG"),

                # Div selectors
                ("div[class*='slider-button']", "Div slider-button"),
                ("div[class*='sliderButton']", "Div sliderButton"),
                ("div[class*='captcha-slider']", "Div captcha-slider"),
                ("div[class*='drag-button']", "Div drag-button"),
                ("div[class*='dragButton']", "Div dragButton"),

                # Span selectors
                ("span[class*='slider']", "Span slider"),
                ("span[class*='drag']", "Span drag"),

                # Generic draggable
                ("[draggable='true']", "Draggable element"),
                ("[role='slider']", "Role=slider"),

                # RC Captcha
                ("[class*='rc-slider']", "RC slider"),
                (".rc-slider-handle", "RC slider handle"),

                # Text-based
                ("div:has-text('Geser')", "Div with 'Geser' text"),
                ("button:has-text('Geser')", "Button with 'Geser' text"),
            ]

            found_elements = []

            for idx, (selector, description) in enumerate(slider_selectors, 1):
                try:
                    print(f"   Trying #{idx}: {description}")
                    print(f"      Selector: {selector}")

                    elem = page.locator(selector).first
                    if elem.is_visible(timeout=500):
                        print(f"      ✅ FOUND and VISIBLE!")

                        # Get element details
                        try:
                            tag = elem.evaluate("el => el.tagName")
                            classes = elem.evaluate("el => el.className") or "[no class]"
                            elem_id = elem.evaluate("el => el.id") or "[no id]"
                            box = elem.bounding_box()

                            print(f"      📋 Details:")
                            print(f"         Tag: {tag}")
                            print(f"         Class: {classes}")
                            print(f"         ID: {elem_id}")
                            if box:
                                print(f"         Position: X={box['x']}, Y={box['y']}")
                                print(f"         Size: W={box['width']}, H={box['height']}")

                            found_elements.append({
                                'selector': selector,
                                'description': description,
                                'tag': tag,
                                'class': classes,
                                'id': elem_id,
                                'box': box
                            })

                            # Highlight element (optional)
                            try:
                                elem.evaluate("""el => {
                                    el.style.border = '3px solid red';
                                    el.style.boxShadow = '0 0 10px red';
                                }""")
                            except:
                                pass

                        except Exception as e:
                            print(f"      ⚠️  Found but error getting details: {e}")

                        print()
                    else:
                        print(f"      ✗ Not visible")
                        print()

                except Exception as e:
                    print(f"      ✗ Error: {str(e)[:60]}")
                    print()

            # Summary
            print("\n" + "="*60)
            print("📊 DETECTION SUMMARY")
            print("="*60)

            if found_elements:
                print(f"\n✅ Found {len(found_elements)} slider element(s)!\n")

                for idx, elem in enumerate(found_elements, 1):
                    print(f"Element #{idx}:")
                    print(f"  Selector: {elem['selector']}")
                    print(f"  Tag: {elem['tag']}")
                    print(f"  Class: {elem['class']}")
                    print(f"  ID: {elem['id']}")
                    if elem['box']:
                        print(f"  Position: ({elem['box']['x']}, {elem['box']['y']})")
                    print()

                print("💡 RECOMMENDED ACTION:")
                print(f"   Use this selector in codegen.py:")
                print(f"   '{found_elements[0]['selector']}'")
                print()

                # Take screenshot with highlighted element
                page.screenshot(path="slider_detected_highlighted.png")
                print("📸 Screenshot with highlighted slider:")
                print("   ✅ Saved: slider_detected_highlighted.png")

            else:
                print("\n❌ NO SLIDER ELEMENT FOUND!\n")
                print("💡 TROUBLESHOOTING:")
                print("   1. Check captcha_detected_inspection.png")
                print("   2. Inspect element manually (F12 DevTools)")
                print("   3. Find the green slider button class/id")
                print("   4. Add custom selector to codegen.py")
                print()
                print("   Mencoba dump ALL buttons...")

                try:
                    all_buttons = page.locator("button").all()
                    print(f"\n   📋 Found {len(all_buttons)} button elements:")

                    for idx, btn in enumerate(all_buttons[:20], 1):
                        try:
                            if btn.is_visible():
                                classes = btn.evaluate("el => el.className") or "[no class]"
                                text = btn.inner_text()[:30] if btn.inner_text() else "[no text]"
                                print(f"      Button #{idx}: class='{classes[:50]}', text='{text}'")
                        except:
                            pass
                except Exception as e:
                    print(f"   Error dumping buttons: {e}")

            print("\n" + "="*60)
            print("✅ INSPECTION COMPLETE")
            print("="*60)
            print("\nGenerated files:")
            print("  - page_before_inspection.png")
            print("  - captcha_detected_inspection.png")
            if found_elements:
                print("  - slider_detected_highlighted.png")
            else:
                print("  - no_captcha_found.png (if captcha not detected)")
            print()

            # Keep browser open for manual inspection
            print("⏳ Browser akan tetap terbuka selama 60 detik")
            print("   untuk Anda inspect manual...")
            time.sleep(60)

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

            try:
                page.screenshot(path="error_inspection.png")
                print("📸 Error screenshot: error_inspection.png")
            except:
                pass

        finally:
            print("\n🔚 Closing browser...")
            browser.close()
            print("✅ Done!")


if __name__ == "__main__":
    inspect_captcha()
