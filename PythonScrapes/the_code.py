import requests
from bs4 import BeautifulSoup
import csv
import os
import logging
from datetime import datetime

# Logging Configuration
LOG_DIRECTORY_PATH = '../logBox'
CURRENT_DATETIME = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIRECTORY_PATH, f'code_scraping_log_{CURRENT_DATETIME}.log')

# Ensure log directory exists
os.makedirs(LOG_DIRECTORY_PATH, exist_ok=True)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)

logger.addHandler(handler)

def scrape_website(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        sections = []
        
        for entry in soup.find_all("div", class_="toc-entry"):
            toc_link = entry.find("a", class_="toc-link")
            if toc_link:
                title = toc_link.get_text(strip=True)
                link = "https://codelibrary.amlegal.com" + toc_link['href']
                sections.append((title, link))
                
        logger.info(f"Successfully scraped main page: {url}")
        return sections

    except requests.RequestException as e:
        logger.error(f"Error scraping main page: {url} - {str(e)}")
        return []

def get_links_from_section(url, main_title):
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        
        for a in soup.find_all('a', href=True):
            if not a['href'].startswith("javascript"):
                combined_title = main_title + " | " + a.get_text(strip=True)
                if "codelibrary.amlegal.com" not in a['href']:
                    link = "https://codelibrary.amlegal.com" + a['href']
                else:
                    link = a['href']

                if len(a.get_text(strip=True)) > 2:
                    title = combined_title
                else:
                    title = main_title
                links.append((title, link))

        logger.info(f"Successfully scraped section: {url}")
        return links

    except requests.RequestException as e:
        logger.error(f"Error scraping section: {url} - {str(e)}")
        return []

def write_to_csv(data, filename): 
    try:
        path = os.path.join("..", "ScrapeBox", "theCode", filename)
        
        with open(path, 'w', newline='') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(["Title", "Link"])
            for title, link in data:
                csv_writer.writerow([title, link])

        logger.info(f"Data successfully written to CSV file: {filename}")

    except Exception as e:
        logger.error(f"Error writing to CSV file: {filename} - {str(e)}")

def remove_duplicates_ordered(data):
    seen = set()
    result = []
    for item in data:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result

url = "https://codelibrary.amlegal.com/codes/philadelphia/latest/overview"
sections = scrape_website(url)

all_links = []
for title, section_link in sections:
    inner_links = get_links_from_section(section_link, title)
    all_links.extend(inner_links)

unique_links = remove_duplicates_ordered(all_links)
write_to_csv(unique_links, 'philadelphia_codes.csv')
 