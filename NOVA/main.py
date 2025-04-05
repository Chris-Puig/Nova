# main.py - NOVA Entry Point

from core.search import run_osint_queries
from core.scraper import scrape_urls
from core.extractor import extract_keywords
from core.generator import generate_wordlist
from pathlib import Path
import re

ASCII_ART = r'''

            _   _   ____  __     __    _       
           | \ | | / __ \ \ \   / /   / \     
           |  \| || |  | | \ \ / /   / _ \    
           | |\  || |__| |  \ V /   / ___ \   
           |_| \_| \____/    \_/   /_/   \_\  
        
'''

def get_user_input():
    print(ASCII_ART)
    print("=== NOVA: Custom Wordlist Generator ===\n")
    print("Leave a field empty if you want to skip it.\n")

    full_name = input("Enter target's full name (required): ").strip()
    dob = input("Enter target's date of birth (optional, e.g., 1990 or 12/08/1990): ").strip()
    company_name = input("Enter target's company name (optional): ").strip()
    location = input("Enter target's city or location (optional): ").strip()

    print("\nChoose wordlist size (500, 1000, 5000):")
    try:
        size_choice = int(input("Enter desired size: ").strip())
        if size_choice not in [500, 1000, 5000]:
            print("[!] Invalid choice. Defaulting to 1000 entries.")
            size_choice = 1000
    except ValueError:
        print("[!] Invalid input. Defaulting to 1000 entries.")
        size_choice = 1000

    if not full_name:
        print("\n[!] Full name is required. Exiting.")
        exit(1)

    return full_name, dob, company_name, location, size_choice

def main():
    full_name, dob, company_name, location, size_choice = get_user_input()

    print("\n[+] Starting NOVA Wordlist Generator...\n")

    print("[*] Running OSINT search queries...")
    search_results = run_osint_queries(full_name, company=company_name, location=location)

    if not search_results:
        print("[!] No search results found. Exiting.")
        return

    print("[*] Scraping collected URLs...")
    scraped_data = scrape_urls(search_results, company_name)

    # Add manual user inputs to the data set
    manual_data = {
        "full_name": full_name,
        "dob": dob,
        "company_name": company_name,
        "location": location
    }
    scraped_data.append(manual_data)

    print("[*] Extracting useful keywords and identities...")
    extracted_info = extract_keywords(scraped_data, company_name)

    if not extracted_info or not any(extracted_info.values()):
        print("[!] No useful data extracted. Exiting.")
        return

    print("[*] Generating custom wordlist...")
    generate_wordlist(extracted_info, company_name=company_name, username_count=size_choice, password_count=size_choice)

    print("\n[✓] Done! Your custom wordlist has been created successfully.\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Aborted by user.")
