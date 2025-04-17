import pandas as pd
import requests
import os
import csv
import random
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException
from random import randint
from time import sleep
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from text_cleaner import clean_text

# options = Options()
# s = Service(ChromeDriverManager().install())
# driver = webdriver.Chrome(service=s, options=options)
# driver.set_page_load_timeout(30)        # prevent pages from loading for too long

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:111.0) Gecko/20100101 Firefox/111.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:111.0) Gecko/20100101 Firefox/111.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL Build/QD1A.190805.004) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:111.0) Gecko/20100101 Firefox/111.0"
]


def setup_driver():
    """
    Setup WebDriver with random user agent
    """
    options = Options()
    user_agent = random.choice(user_agents)
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument('--headless')      # prevent a bunch of browser windows from opening up
    
    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)
    driver.set_page_load_timeout(30)
    
    return driver


def get_cr_htm(index, row, output_dir, downloaded_indexes, missed_indexes):
    """
    Main scraper program
    """
    try:
        sleep(randint(2, 4))
        # rotate user agent
        driver = setup_driver()

        url_parts = row['URL'].split('/')
        curr_url = ""
        # # if URL corresponds to event/amendment/bill and does not already have '/text' filepath, adjust filepath to get text page
        if url_parts[3] in ['event', 'amendment', 'bill'] and url_parts[-1] != 'text':
            curr_url = row['URL'] + '/text'

            # fetch content from current url (+ handle pageload timeout)
            try:
                driver.get(curr_url)
            except TimeoutException:
                print(f"Timeout on index {index}: {curr_url}")
                add_missing_row(row)
                missed_indexes.append(index)
                return
        else:
            curr_url = row['URL']
            # fetch content from current url (+ handle pageload timeout)
            try:
                driver.get(curr_url)
            except TimeoutException:
                print(f"Timeout on index {index}: {curr_url}")
                add_missing_row(row)
                missed_indexes.append(index)
                return
            
        content = get_report_body(driver.page_source)
        sleep(randint(2, 4))

    except requests.RequestException as e:
        print(f"Error downloading {row['URL']}: {e}")
        return
    finally:
        if driver:
            driver.quit()
    
    # if content was extracted by scraper
    if content:
        # formats file name as [congress number]_[page type]_[identifier].txt
        #txt_file_name = f"{url_parts[4]}_{url_parts[5]}_{url_parts[6]}.txt"
        # formats file name as [row index].txt
        txt_file_name = f"{row['row_id']}.txt"
        file_path = os.path.join(output_dir, txt_file_name)
        # write content fo file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(clean_text(content))
            print(f"Downloaded: {row['URL']}")
            downloaded_indexes.append(index)
        except IOError as e:
            print(f"Error writing file {row['URL']}: {e}")      # error writing to file
            add_missing_row(row)
    else:
        print(f"Error fetching content - no content extracted for: {row['URL']}")        # if no content extracted by scraper
        add_missing_row(row)
        missed_indexes.append(index)


def get_report_body(content):
    """
    Extract congressional report text contained in preformatted <pre> tag (or <div>, see comments below)
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


def add_missing_row(row):
    """
    If an error occurs when processing a row, add that row 
    to a csv to process later in a second pass
    """
    #with open("missed_rows_pass1.csv", "a", newline='', encoding='utf-8') as f:        # for pass 1
    #with open("missed_rows_pass2.csv", "a", newline='', encoding='utf-8') as f:         # for pass 2
    #with open("missed_rows_pass3.csv", "a", newline='', encoding='utf-8') as f:         # for pass 3
    with open("missed_rows_pass4.csv", "a", newline='', encoding='utf-8') as f:         # for pass 4
        writer = csv.writer(f)
        writer.writerow(row)


def process_row(args):
    index, row, output_dir, downloaded_indexes, missed_indexes = args
    get_cr_htm(index, row, output_dir, downloaded_indexes, missed_indexes)


#df = pd.read_csv('congressional_to_go_withrows.csv')       # csv source for pass 1
#df = pd.read_csv('missed_rows_pass1.csv')         # csv source for pass 2
#df = pd.read_csv('missed_rows_pass2.csv')         # csv source for pass 3
df = pd.read_csv('missed_rows_pass3.csv')           # csv source for pass 4
output_dir = 'data'
downloaded_indexes = []
missed_indexes = []

i, j = 0, 257
print(f"---------------------- Processing indexes {i}-{j-1} (csv rows {i+1}-{j}) ----------------------")
# multithreading
with ThreadPoolExecutor(max_workers=15) as executor:
    list(executor.map(process_row, [(index, row, output_dir, downloaded_indexes, missed_indexes) for index, row in df.iloc[i:j].iterrows()]))

downloaded_indexes.sort()
print(f"Downloaded Indexes: {downloaded_indexes}")
print(f"Num Indexes Downloaded: {len(downloaded_indexes)}")
missed_indexes.sort()
print(f"Missed Indexes: {missed_indexes}")
print(f"Num Indexes Missed: {len(missed_indexes)}")
downloaded_indexes.clear()
missed_indexes.clear()

