import re
import time
import requests
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
from google.oauth2.service_account import Credentials
from bs4 import BeautifulSoup
import gspread
import pandas as pd

URL = 'https://www.zolo.ca/index.php?'
scopes = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = Credentials.from_service_account_file('lithe-climber-365900-cdce51b6e6fa.json', scopes=scopes)
gc = gspread.authorize(creds)
sh = gc.open('houses')

opts = {
    'sarea': ['Markham', 'Mississauga', 'Oakville'],
    'ptype_house': '1',
    'min_baths': '2',
    'min_beds': '2',
    'min_price': '950000',
    'max_price': '1700000',
    'filter': '1'
}
    
def scrape(url, params, filter=None):
    data = []
    driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()))
    areas = params.pop('sarea')
    for area in areas:
        dest = url + f'sarea={area}&' + "&".join(['{}={}'.format(k,v) for k, v in params.items()])
        print(area, dest)
        while True:
            driver.get(dest)
            postings = driver.find_elements(By.CLASS_NAME, 'card-listing--details')
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            details = soup.find_all('div', 'card-listing--details')
            
            for elem in details:
                address = elem.find(class_="street").get_text().strip() if elem.find(class_="street") is not None else "Unavailable"
                price = elem.find(itemprop='price')['value'] if elem.find(itemprop='price') is not None else 0 
                city = elem.find(class_="city").get_text() if elem.find(class_="city") is not None else "Unavailable"
                neighbourhood = elem.find(class_="neighbourhood").get_text().replace('•', '').strip() if elem.find(class_="neighbourhood") is not None else "Unavailable"
                bedrooms = elem.find(text=re.compile("([0-9]|...) bed")).replace('bed', '').strip() if elem.find(text=re.compile("([0-9]|...) bed")) is not None else 0
                bathrooms = elem.find(text=re.compile("[0-9] bath")).replace('bath', '').strip() if elem.find(text=re.compile("[0-9] bath")) is not None else 0
                data.append({"price": price, "address": address, "city": city, "neighbourhood": neighbourhood, "bedrooms": bedrooms, "bathrooms": bathrooms})
                
            next_url = soup.find('a', attrs={"aria-label": "next page of results"})
            if next_url is None:
                print('Out of pages to scrape.') 
                break
            dest = next_url['href']
            time.sleep(2)
    driver.close()
    return data
        
def push_to_sheets(data):
    sheet = sh.worksheet('houses')
    sheet_rec = sheet.get_all_records()
    
    for listing in data:
        if any(rec['address'] == listing['address'] for rec in sheet_rec):
            next(rec for rec in sheet_rec if rec['address'] == listing['address']).update(listing)
        sheet_rec.append(listing)
            
    df = pd.DataFrame(sheet_rec)
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())
    
def update_current_listings():
    sheet = sh.worksheet('houses')
    sheet_rec = sheet.get_all_records()
    
    options = Options()
    options.set_preference("dom.webdriver.enabled", False)
    options.headless = False
    driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()), options=options)
    # driver = webdriver.Firefox(service=Service(executable_path=GeckoDriverManager().install()))
    # for rec in sheet_rec:
    #     url = 'https://www.google.com/search?q={}+realtor+ca/start=0'.format(rec["address"].replace(" ", "+"))
    #     driver.get(url)
    #     element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.TAG_NAME, "h3")))
    #     element.click()
        
    rec = sheet_rec[6]
    # url = 'https://www.google.com/search?q={}+realtor+ca/start=0'.format(rec["address"].replace(" ", "+"))
    url = 'https://www.realtor.ca/real-estate/24634157/200-troy-st-mississauga-mineola'

def main():
    update_current_listings()

main()
