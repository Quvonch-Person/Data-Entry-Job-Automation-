import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# Configuration
FORM_URL = "YOUR_GOOGLE_FORM_LINK_HERE"
TARGET_URL = "https://appbrewery.github.io/Zillow-Clone/"

# ----------------- STEP 1: SCRAPE DATA -----------------
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

response = requests.get(TARGET_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Extract and sanitize listing data
address_tags = soup.select(".StyledPropertyCardDataWrapper address")
all_addresses = [a.get_text().replace("|", "").strip() for a in address_tags]

price_tags = soup.select(".PropertyCardWrapper span")
all_prices = [
    p.get_text().split("+")[0].split("/")[0].strip()
    for p in price_tags
    if "$" in p.get_text()
]

link_tags = soup.select(".StyledPropertyCardDataWrapper a")
all_links = [
    f"https://appbrewery.github.io{a['href']}"
    if a["href"].startswith("/")
    else a["href"]
    for a in link_tags
]

print(f"Extracted {len(all_addresses)} synchronized records.")

# ----------------- STEP 2: AUTOMATE SUBMISSION -----------------
chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)
driver = webdriver.Chrome(options=chrome_options)

try:
    for i in range(len(all_addresses)):
        driver.get(FORM_URL)
        time.sleep(2)

        form_inputs = driver.find_elements(
            By.CSS_SELECTOR, "input[type='text']"
        )
        submit_btn = driver.find_element(
            By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div'
        )

        form_inputs[0].send_keys(all_addresses[i])
        form_inputs[1].send_keys(all_prices[i])
        form_inputs[2].send_keys(all_links[i])

        submit_btn.click()
        print(f"Submitted record {i + 1}/{len(all_addresses)}")
        time.sleep(1)

finally:
    driver.quit()
    print(
        "Automation cycle complete. Verify incoming data in your linked Google Sheet."
    )