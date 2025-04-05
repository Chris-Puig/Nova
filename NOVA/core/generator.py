# generator.py - Creates customized username and password wordlists

import random
import os
import logging
from datetime import datetime
import sys
import string

LOG_DIR = "/home/kali/Desktop/NOVA/logs/logs - generator.py/"


def setup_logger(company_name):
    os.makedirs(LOG_DIR, exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    target_id = company_name if company_name else "target"
    log_filename = f"{company_name.replace(' ', '_')}_{date_str}.log"
    log_path = os.path.join(LOG_DIR, log_filename)

    logger = logging.getLogger("generator")
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        file_handler = logging.FileHandler(log_path)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.info(f"Initialized generator logging for target company: {company_name}")
    return logger


def mutate_word(word):
    leet_map = {'a': '@', 's': '$', 'o': '0', 'e': '3', 'i': '1', 'l': '1'}
    return ''.join(leet_map.get(c.lower(), c) for c in word)


def validate_password_policy(password):
    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_special = any(c in string.punctuation for c in password)
    long_enough = len(password) >= 8
    return all([has_upper, has_lower, has_special, long_enough])


def validate_username_policy(username):
    valid_chars = string.ascii_letters + string.digits + "_"
    if not (5 <= len(username) <= 20):
        return False
    if not username[0].isalpha():
        return False
    return all(c in valid_chars for c in username)


def enrich_usernames(keywords):
    enriched = set()
    names = set()
    if 'usernames' in keywords:
        names.update(keywords['usernames'])
    if 'full_name' in keywords:
        for full in keywords['full_name']:
            parts = full.lower().split()
            names.update(parts)
            if len(parts) == 2:
                enriched.add(parts[0] + parts[1])
                enriched.add(parts[1] + parts[0])
                enriched.add(parts[0][0] + parts[1])
                enriched.add(parts[0] + parts[1][0])
    if 'generic' in keywords:
        for w in keywords['generic']:
            if w.isalpha():
                names.add(w)

    for name in names:
        enriched.add(name)
        enriched.add(name + str(random.randint(1, 99)))
        enriched.add(name + str(random.randint(1950, 2025)))
        enriched.add(name + "_")
        enriched.add(name + "123")

    return list(enriched)


def generate_variations(keywords, category, count, enforce_policy=False, policy_type="password"):
    base_words = keywords.get(category, [])
    extra_words = set()

    if category == 'generic':
        for k in ['full_name', 'dob', 'company_name']:
            extra_words.update(keywords.get(k, []))

    if category == 'usernames':
        base_words = enrich_usernames(keywords)

    base_words = list(set(base_words) | extra_words)
    output = set()
    attempts = 0
    max_attempts = count * 10

    while len(output) < count and base_words and attempts < max_attempts:
        word = random.choice(base_words)
        year = str(random.randint(1950, 2025))
        suffix = random.choice(['!', '@', '#', '', '_', '.', '123'])
        mutated = mutate_word(word)

        candidates = [
            word,
            mutated,
            word + suffix,
            mutated + suffix,
            word + year,
            mutated + year,
            word + year + suffix,
            mutated + year + suffix,
        ]

        for c in candidates:
            if policy_type == "password":
                if not enforce_policy or validate_password_policy(c):
                    output.add(c)
            elif policy_type == "username":
                if validate_username_policy(c):
                    output.add(c)
            if len(output) >= count:
                break
        attempts += 1

    if len(output) < count:
        logging.warning(f"Only generated {len(output)} out of {count} requested {policy_type}s.")
        missing = count - len(output)
        fallback_name = (keywords.get('usernames') or ["user"])[0].lower()
        while len(output) < count:
            fallback = f"{fallback_name}{random.randint(1000,9999)}"
            if validate_username_policy(fallback):
                output.add(fallback)

    return list(output)[:count]


def generate_wordlist(keywords, company_name="target", username_count=1000, password_count=1000):
    logger = setup_logger(company_name)
    try:
        logger.info("[Generator] Generating usernames and passwords...")
        logger.debug(f"[Generator] Raw keyword input: {keywords}")

        if username_count not in [500, 1000, 5000] or password_count not in [500, 1000, 5000]:
            logger.warning("[Generator] Unsupported count provided, defaulting to 1000 for both.")
            username_count = 1000
            password_count = 1000

        if not keywords.get('usernames'):
            logger.warning("[Generator] No usernames found, adding fallback username.")
            keywords['usernames'] = [company_name]
        if not keywords.get('generic'):
            logger.warning("[Generator] No generic keywords found, adding fallback password seed.")
            keywords['generic'] = [company_name]

        usernames = generate_variations(keywords, 'usernames', username_count, enforce_policy=True, policy_type="username")
        passwords = generate_variations(keywords, 'generic', password_count, enforce_policy=True, policy_type="password")

        if not usernames or not passwords:
            logger.error("[Generator] Failed: Not enough keywords to generate wordlists.")
            print("[!] Error: Failed to generate wordlists. Check logs for details.")
            raise ValueError("Insufficient data for wordlist generation")

        os.makedirs("wordlists", exist_ok=True)
        date_str = datetime.now().strftime("%Y-%m-%d")
        # Prefer full_name or fallback to company_name or default "target"
        target_base = (
        (keywords.get('full_name') or [company_name]) or ["target"])[0]
        safe_target = target_base.replace(' ', '_')

        username_path = f"wordlists/{safe_target}_{date_str}_usernames.txt"
        password_path = f"wordlists/{safe_target}_{date_str}_passwords.txt"

        with open(username_path, 'w') as ufile:
            for user in usernames:
                ufile.write(user + '\n')
        logger.info(f"[Generator] Saved {username_count} usernames to {username_path}")

        with open(password_path, 'w') as pfile:
            for pw in passwords:
                pfile.write(pw + '\n')
        logger.info(f"[Generator] Saved {password_count} passwords to {password_path}")

        return usernames + passwords

    except Exception as e:
        logger.error(f"[Generator] Exception occurred: {e}")
        print(f"[!] Generator failed with exception: {e}")
        raise
