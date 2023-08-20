import requests 
import pandas as pd
import os
import logging
from datetime import datetime

API_URL = 'https://api.phila.gov/phila/publications/archives?count=-1'
DIRECTORY_PATH = '../ScrapeBox/publications'
CSV_FILE = os.path.join(DIRECTORY_PATH, 'publications_data.csv')
LOG_DIRECTORY_PATH = '../logBox'
CURRENT_DATETIME = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIRECTORY_PATH, f'publications_log_{CURRENT_DATETIME}.log')

# Ensure log directory exists
os.makedirs(LOG_DIRECTORY_PATH, exist_ok=True)

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)

logger.addHandler(handler)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def fetch_data(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        logger.info("Successfully fetched data from the API.")
        return response.json()
    else:
        logger.error(f"Failed to retrieve data. Status code: {response.status_code}")
        return []

def process_data(data):
    # Transform data into DataFrame format
    records = []
    for entry in data:
        categories = ";".join([cat['name'] for cat in entry['categories']])
        
        # Prepend www.phila.gov to the link
        link = "www.phila.gov" + entry['link'] if not entry['link'].startswith("www.phila.gov") else entry['link']
        
        records.append([entry['id'], entry['title'], entry['template'], entry['date'], link, categories])
    
    logger.info(f"Processed {len(records)} records from the fetched data.")
    return pd.DataFrame(records, columns=['ID', 'Title', 'Template', 'Date', 'Link', 'Categories'])

def update_data():
    # Ensure the directory exists
    os.makedirs(DIRECTORY_PATH, exist_ok=True)
    logger.info(f"Ensured the existence of directory: {DIRECTORY_PATH}")

    data = fetch_data(API_URL)
    if not data:
        return

    api_df = process_data(data)

    # If CSV doesn't exist, create it
    if not os.path.exists(CSV_FILE):
        api_df.to_csv(CSV_FILE, index=False)
        logger.info(f"Created new CSV file at {CSV_FILE}")
        return

    # If CSV exists, load and update
    local_df = pd.read_csv(CSV_FILE)

    # Merge dataframes, update old records and append new ones
    updated_df = local_df.merge(api_df, on='ID', how='right', suffixes=('', '_new'))

    # Update old records
    for column in ['Title', 'Template', 'Date', 'Link', 'Categories']:
        updated_df[column] = updated_df[column + '_new'].combine_first(updated_df[column])
        updated_df = updated_df.drop(column + '_new', axis=1)

    updated_df.to_csv(CSV_FILE, index=False)
    logger.info(f"Updated CSV file at {CSV_FILE}")

update_data()
