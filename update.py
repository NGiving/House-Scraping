import pandas as pd
import requests
from bs4 import BeautifulSoup

import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

scopes = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

def main():
    creds = Credentials.from_service_account_file('lithe-climber-365900-cdce51b6e6fa.json', scopes=scopes)
    gc = gspread.authorize(creds)
    sh = gc.open('houses')
    
    sheet1 = sh.get_worksheet_by_id(1179762581)
    records_data = sheet1.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    
def put():
    pass

def get():
    pass
    
    
   
def get_house_by_address(address):
    # url = 'https://www.zolo.ca/{city}-real-estate/{address.replace(" ", "-")}'
    r = requests.get('https://www.zolo.ca/toronto-real-estate/20-rochdale-avenue')
    soup = BeautifulSoup(r.text, 'html.parser')
    print(soup.prettify())
    
if __name__ == '__main__':
    get_house_by_address('a')