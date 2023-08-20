import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os
import numpy as np
import logging

# Constants
URL = 'https://regulations.phila-records.com/'  # Base URL
LOG_DIRECTORY_PATH = '../logBox'
CURRENT_DATETIME_LOG = datetime.now().strftime('%Y%m%d_%H%M%S')
LOG_FILE = os.path.join(LOG_DIRECTORY_PATH, f'phila_records_log_{CURRENT_DATETIME_LOG}.log')
CSV_FILE = os.path.join('../ScrapeBox/phila-records', 'phila_records_data.csv')

# Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(formatter)

logger.addHandler(handler)

# Fetching data from the URL
response = requests.get(URL)
if response.status_code != 200:
    logger.error(f"Failed to retrieve data from URL {URL}. Status code: {response.status_code}")
    exit()  # Exit the script if the response is not successful

soup = BeautifulSoup(response.content, 'html.parser')

# Extracting regulations data
table = soup.find('table', {'id': 'grvRegulations'})
regulations_data = [
    {
        'Filing Date': columns[0].span.text,
        'Department or Agency': columns[1].span.text,
        'Regulation Title': columns[2].span.text,
        'Hearing/Report Date': columns[3].span.text,
        'Became Law': columns[4].span.text,
        'Link': ', '.join([URL + a['href'] for a in columns[5].find_all('a')])
    }
    for columns in (row.find_all('td') for row in table.find_all('tr')[1:])
]

api_df = pd.DataFrame(regulations_data).replace('', np.nan)

# Ensure the data directory exists
os.makedirs('../ScrapeBox/phila-records', exist_ok=True)
logger.info(f"Ensured the existence of directory: {'../ScrapeBox/phila-records'}")

if os.path.exists(CSV_FILE):
    local_df = pd.read_csv(CSV_FILE)
    
    # Merge dataframes using right merge to retain all records from the API and add new ones to the local file
    merged_df = pd.merge(local_df, api_df, how='right', left_on='Regulation Title', right_on='Regulation Title', suffixes=('', '_new'))
    
    # Update old records and append new ones
    for column in ['Filing Date', 'Department or Agency', 'Hearing/Report Date', 'Became Law', 'Available Documents']:
        merged_df[column] = merged_df[column + '_new'].combine_first(merged_df[column])
        merged_df = merged_df.drop(column + '_new', axis=1)

    merged_df.to_csv(CSV_FILE, index=False)
    logger.info(f"Updated CSV file at {CSV_FILE}")
else:
    api_df.to_csv(CSV_FILE, index=False)
    logger.info(f"Data saved to {CSV_FILE}")
