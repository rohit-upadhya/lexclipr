import requests
from bs4 import BeautifulSoup
import urllib.request
import urllib.error

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time

def fetch_webpage_content(url):
    chrome_driver_path = '/path/to/chromedriver/chromedriver'
    service = Service(chrome_driver_path)
    
    driver = webdriver.Chrome(service=service)

    driver.get(url)

    time.sleep(5)

    html_content = driver.page_source
    driver.quit()
    
    return html_content

def find_paragraphs_recursively(element, paragraph_number):
    matching_paragraphs = []
    if element.name == 'p' and f"§ {paragraph_number}" in element.get_text():
        matching_paragraphs.append(element.get_text())
    
    for child in element.find_all(recursive=False):
        matching_paragraphs.extend(find_paragraphs_recursively(child, paragraph_number))
    
    return matching_paragraphs

def find_paragraph_by_number(html_content, paragraph_number):
    soup = BeautifulSoup(html_content, 'html.parser')
    
    matching_paragraphs = find_paragraphs_recursively(soup, paragraph_number)
    
    return matching_paragraphs

if __name__ == "__main__":
    url = "https://hudoc.echr.coe.int/eng?i=001-211972"
    paragraph_number = 97

    try:
        html_content = fetch_webpage_content(url)
        paragraphs = find_paragraph_by_number(html_content, paragraph_number)

        if paragraphs:
            for i, paragraph_text in enumerate(paragraphs, 1):
                print(f"Paragraph § {paragraph_number} - Match {i}:\n{paragraph_text}\n")
        else:
            print(f"Paragraph § {paragraph_number} not found.")
    except Exception as e:
        print(f"Error: {e}")
