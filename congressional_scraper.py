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
        # # if URL corresponds to event/amendment/bill and does not already have '/text' filepath, adjust filepath to get text page
        if url_parts[3] in ['event', 'amendment', 'bill'] and url_parts[-1] != 'text':
            curr_url = row['URL'] + '/text'
            driver.get(curr_url)
        else:
            curr_url = row['URL']
            driver.get(curr_url)
            
        content = get_report_body(driver.page_source, curr_url)
        sleep(randint(1, 10))

    except requests.RequestException as e:
        print(f"Error downloading {row['URL']}: {e}")
        return
    if content:
        # formats file name as [congress number]_[page type]_[identifier]
        txt_file_name = f"{url_parts[4]}_{url_parts[5]}_{url_parts[6]}.txt"
        file_path = os.path.join(output_dir, txt_file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Downloaded: {row['URL']}")
        except IOError as e:
            print(f"Error writing file {row['URL']}: {e}")
    else:
        print(f"No content extracted for: {row['URL']}")


def get_report_body(content, url):
    """
    Extract congressional report text contained in preformatted <pre> tag
    """
    soup = BeautifulSoup(content, 'lxml')
    preformatted_report_txt = soup.find('pre')              # most pages have monospace preformatted report text (typically inside of a <div id="report">)
    bill_txt = soup.find('div', {'id': 'bill-summary'})     # bills appear to have different html formatting w/ text inside <div> instead of <pre>
    report_txt = soup.find('div', {'id': 'report'})         # a select few pages have <div id="report">, but no <pre>, so collect this

    if preformatted_report_txt:
        return preformatted_report_txt.get_text()
    elif bill_txt:
        return bill_txt.get_text()
    elif report_txt:
        return report_txt.get_text()
    else:
        print(f"Error fetching preformatted report text content from: {url}")


df = pd.read_csv('congressional_to_go.csv')
output_dir = 'data'
for index, row in df.iterrows():
    get_cr_htm(row, output_dir)
