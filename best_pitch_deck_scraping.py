import os
import shutil
from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import requests
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfMerger
import pandas as pd
from pathlib import Path

# specify the URL of the website to be scraped
url = "https://bestpitchdeck.com/"


# create Chrome options object
chrome_options = webdriver.ChromeOptions()

# add the disable-site-isolation-trials argument to Chrome options
chrome_options.add_argument('--disable-site-isolation-trials')

# create Chrome webdriver instance with the options
driver = webdriver.Chrome(options=chrome_options)

# navigate to the URL
driver.get(url)

# wait for the page to load
driver.implicitly_wait(10)



# initialize vars
count = 0 
names = []
industries = []
descriptions = []
short_descs = []
tags = []
b_models = []
c_models = []
websites = []
raiseds = []
years_raised = []
stages = []
investors = []
pdf_urls = []


# find all the company cards on the page
company_cards = driver.find_elements("xpath", '//div[@class="card"]')
# loop through the company cards and click on the Browse Deck button
for card in company_cards:
    driver.implicitly_wait(10)
    try:
        link = card.find_element("xpath", './/a')
        href = link.get_attribute("href")
    except:
        continue
    if href == "https://bestpitch.es/ultimate-pitch-deck-bundle?ref=ex":
        continue

    # open the href for the card
    driver.get(href)
    # do something on the new page (e.g., extract information)
    # wait for the modal to load
    driver.implicitly_wait(7)
    
    # extract the pitch deck description
    try:
        description = driver.find_element("xpath", "//p").text
    except:
        description = ''
   
   #first column info
    try:
        column_one = driver.find_element("xpath", "//div[@class='col-12 col-md-6'][1]")
    except:
        # if not even column is there, page must be 404 -- go to next startup
        driver.back()
        continue
    try:
        raised = column_one.find_element("xpath", "//div[@class='col-12 col-md-6'][1]//li[1]").text.split(":")[1].strip()
    except:
        raised = ''
    try:
        year_raised = column_one.find_element("xpath", "//div[@class='col-12 col-md-6'][1]//li[2]").text.split(":")[1].strip()
    except:
        year_raised = ''
    try:
        stage = column_one.find_element("xpath", "//div[@class='col-12 col-md-6'][1]//li[3]").text.split(":")[1].strip()
    except:
        stage = ''
    try:
        investor = column_one.find_element("xpath", "//div[@class='col-12 col-md-6'][1]//li[4]").text.split(":")[1].strip()
    except:
        investor = ''
   
   
    # second column info
    try:
        column_two = driver.find_element("xpath", "//div[@class='col-12 col-md-6'][2]")
    except:
        driver.back()
        continue
    try:
        short_desc = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//p").text
    except:
        short_desc = ''
    try:
        industry = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//li[1]").text.split(":")[1].strip()
    except:
        industry = ''
    try:
        tag = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//li[2]").text.split(":")[1].strip()
    except:
        tag = ''
    try:
        b_model = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//li[3]").text.split(":")[1].strip()
    except:
        b_model = ''
    try:
        c_model = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//li[4]").text.split(":")[1].strip()
    except:
        c_model = ''
    try:
        website = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//li[5]").text.split(":")[1].strip()
    except:
        website = ''
    try:
        name = column_two.find_element("xpath", "//div[@class='col-12 col-md-6'][2]//li[6]").text.split(":")[1].strip()
        print(name)
    except:
        name = ''

    # images 
    # save a copy of the name with lowercase, no spaces and no special characters
    adjusted_name = name.lower().replace(" ", "").replace(".", "").replace(",", "").replace("(", "").replace(")", "").replace("'", "").replace("&", "").replace("/", "").replace("-", "")
    local_path = "./BestPitchPDFs/" + adjusted_name + '.pdf'
    try:
        slideshow = driver.find_element('xpath', "//iframe")
        slideshow_href = slideshow.get_attribute("src")
    except:
        driver.back()
        continue


    driver.get('https://slideshare.parthmaniar.tech/')
    driver.implicitly_wait(10)
    # enter the slideshow url into the input box
    input_box = driver.find_element('xpath', "//input")
    input_box.send_keys(slideshow_href)
    # click the download button
    download_button = driver.find_element('xpath', "//button")
    download_button.click()
    # wait for the download to finish
    time.sleep(10)

    # move the file from the Downloads folder to the ~/antonytahan/CS5787/BestPitchPDFs folder
    try:
        shutil.move('/Users/antonytahan/Downloads/embed_code.pdf','/Users/antonytahan/cs5787/BestPitchPDFs/embed_code.pdf')
        # # rename the file to the name of the company
        os.rename('/Users/antonytahan/cs5787/BestPitchPDFs/embed_code.pdf', '/Users/antonytahan/cs5787/BestPitchPDFs/' + adjusted_name + '.pdf')
    except:
        driver.back()
        driver.implicitly_wait(10)
        driver.back()
        continue

    driver.back()
    driver.implicitly_wait(10)

    names.append(name)
    industries.append(industry)
    descriptions.append(description)
    short_descs.append(short_desc)
    tags.append(tag)
    b_models.append(b_model)
    c_models.append(c_model)
    websites.append(website)
    raiseds.append(raised)
    years_raised.append(year_raised)
    stages.append(stage)
    investors.append(investor)
    pdf_urls.append(local_path)
    count += 1
    print(count)
    # go back to the previous page
    driver.back()


print('Total Number of Pitch Decks Extracted:', count)

df = pd.DataFrame({'Name': names, 'Industry': industries, 'Description': descriptions, 'Short Description': short_descs, 'Tags': tags, 'Business Model': b_models, 'Customer Model': c_models, 'Website': websites, 'Raised': raiseds, 'Year Raised': years_raised, 'Stage': stages, 'Investors': investors, 'PDF URL': pdf_urls})

df.to_csv('BestPitchDecks.csv', index=False)


# close the browser window
# input('Press Enter to exit...')
driver.quit()
