# Scrape ONET summary pages in **Google Colab** using the *google‑colab‑selenium* helper
# -----------------------------------------------------------------------------
# Setup in Colab:
#   %pip install -q google-colab-selenium[undetected] pandas lxml
#   # upload codes.csv  (one ONET‑SOC code per row)
#   !python scrape_onet.py
# -----------------------------------------------------------------------------

import csv
import random
import time
from pathlib import Path
from typing import Dict, List

import google_colab_selenium as gs
import pandas as pd
from lxml import html
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import MoveTargetOutOfBoundsException

# -----------------------------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------------------------

CODES_CSV_PATH = Path("codes.csv")          # input file (one code per line)
OUTPUT_CSV_PATH = Path("onet_data_scraped.csv")

DELAY_RANGE = (5, 20)                        # seconds between actions
MOUSE_MOVE_COUNT_RANGE = (3, 7)              # wiggles per page
SCROLL_PIXELS_RANGE = (200, 1200)            # scroll distance

USER_AGENTS = [
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
]

USE_UNDETECTED = False  # flip to True for `gs.UndetectedChrome()`

# -----------------------------------------------------------------------------
# DRIVER BUILDER
# -----------------------------------------------------------------------------

def build_driver():
    """Spin up a Colab‑ready Chrome session via google‑colab‑selenium."""
    opts = Options()
    opts.add_argument(f"user-agent={random.choice(USER_AGENTS)}")
    if USE_UNDETECTED:
        driver = gs.UndetectedChrome(options=opts)
    else:
        driver = gs.Chrome(options=opts)
    return driver


# -----------------------------------------------------------------------------
# HELPER ROUTINES
# -----------------------------------------------------------------------------

def random_delay():
    time.sleep(random.uniform(*DELAY_RANGE))


def simulate_human_interaction(driver):
    """Scroll a bit and wiggle the mouse safely inside the page bounds."""
    # Random scroll down the page
    driver.execute_script(
        "window.scrollTo(0, arguments[0]);",
        random.randint(*SCROLL_PIXELS_RANGE),
    )
    time.sleep(random.uniform(0.5, 1.5))

    # Random mouse moves – constrained inside <body> rectangle to avoid
    # MoveTargetOutOfBoundsException.
    body = driver.find_element(By.TAG_NAME, "body")
    rect = body.rect  # dict with width/height/…
    width = max(1, int(rect.get("width", 1)))
    height = max(1, int(rect.get("height", 1)))

    actions = ActionChains(driver)
    for _ in range(random.randint(*MOUSE_MOVE_COUNT_RANGE)):
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        try:
            actions.move_to_element_with_offset(body, x, y).pause(
                random.uniform(0.2, 0.8)
            )
        except MoveTargetOutOfBoundsException:
            # Skip if coordinates are invalid for some reason
            continue
    try:
        actions.perform()
    except MoveTargetOutOfBoundsException:
        pass  # ignore final edge cases


def read_codes(path: Path) -> List[str]:
    with path.open(newline="") as f:
        return [
            row[0].strip()
            for row in csv.reader(f)
            if row and row[0].strip() and row[0].strip().lower() != "onet_soc_code"
        ]


def extract_fields(page_html: str) -> Dict[str, str]:
    tree = html.fromstring(page_html)
    syn_nodes = tree.xpath("/html/body/div[1]/div[1]/div/div[2]/p/text()")
    task_nodes = tree.xpath("/html/body/div[1]/div[1]/div/div[2]/div[2]/div[1]/text()")
    return {
        "synonyms": " ".join(t.strip() for t in syn_nodes if t.strip()),
        "tasks": " ".join(t.strip() for t in task_nodes if t.strip()),
    }


def scrape_codes(codes: List[str]) -> pd.DataFrame:
    random.shuffle(codes)  # visit in random order
    driver = build_driver()
    rows: List[Dict[str, str]] = []

    try:
        for code in codes:
            url = f"https://www.mynextmove.org/profile/summary/{code}"
            driver.get(url)
            random_delay()
            simulate_human_interaction(driver)
            random_delay()
            data = extract_fields(driver.page_source)
            data["onet_soc_code"] = code
            rows.append(data)
            print(f"✓ {code} done")
    finally:
        driver.quit()

    return pd.DataFrame(rows, columns=["onet_soc_code", "synonyms", "tasks"])


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------

def main():
    codes = read_codes(CODES_CSV_PATH)
    if not codes:
        raise SystemExit("No codes found in codes.csv")
    df = scrape_codes(codes)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Saved {len(df)} records → {OUTPUT_CSV_PATH}")


if __name__ == "__main__":
    main()
