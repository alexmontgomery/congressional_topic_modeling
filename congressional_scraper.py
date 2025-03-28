import pandas as pd
import requests
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from random import randint
from time import sleep
from bs4 import BeautifulSoup
import lxml

options = Options()
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)


def get_cr_htm(row, output_dir):
    try:
        sleep(randint(1, 10))
        url_parts = row['URL'].split('/')
        curr_url = ""
        # if URL corresponds to bill/amemdement/event and does not already have '/text' filepath, adjust filepath to get text page
        if url_parts[-2] in ['house-bill', 'senate-bill', 'senate-amendment', 'house-amendment', 'house-event', 'senate-event'] and url_parts[-1] != 'text':
            driver.get(row['URL'] + '/text')
            curr_url = row['URL'] + '/text'     # save the current url (will make error handling easier in get_report_body())
        else:
            driver.get(row['URL'])
            curr_url = row['URL']
            
        content = get_report_body(driver.page_source, curr_url)
        sleep(randint(1, 10))

    except requests.RequestException as e:
        print(f"Error downloading {row['URL']}: {e}")
        return
    if content:
        # formats file name as [congress number]_[house/senate bill/amendment/event]_[identifier]
        txt_file_name = f"{url_parts[-4]}_{url_parts[-3]}_{url_parts[-2]}.html" if url_parts[-1] == 'text' else f"{url_parts[-3]}_{url_parts[-2]}_{url_parts[-1]}.txt"
        file_path = os.path.join(output_dir, txt_file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Downloaded: {row['URL']}")
        except IOError as e:
            print(f"Error writing file {row['URL']}: {e}")
    else:
        print(f"No content extracted for: {row['URL']}")


"""Extract congressional report text contained in preformatted <pre> tag"""
def get_report_body(content, url):
    soup = BeautifulSoup(content, 'lxml')
    report_txt = soup.find('pre')
    bill_txt = soup.find('div', {'id': 'bill-summary'})     # bills appear to have different html formatting w/ text inside <div> instead of <pre>

    if report_txt:
        return report_txt.get_text()
    elif bill_txt:
        return bill_txt.get_text()
    else:
        print(f"Error fetching preformatted report text content from: {url}")


df = pd.read_csv('congressional_to_go.csv')
output_dir = 'data'
for index, row in df.iterrows():
    get_cr_htm(row, output_dir)
