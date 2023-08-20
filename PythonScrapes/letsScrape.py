from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time

def extract_section_data(soup_element):
    data = {
        "title": None,
        "link": None,
        "sub_sections": []
    }
    link_elem = soup_element.find('a', class_='toc-link')
    if link_elem:
        data["title"] = link_elem.text
        data["link"] = link_elem['href']

    # Check for any sub-sections
    sub_section_elems = soup_element.find_all('div', class_='toc-entry', recursive=False)
    for sub_elem in sub_section_elems:
        sub_data = extract_section_data(sub_elem)
        data["sub_sections"].append(sub_data)
    
    return data

driver = webdriver.Chrome()
driver.get("https://codelibrary.amlegal.com/codes/philadelphia/latest/overview")

# Let's expand all sections first
expand_buttons = driver.find_elements(by=By.CLASS_NAME, value="toc-caret")
while expand_buttons:
    for button in expand_buttons:
        if button.is_displayed():
            button.click()
            time.sleep(1)
    expand_buttons = driver.find_elements(by=By.CLASS_NAME, value="toc-caret")

# Now, extract the data
html_source = driver.page_source
soup = BeautifulSoup(html_source, "html.parser")
top_level_sections = soup.find_all('div', class_='toc-entry', recursive=False)

data_list = []
for section in top_level_sections:
    section_data = extract_section_data(section)
    data_list.append(section_data)

# Convert data to JSON and save
path_to_save = '../ScrapeBox/theCode/code_data.json'
with open(path_to_save, 'w') as f:
    json.dump(data_list, f, indent=4)

driver.quit()
