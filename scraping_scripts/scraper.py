import requests
import os
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
from supabase import create_client, Client
from prefect import task, flow
from prefect.task_runners import ThreadPoolTaskRunner
from dotenv import load_dotenv

load_dotenv()

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


def get_supabase_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


@task
def fetch_urls():
    """
    Get the urls and the corresponding document_id from Supabase
    and put into a {id: url} hashmap
    """
    supabase = get_supabase_client()   
    response = (
        supabase.table("documents")
        .select("document_id, url")
        .execute()
    )

    if response.data:
        url_map = {item["document_id"]: item["url"] for item in response.data}
    else:
        print("No documents found or an error occurred.")
        url_map = {}

    return url_map


@task(
    retries=5,
    retry_delay_seconds=7,
    timeout_seconds=120
)
def scrape_doc_text(curr_id, curr_url):
    """
    Main scraper program
    """
    driver = None
    try:
        sleep(randint(2, 4))
        driver = setup_driver()

        # scrape the current url's text content
        driver.get(curr_url)
        content = get_report_body(driver.page_source)
        if not content:
            raise ValueError("No content extracted")

        # insert scraped content into raw_text column in db
        supabase = get_supabase_client()
        response = supabase.table("documents").upsert(
            {
                "document_id": curr_id,
                "raw_text": content,
            },
            on_conflict="document_id"
        ).execute()

        return curr_id

    finally:
        if driver:
            driver.quit()


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


@flow(task_runner=ThreadPoolTaskRunner(max_workers=15))
def scrape_all_docs():
    url_map = fetch_urls()

    futures = []
    for doc_id, url in url_map.items():
        future = scrape_doc_text.submit(doc_id, url)         # uses built-in concurrency (see Prefect .submit() method)
        futures.append(future)
    
    return [future.result() for future in futures]


if __name__ == "__main__":
    scrape_all_docs()
    