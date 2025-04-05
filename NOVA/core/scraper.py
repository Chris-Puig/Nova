# scraper.py - Scrapes GitHub, Twitter, Pastebin, and other URLs

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging
import os
from datetime import datetime
from core.classifier import classify_text

LOG_DIR = "/home/kali/Desktop/NOVA/logs/logs - scraper.py/"


def setup_logger(company_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_id = company_name if company_name else "target"
    log_filename = f"{company_name.replace(' ', '_')}_{date_str}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    logger = logging.getLogger("scraper")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Initialized scraper logging for target company: {company_name}")
    return logger


def classify_url(url):
    domain = urlparse(url).netloc
    if "github.com" in domain:
        return "github"
    elif "twitter.com" in domain:
        return "twitter"
    elif "pastebin.com" in domain:
        return "pastebin"
    else:
        return "generic"


def scrape_github(url, logger):
    logger.info(f"Scraping GitHub URL: {url}")
    data = []
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        username = url.split("/")[-1]
        repos = [a.text.strip() for a in soup.select("a[itemprop='name codeRepository']")]
        data.extend([username] + repos)
    except Exception as e:
        logger.error(f"GitHub scrape failed: {e}")
        raise
    return data


def scrape_twitter(url, logger):
    logger.info(f"Scraping Twitter URL: {url}")
    data = []
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        bio = soup.find("meta", {"name": "description"})
        if bio:
            data.append(bio.get("content"))
        handle = url.split("/")[-1]
        data.append(handle)
    except Exception as e:
        logger.error(f"Twitter scrape failed: {e}")
        raise
    return data


def scrape_pastebin(url, logger):
    logger.info(f"Scraping Pastebin URL: {url}")
    data = []
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        paste_content = soup.find("textarea", {"id": "paste_code"})
        if paste_content:
            data.append(paste_content.text.strip())
    except Exception as e:
        logger.error(f"Pastebin scrape failed: {e}")
        raise
    return data


def scrape_generic(url, company_name, logger):
    logger.info(f"Scraping generic URL: {url}")
    data = []
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        paragraphs = soup.find_all("p")
        extracted = [p.text.strip() for p in paragraphs if len(p.text.strip()) > 20]
        data.extend(extracted)

        combined_text = ' '.join(extracted)
        tags = classify_text(combined_text, company_name)
        logger.info(f"Page classified as: {tags}")

    except Exception as e:
        logger.error(f"Generic scrape failed: {e}")
        raise
    return data

def scrape_urls(url_list, company_name):
    logger = setup_logger(company_name)
    logger.info("Starting scrape phase for collected URLs.")

    if not url_list:
        logger.warning("No URLs provided to scrape.")
        return []

    results = []
    for item in url_list:
        url = item.get("url")
        if not url:
            continue
        source_type = classify_url(url)

        try:
            if source_type == "github":
                logger.info(f"Routing to GitHub scraper: {url}")
                results.extend(scrape_github(url, logger))
            elif source_type == "twitter":
                logger.info(f"Routing to Twitter scraper: {url}")
                results.extend(scrape_twitter(url, logger))
            elif source_type == "pastebin":
                logger.info(f"Routing to Pastebin scraper: {url}")
                results.extend(scrape_pastebin(url, logger))
            else:
                logger.info(f"Routing to generic scraper: {url}")
                results.extend(scrape_generic(url, company_name, logger))
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
            continue

    if not results:
        logger.warning("Scraping phase returned no data.")

    logger.info(f"Scraping complete. Extracted {len(results)} total data points.")
    return results
