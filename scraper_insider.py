from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import time
import requests
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfMerger
import pandas as pd
from pathlib import Path
import re

driver = webdriver.Chrome()
driver.get(
    'https://www.businessinsider.com/searchable-database-of-business-insider-pitch-decks-2020-7')

login_btn = driver.find_element(By.CLASS_NAME, "account-text-not-logged-in")
login_btn.click()

driver.implicitly_wait(3)
email_textbox = driver.find_element(By.ID, "email")
email_textbox.send_keys('at675@cornell.edu')

pwd_textbox = driver.find_element(By.ID, "password")
pwd_textbox.send_keys('Cs5787dl')

login_btn = driver.find_element(By.CLASS_NAME, "login-button")
login_btn.click()
driver.implicitly_wait(5)
# once logged in:
iframe = driver.find_element(
    By.ID, "datawrapper-chart-HtQqi")

table_url = iframe.get_attribute("src")

driver.get(table_url)
driver.implicitly_wait(1)
pitch_df = pd.DataFrame(columns=["Local Link", "Stage", "Industry", "Region"])


print("Start Scraping... \n")

for page_num in range(1, 42):
    next_btn = driver.find_element(By.CLASS_NAME, "next")
    for next_clicks in range(page_num - 1):
        try:
            next_btn.click()
        except StaleElementReferenceException:
            pass

    print("Page Number: ", page_num)
    len_table_page = len(driver.find_elements(
        By.CLASS_NAME, "datawrapper-HtQqi-1m87fdh"))

    for i in range(len_table_page):
        row = driver.find_elements(
            By.CLASS_NAME, "datawrapper-HtQqi-1m87fdh")[i]
        tds = row.find_elements(By.XPATH, ".//td")
        row_vals = [td.text for td in tds]

        startup_link = row.find_element(
            By.XPATH, ".//th/a").get_attribute("href")
        startup_name = row.find_element(
            By.XPATH, ".//th/a").text.replace(" ", "")

        startup_name = re.sub('[^0-9a-zA-Z]+', '', startup_name)

        print("Now Scraping Startup: ", startup_name)

        local_path = "./InsiderPitchPDFs/" + startup_name + '.pdf'
        if (not Path(local_path).is_file()):
            driver.get(startup_link)

            driver.implicitly_wait(1)
            pitch_divs = driver.find_elements(By.CLASS_NAME, "slide")

            image_links = []
            for div in pitch_divs:
                try:
                    image_links.append(div.find_element(By.CLASS_NAME, "lazy-image").get_attribute(
                        "data-srcs").split('"')[1])
                except NoSuchElementException:  # spelling error making this code not work as expected
                    pass

            pdf_merger = PdfMerger()
            for img_link in image_links:
                response = requests.get(img_link)
                image = Image.open(BytesIO(response.content))
                image = image.convert('RGB')

                image_bytes = BytesIO()
                image.save(image_bytes, format='PDF')
                pdf_merger.append(BytesIO(image_bytes.getvalue()))

            # save the merged PDF to a file
            with open(local_path, 'wb') as f:
                pdf_merger.write(f)

            driver.get(table_url)
            driver.implicitly_wait(1)

        row_vals = [local_path] + row_vals
        pitch_df.loc[len(pitch_df)] = row_vals

pitch_df.to_csv("./data/insider_pitch_decks.csv")
# time.sleep(5)
driver.quit()
