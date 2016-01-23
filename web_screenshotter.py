"""
Module to automate taking screenshots from websites.

Current features:
- URLs list from file (one URL per line) given from command line
- Specify one URL from command line
"""

import os
import sys
import logging
import datetime
import argparse

from selenium import webdriver
from bs4 import BeautifulSoup
import requests


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] - %(name)s - %(levelname)s - %(message)s')

console_handler.setFormatter(formatter)
logger.addHandler(console_handler)
logger.info('Logging initialized')

visited = set()
to_visit = set()

HEADERS = {'User-Agent': 'Mozilla/5.0'}
navigate = False

def save_screenshot(driver, url):
    """
    Saves screenshot from URL under screenshots/YYYY-MM-DD directory.
    
    :param driver: Selenium webdriver instance
    :type driver: webdriver instance
    :param url: Web address
    :type url: str
    """
    try:
        driver.get(url)
        
        dt = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d')
        file_name = url.replace('http://', '').replace('/', '-').replace(':', '-').replace('.html', '') + '.png'
        path = os.path.join(os.path.abspath(os.curdir), 'screenshots/{}'.format(dt))
        os.makedirs('screenshots/{}'.format(dt), exist_ok=True)
        f = os.path.join(path, file_name)
        
        logger.info(f)
        
        driver.get_screenshot_as_file(f)
    except Exception as e:
        logger.error(e)

def take_screenshot():
    """
    Goes to every filtered link within the given URL, taking screenshots.
    """
    try:
        driver = webdriver.Firefox()
        for url in list(to_visit):
            save_screenshot(driver, url)
            visited.add(url)
            to_visit.remove(url)
    except Exception as e:
        logger.error(e)
    finally:
        driver.quit()
            
def fix_url(url):
    """
    Ensures url format is valid, fixes it if necessary
    
    :param url: The web address to verify
    :type url: str
    """
    if 'http://' not in url and 'https://' not in url:
        url = 'http://' + url
    return url

def process(base_url):
    """
    Collects all 'filtered' links within an URL
    
    :param base_url: Main web address to parse
    :type base_url: str
    """
    logger.info('Processing {}'.format(base_url))
    exceptions = ['.css', '.js', '.zip', '.tar.gz', '.jar', '.txt', '.json']
    logger.info('Ignoring links containing: {}'.format(exceptions))
    soup = BeautifulSoup(requests.get(base_url).content, 'lxml')
    urls = [href['href'] for href in soup.find_all(href=True) if href['href'] not in exceptions]
    for url in urls:
        if base_url in url:
            to_visit.add(url)

def process_url(url):
    """
    Wraps functionality & logic to take screenshots for every 'filtered link' in URL
    
    :param url: Web address to take screenshots from
    :type url: str
    """
    process(url)
    while to_visit:
        take_screenshot()
    logging.info('No urls left to process from {}. Finishing...'.format(url))

if __name__ == '__main__':
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-u', '--url', help='URL of the website to screenshot')
        parser.add_argument('-f', '--file', help='Filename path of list of URLs to screenshot (one URL per line)')
        args = parser.parse_args()
        
        if len(sys.argv) < 2:
            parser.print_help()
            sys.exit()
        
        if args.url:
            process_url(args.url)
        elif args.file:
            with open(args.file) as urls:
                try:
                    driver = webdriver.Firefox()
                    for url in urls:
                        save_screenshot(driver, url)
                except Exception as e:
                    logger.error(e)
                finally:
                    driver.quit()
            
    except Exception as e:
        logger.error(e)