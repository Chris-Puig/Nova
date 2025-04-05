# extractor.py - Extracts keywords from raw data for wordlist generation

import re
import logging
import os
import sys
from collections import defaultdict
from datetime import datetime

LOG_DIR = "/home/kali/Desktop/NOVA/logs/logs - extractor.py/"

def setup_logger(company_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_id = company_name if company_name else "target"
    log_filename = f"{company_name.replace(' ', '_')}_{date_str}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    logger = logging.getLogger("extractor")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Initialized extractor logging for target company: {company_name}")
    return logger

def clean_text(text):
    text = re.sub(r"[^a-zA-Z0-9@.\-_' ]", '', text)
    return text.strip()

def extract_keywords(data, company_name):
    try:
        logger = setup_logger(company_name)
        logger.info("[Extractor] Starting keyword extraction...")
        logger.debug(f"[Extractor] Raw data input: {data}")

        keywords = defaultdict(set)

        for entry in data:
            if isinstance(entry, dict):
                for key, value in entry.items():
                    if isinstance(value, str):
                        value = clean_text(value)
                        logger.debug(f"Extracted from dict - {key}: {value}")
                        keywords[key].add(value)
                    elif isinstance(value, list):
                        for item in value:
                            item = clean_text(str(item))
                            logger.debug(f"Extracted from list - {key}: {item}")
                            keywords[key].add(item)
            elif isinstance(entry, str):
                entry = clean_text(entry)
                tokens = re.findall(r"\b\w{3,}\b", entry)
                for token in tokens:
                    logger.debug(f"Extracted from raw string: {token}")
                    keywords['generic'].add(token)
            else:
                logger.debug(f"Skipped unsupported data type: {type(entry)}")

        # Add manual keyword variations
        name_parts = set()
        if 'full_name' in keywords:
            for name in keywords['full_name']:
                parts = name.lower().split()
                name_parts.update(parts)
                keywords['usernames'].update(parts)
                keywords['generic'].update(parts)

        if company_name:
            company_clean = company_name.lower()
            keywords['usernames'].add(company_clean)
            keywords['generic'].add(company_clean)
            for part in name_parts:
                keywords['usernames'].add(part + company_clean)
                keywords['usernames'].add(company_clean + part)
                keywords['generic'].add(part + company_clean)
                keywords['generic'].add(company_clean + part)

        # Add DOB variations
        if 'dob' in keywords:
            for dob in keywords['dob']:
                dob_clean = re.sub(r"[^0-9]", "", dob)
                if len(dob_clean) >= 4:
                    year = dob_clean[:4]
                    keywords['generic'].add(year)
                    for part in name_parts:
                        keywords['generic'].add(part + year)
                        keywords['generic'].add(year + part)
                    if company_name:
                        keywords['generic'].add(company_clean + year)
                        keywords['generic'].add(year + company_clean)

        final_keywords = {
            k: sorted([w for w in v if w]) for k, v in keywords.items()
        }

        total_keywords = sum(len(v) for v in final_keywords.values())
        logger.info(f"[Extractor] Extracted {total_keywords} keywords across {len(final_keywords)} categories.")
        return final_keywords

    except Exception as e:
        logger = logging.getLogger("extractor")
        logger.error(f"[Extractor] Exception occurred: {e}")
        print(f"[!] Extractor failed with exception: {e}")
        raise
