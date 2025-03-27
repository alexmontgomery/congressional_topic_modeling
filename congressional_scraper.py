import pandas as pd
import requests
import os
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from random import randint
from time import sleep

options = Options()
s = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=s, options=options)


def get_cr_htm(row, output_dir):
    try:
        sleep(randint(1, 10))
        if row['URL'].split('/')[-2] in ['house-bill', 'senate-bill', 'senate-amendement', 'house-amendment']:
            driver.get(row['URL'] + '/text')
        else:
            driver.get(row['URL'])
        content = driver.page_source
        sleep(randint(1, 10))

    except requests.RequestException as e:
        print(f"Error downloading {row['URL']}: {e}")
        return
    if content:
        file_name = row['URL'].split('/')[-4] + '_' + row['URL'].split('/')[-3] + '_' + row['URL'].split('/')[-2] + '_' + row['URL'].split('/')[-1] + '.html'
        file_path = os.path.join(output_dir, file_name)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Downloaded: {row['URL']}")
        except IOError as e:
            print(f"Error writing file {row['URL']}: {e}")
    else:
        print(f"No content extracted for: {row['URL']}")

df = pd.read_csv('congressional_to_go.csv')
output_dir = 'data'
for index, row in df.iterrows():
    get_cr_htm(row, output_dir)
