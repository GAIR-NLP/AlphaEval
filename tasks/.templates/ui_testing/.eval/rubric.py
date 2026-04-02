#!/usr/bin/env python3
"""
Automated UI Testing Evaluation Template
Based on the actual AlphaEval miniprogram evaluation pipeline.

Architecture:
  1. Launch Playwright with mobile device emulation (iPhone 13)
  2. Navigate to the agent's running app
  3. For each rubric item, run a dedicated test function that:
     a. Performs UI interactions (click, fill, scroll)
     b. Takes screenshots at each step (for Vision LLM verification)
     c. Monitors network requests (4xx/5xx = rendering errors)
     d. Generates a structured test_report.json per rubric
  4. Optionally feed screenshots to Vision LLM (GPT-4o/Claude) for visual verification
  5. Aggregate scores across all rubrics

Requirements:
  pip install playwright pyyaml
  playwright install chromium

Output format (required):
    score=X.XX    (0.00 to 1.00)
    result=PASSED or result=FAILED
"""

import os
import sys
import json
import time
import argparse
import yaml
from pathlib import Path
from typing import Optional

try:
    from playwright.sync_api import sync_playwright, devices as pw_devices
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False


# ============================================================
# CONFIGURATION
# ============================================================

PASS_THRESHOLD = 0.6
DEFAULT_TIMEOUT = 30000       # ms per operation
NAVIGATION_TIMEOUT = 60000    # ms for page loads
DEVICE = "iPhone 13"          # Mobile device emulation
LOCALE = "zh-CN"
SCREENSHOT_QUALITY = 80       # JPEG quality (lower = smaller for Vision LLM)


# ============================================================
# ACTION MONITOR — Track network requests & console errors
# ============================================================

class ActionMonitor:
    """Monitors network health and console errors during UI testing."""

    def __init__(self, page):
        self.page = page
        self.logs = []
        self.network_issues = []
        self._setup_listeners()

    def _setup_listeners(self):
        self.page.on("console", lambda msg: self._on_console(msg))
        self.page.on("response", lambda resp: self._on_response(resp))
        self.page.on("pageerror", lambda err: self._on_error(err))

    def _on_console(self, msg):
        if msg.type in ("error", "warning"):
            self.logs.append({
                "timestamp": int(time.time() * 1000),
                "type": "console",
                "level": msg.type,
                "message": msg.text[:500],
            })

    def _on_response(self, response):
        if response.status >= 400:
            url = response.url
            # Flag critical resource failures
            is_critical = any(ext in url for ext in [".css", ".js", ".woff", ".png", ".jpg"])
            self.network_issues.append({
                "url": url[:200],
                "status": response.status,
                "critical": is_critical,
            })
            self.logs.append({
                "timestamp": int(time.time() * 1000),
                "type": "network_error",
                "level": "error" if is_critical else "warning",
                "message": f"HTTP {response.status}: {url[:100]}",
            })

    def _on_error(self, error):
        self.logs.append({
            "timestamp": int(time.time() * 1000),
            "type": "page_error",
            "level": "error",
            "message": str(error)[:500],
        })

    def get_logs(self):
        return self.logs

    def get_network_issues(self):
        return self.network_issues


# ============================================================
# SMART SCROLLER — Capture full-page screenshots for Vision LLM
# ============================================================

class SmartScroller:
    """Handles scrolling and full-page screenshots for SPA apps."""

    def __init__(self, page, artifacts_dir: str):
        self.page = page
        self.artifacts_dir = artifacts_dir

    def capture_screenshot(self, label: str = "") -> str:
        """Take a screenshot and save to artifacts directory.

        Returns the file path of the saved screenshot.
        """
        timestamp = int(time.time() * 1000)
        filename = f"screenshot_{label}_{timestamp}.jpg"
        filepath = os.path.join(self.artifacts_dir, filename)
        self.page.screenshot(path=filepath, type="jpeg", quality=SCREENSHOT_QUALITY)
        return filepath

    def scroll_and_capture(self) -> list:
        """Scroll through the page capturing screenshots for lazy-loaded content.

        Useful for SPA apps where content loads on scroll.
        Returns list of screenshot paths.
        """
        screenshots = []

        # Capture initial viewport
        screenshots.append(self.capture_screenshot("initial"))

        # Try scrolling the page
        prev_height = 0
        for i in range(5):  # Max 5 scroll iterations
            self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            self.page.wait_for_timeout(1000)

            current_height = self.page.evaluate("document.body.scrollHeight")
            if current_height == prev_height:
                break
            prev_height = current_height

            screenshots.append(self.capture_screenshot(f"scroll_{i}"))

        # Scroll back to top
        self.page.evaluate("window.scrollTo(0, 0)")
        return screenshots


# ============================================================
# RUBRIC TEST FUNCTIONS — One per feature to verify
# ============================================================

def test_rubric(page, monitor, scroller, rubric_item: dict, test_config: dict) -> dict:
    """Execute a single rubric test.

    This function dispatches to specific test logic based on the rubric's test_id.
    Each test follows the pattern:
      1. Navigate / interact
      2. Screenshot at each step
      3. Check expected outcome
      4. Return score (0.0 or 1.0) with screenshots and logs

    For custom tests, add a handler in the dispatch table below.
    """
    test_id = rubric_item.get("test_id", "default")
    test_steps = rubric_item.get("test_steps", [])
    artifacts_dir = os.path.join(scroller.artifacts_dir, f"rubric_{test_id}")
    os.makedirs(artifacts_dir, exist_ok=True)

    rubric_scroller = SmartScroller(page, artifacts_dir)
    result = {
        "test_id": test_id,
        "point": rubric_item.get("point", ""),
        "score": 0.0,
        "screenshots": [],
        "details": "",
    }

    try:
        if test_steps:
            # Execute declarative test steps
            result = execute_test_steps(page, rubric_scroller, test_steps, result)
        else:
            # No test steps — take screenshot for manual/Vision LLM review
            shot = rubric_scroller.capture_screenshot("state")
            result["screenshots"].append(shot)
            result["details"] = "No test steps defined — screenshot captured for manual review"
            result["score"] = 0.0
    except Exception as e:
        result["details"] = f"Test error: {str(e)[:200]}"
        try:
            shot = rubric_scroller.capture_screenshot("error")
            result["screenshots"].append(shot)
        except:
            pass

    return result


def execute_test_steps(page, scroller, steps: list, result: dict) -> dict:
    """Execute a list of declarative test steps."""
    all_passed = True

    for i, step in enumerate(steps):
        action = step.get("action", "")
        selector = step.get("selector", "")
        value = step.get("value", "")
        url = step.get("url", "")
        text = step.get("text", "")
        count = step.get("count", 0)
        timeout = step.get("timeout", DEFAULT_TIMEOUT)

        try:
            if action == "goto":
                page.goto(url, wait_until="networkidle", timeout=NAVIGATION_TIMEOUT)

            elif action == "click":
                # Try multiple strategies (like real tests do)
                element = page.locator(selector).first
                if element.is_visible():
                    element.scroll_into_view_if_needed()
                    element.click(force=True)
                else:
                    # Fallback: try getByText
                    page.get_by_text(selector.strip("#.")).first.click(force=True)

            elif action == "fill":
                inputs = page.locator(selector)
                for j in range(inputs.count()):
                    inp = inputs.nth(j)
                    if inp.is_visible():
                        inp.fill(value)
                        break

            elif action == "wait_for":
                page.wait_for_selector(selector, state="visible", timeout=timeout)

            elif action == "wait_for_navigation":
                page.wait_for_load_state("networkidle", timeout=NAVIGATION_TIMEOUT)

            elif action == "assert_visible":
                element = page.query_selector(selector)
                assert element and element.is_visible(), f"'{selector}' not visible"

            elif action == "assert_text":
                element = page.query_selector(selector)
                assert element, f"'{selector}' not found"
                actual = element.inner_text()
                assert text in actual, f"Expected '{text}' in '{actual[:50]}'"

            elif action == "assert_count_gte":
                elements = page.query_selector_all(selector)
                assert len(elements) >= count, \
                    f"Expected >= {count} '{selector}', found {len(elements)}"

            elif action == "scroll_to_bottom":
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(1500)

            elif action == "screenshot":
                shot = scroller.capture_screenshot(f"step_{i}")
                result["screenshots"].append(shot)

            elif action == "wait":
                page.wait_for_timeout(int(value) if value else 2000)

            # Take screenshot after significant actions
            if action in ("goto", "click", "fill", "scroll_to_bottom"):
                page.wait_for_timeout(500)
                shot = scroller.capture_screenshot(f"after_{action}_{i}")
                result["screenshots"].append(shot)

        except Exception as e:
            result["details"] += f"Step {i+1} ({action}) failed: {str(e)[:100]}; "
            all_passed = False
            # Screenshot on failure
            try:
                shot = scroller.capture_screenshot(f"fail_{action}_{i}")
                result["screenshots"].append(shot)
            except:
                pass

    result["score"] = 1.0 if all_passed else 0.0
    if all_passed:
        result["details"] = "All test steps passed"
    return result


# ============================================================
# MAIN EVALUATION
# ============================================================

def load_task_config():
    """Load rubrics and test config from task.yaml."""
    task_path = Path(__file__).parent.parent / "task.yaml"
    with open(task_path, 'r') as f:
        task = yaml.safe_load(f)
    eval_config = task.get("evaluation", {})
    return {
        "rubrics": eval_config.get("rubrics", []),
        "test_config": eval_config.get("test_config", {}),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submission", required=True, help="Submission directory")
    args = parser.parse_args()

    config = load_task_config()
    rubrics = config["rubrics"]
    test_config = config["test_config"]

    if not rubrics:
        print("No rubric criteria found in task.yaml")
        print("score=0.00")
        print("result=FAILED")
        return

    app_url = test_config.get("app_url", "http://localhost:5173/")
    device_name = test_config.get("mobile_device", DEVICE)
    artifacts_base = os.path.join(args.submission, "test_artifacts")
    os.makedirs(artifacts_base, exist_ok=True)

    # Setup browser
    if not HAS_PLAYWRIGHT:
        print("Playwright not installed. Install with:")
        print("  pip install playwright && playwright install chromium")
        print("\nRunning in dry-run mode...\n")
        page = monitor = scroller = None
    else:
        try:
            pw = sync_playwright().start()
            browser = pw.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            device_config = pw_devices.get(device_name, {})
            context = browser.new_context(**device_config, locale=LOCALE)
            context.set_default_timeout(DEFAULT_TIMEOUT)
            page = context.new_page()
            monitor = ActionMonitor(page)
            scroller = SmartScroller(page, artifacts_base)
            print(f"Browser launched: {device_name}")
            print(f"Testing: {app_url}\n")
        except Exception as e:
            print(f"Browser launch failed: {e}")
            page = monitor = scroller = None

    # Run tests
    total_weight = 0
    passed_weight = 0
    all_reports = []

    for i, rubric in enumerate(rubrics):
        point = rubric.get("point", "")
        weight = rubric.get("weight", 1)
        total_weight += weight

        if page and monitor and scroller:
            # Navigate to app before each test
            try:
                page.goto(app_url, wait_until="networkidle", timeout=NAVIGATION_TIMEOUT)
                page.wait_for_timeout(2000)
            except:
                pass

            result = test_rubric(page, monitor, scroller, rubric, test_config)
        else:
            result = {"test_id": str(i), "point": point, "score": 0.0,
                      "screenshots": [], "details": "No browser available"}

        if result["score"] >= 0.5:
            passed_weight += weight
            print(f"  [PASS] {i+1}/{len(rubrics)} (w={weight}): {point[:70]}")
        else:
            print(f"  [FAIL] {i+1}/{len(rubrics)} (w={weight}): {point[:70]}")
            if result["details"]:
                print(f"         {result['details'][:100]}")

        all_reports.append(result)

    # Save aggregated report
    report = {
        "app_url": app_url,
        "device": device_name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "rubric_results": all_reports,
        "network_issues": monitor.get_network_issues() if monitor else [],
        "total_weight": total_weight,
        "passed_weight": passed_weight,
    }
    report_path = os.path.join(artifacts_base, "test_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Cleanup
    if page:
        try:
            browser.close()
            pw.stop()
        except:
            pass

    # Final score
    score = passed_weight / total_weight if total_weight > 0 else 0

    print(f"\n{'='*50}")
    if monitor and monitor.get_network_issues():
        critical = [n for n in monitor.get_network_issues() if n.get("critical")]
        if critical:
            print(f"WARNING: {len(critical)} critical resource failures (CSS/JS/Font)")
    print(f"Score: {score:.2%} ({passed_weight}/{total_weight})")
    print(f"Artifacts: {artifacts_base}")
    print(f"Report: {report_path}")
    print(f"score={score:.2f}")
    print(f"result={'PASSED' if score >= PASS_THRESHOLD else 'FAILED'}")


if __name__ == "__main__":
    main()
