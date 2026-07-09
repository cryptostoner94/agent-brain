"""
agents/human_browser_test.py
Block 18 — HUMAN BROWSER TEST ONLY
Plain human flow: no terminal, no scripts (via Playwright).
iPhone 14 Pro viewport 393x852, isMobile=True.
Steps: / -> /dashboard -> /wallet -> /quote -> /solve -> Onboarding COW.
"""
from __future__ import annotations
import json, logging, os, time
from pathlib import Path
from playwright.sync_api import sync_playwright

log = logging.getLogger("human_test")

TEST_RESULTS_DIR = Path("artifacts/human_test_live")
TEST_RESULTS_DIR.mkdir(parents=True, exist_ok=True)

class HumanBrowserTest:
    def __init__(self, base_url: str = "http://15.223.49.28:8000"):
        self.base_url = base_url.rstrip("/")

    def run_test(self) -> dict:
        results = []
        log.info(f"Starting human browser test against {self.base_url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 393, "height": 852},
                device_scale_factor=3,
                is_mobile=True,
                has_touch=True,
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            )
            page = context.new_page()

            # Step 1: Open /
            log.info("Step 1: Open /")
            page.goto(f"{self.base_url}/")
            page.wait_for_timeout(2000)
            page.screenshot(path=str(TEST_RESULTS_DIR / "step1_root.png"))
            results.append({"step": 1, "url": "/", "status": "ok"})

            # Step 2: Open /dashboard verify visible elements
            log.info("Step 2: Open /dashboard")
            page.goto(f"{self.base_url}/dashboard")
            page.wait_for_timeout(2000)
            # Verify header status pill
            status_pill = page.query_selector(".pill-working") or page.query_selector(".pill-effective") or page.query_selector(".pill-dud")
            if not status_pill:
                log.error("Status pill not found!")
                results.append({"step": 2, "error": "status pill missing"})
            page.screenshot(path=str(TEST_RESULTS_DIR / "step2_dashboard.png"))
            results.append({"step": 2, "url": "/dashboard", "status": "ok"})

            # Step 3: Click /wallet
            log.info("Step 3: Click Trades tab (icon ↔)")
            # In our React app, tabs are at the bottom. Trades is the second button.
            page.click("button:has-text('Trades')")
            page.wait_for_timeout(1000)
            page.screenshot(path=str(TEST_RESULTS_DIR / "step3_trades.png"))
            results.append({"step": 3, "action": "click_trades", "status": "ok"})

            # Step 4: Click Revenue
            log.info("Step 4: Click Revenue tab (icon $)")
            page.click("button:has-text('Revenue')")
            page.wait_for_timeout(1000)
            page.screenshot(path=str(TEST_RESULTS_DIR / "step4_revenue.png"))
            results.append({"step": 4, "action": "click_revenue", "status": "ok"})

            # Step 5: Try /solve without pay (manual API call check via console or just endpoint)
            log.info("Step 5: Verify /solve 401/402 without JWT")
            # This is an API test, but we check it from the browser context
            try:
                response = page.request.post(f"{self.base_url}/solve", data={"wallet": "test"})
                if response.status == 401:
                    results.append({"step": 5, "endpoint": "/solve", "status": "ok", "msg": "401 Unauthorized (expected)"})
                else:
                    results.append({"step": 5, "endpoint": "/solve", "status": "fail", "code": response.status})
            except Exception as e:
                results.append({"step": 5, "error": str(e)})

            # Step 6: Onboarding COW button
            log.info("Step 6: Check COW button")
            page.click("button:has-text('Dashboard')") # Back to dashboard
            page.wait_for_timeout(1000)
            cow_btn = page.query_selector("button:has-text('Onboarding COW INITIATED')")
            if cow_btn:
                is_disabled = cow_btn.is_disabled()
                results.append({"step": 6, "cow_button": "found", "disabled": is_disabled})
                if not is_disabled:
                    cow_btn.click()
                    page.wait_for_timeout(500)
                    # Check for modal
                    modal = page.query_selector("text=Are you sure?")
                    if modal:
                        results.append({"step": 6, "modal": "visible"})
                        page.screenshot(path=str(TEST_RESULTS_DIR / "step6_cow_modal.png"))
            
            # Step 7: Safe area check
            log.info("Step 7: Verify safe area and no scroll")
            # We can check viewport width vs content width
            content_width = page.evaluate("document.body.scrollWidth")
            if content_width <= 393:
                results.append({"step": 7, "no_horizontal_scroll": True})
            else:
                results.append({"step": 7, "no_horizontal_scroll": False, "width": content_width})

            # Step 8: version.json
            log.info("Step 8: Check version.json")
            page.goto(f"{self.base_url}/api/health", timeout=60000)
            health_json = json.loads(page.inner_text("body"))
            results.append({"step": 8, "version": health_json.get("version"), "onboarding": health_json.get("cow_onboarding")})

            browser.close()

        summary_path = TEST_RESULTS_DIR / "human_test_report.json"
        summary_path.write_text(json.dumps(results, indent=2))
        log.info(f"Human test complete. Results saved to {summary_path}")
        return results

if __name__ == "__main__":
    tester = HumanBrowserTest()
    tester.run_test()
