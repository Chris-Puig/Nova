# search.py - Smart dorking and search engine scraping

import requests
from bs4 import BeautifulSoup
import random
import time
import os
import logging
from datetime import datetime

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Linux x86_64)"
]

HEADERS = {
    "User-Agent": random.choice(USER_AGENTS)
}

SEARCH_URL = "https://www.bing.com/search"
LOG_DIR = "/home/kali/Desktop/NOVA/logs/logs - search.py/"


def setup_logger(target_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"{target_name.replace(' ', '_')}_{date_str}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    logger = logging.getLogger("search")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Initialized logging for target: {target_name}")
    return logger


def build_dorks(full_name, company=None, location=None, logger=None):
    name_query = f'"{full_name}"'
    company_query = f'"{company}"' if company else ""
    location_query = f'"{location}"' if location else ""

    queries = [
        f'{name_query} site:github.com',
        f'{name_query} site:twitter.com',
        f'{name_query} site:pastebin.com',
        f'{name_query} {company_query} {location_query}',
        f'{name_query} filetype:pdf',
        f'{name_query} intitle:resume',
        f'{name_query} intext:"{company}"'
    ]

    if logger:
        logger.info(f"Built {len(queries)} search queries for: {full_name}")
    return queries

def perform_search(query, max_results=10, logger=None):
    if logger:
        logger.info(f"Searching Bing for: {query}")
    params = {"q": query, "count": max_results}
    try:
        response = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []

        # Extended search parsing logic
        for item in soup.find_all("a", href=True):
            href = item["href"]
            title = item.get_text(strip=True)
            if href.startswith("http") and "bing.com" not in href:
                results.append({"title": title, "url": href})
                if logger:
                    logger.debug(f"Found result: {title} - {href}")
                if len(results) >= max_results:
                    break

        if not results and logger:
            logger.warning("No results found in Bing search parsing.")

        time.sleep(random.uniform(1.5, 3.5))
        return results

    except requests.exceptions.RequestException as e:
        if logger:
            logger.error(f"Search request failed: {e}")
        raise

def run_osint_queries(full_name, company=None, location=None):
    logger = setup_logger(full_name)
    logger.info("Starting OSINT search phase.")

    queries = build_dorks(full_name, company, location, logger=logger)
    all_results = []

    for query in queries:
        try:
            results = perform_search(query, logger=logger)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"Failed query: {query} due to: {e}")
            continue

    logger.info(f"Search completed with {len(all_results)} total results.")
    return all_results
