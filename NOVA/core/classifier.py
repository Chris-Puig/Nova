# classifier.py - Content classifier for scraped text

import logging
import os
from datetime import datetime

LOG_DIR = "/home/kali/Desktop/NOVA/logs/logs - classifier.py/"


def setup_logger(company_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_id = company_name if company_name else "target"
    log_filename = f"{company_name.replace(' ', '_')}_{date_str}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    logger = logging.getLogger("classifier")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Initialized classifier logging for target company: {company_name}")
    return logger


def classify_text(text, company_name):
    logger = logging.getLogger("classifier")

    keywords = {
        "credentials": ["username", "password", "login", "credentials"],
        "personal": ["address", "phone", "email", "contact"],
        "financial": ["credit card", "bank", "account", "transaction"],
        "employment": ["position", "employer", "hired", "salary"]
    }

    tags = set()
    text_lower = text.lower()

    for category, terms in keywords.items():
        for term in terms:
            if term in text_lower:
                tags.add(category)
                logger.debug(f"Classified as {category} due to term: {term}")
                break

    if not tags:
        logger.debug("No classification matched.")
        tags.add("unclassified")

    logger.info(f"Final classification: {tags}")
    return list(tags)
