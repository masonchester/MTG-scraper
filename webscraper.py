from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue
import requests
import os
import re


class WebScraper():

    def __init__(self, seed_url, keyword, exclusions):

        self.seed_url = seed_url
        self.keyword = keyword
        self.exclusions = exclusions
        self.job_queue = Queue()

    def crawl(self):

        response = requests.get(self.seed_url, timeout=5)

        if response.status_code == 200:

            soup = BeautifulSoup(response.content, 'html.parser')

            div = soup.find('div', class_="mw-parser-output")

           # Remove unwanted elements like references and table of contents
            for unwanted_div in div.find_all(['aside', 'table', 'ol']):
                unwanted_div.extract()

            urls = div.find_all('a', href=True)
            count = 0
            for foud_url in urls:
                url = foud_url['href']
                full_url = urljoin(self.seed_url, url)
                if full_url not in self.job_queue.queue:
                    if self.keyword in full_url:
                        if not any(exclusion in full_url for exclusion in self.exclusions):
                            self.job_queue.put(full_url)
                            count += 1

    def scrape(self):

        url = self.job_queue.get()

        response = requests.get(url, timeout=5)

        if response.status_code == 200:

            soup = BeautifulSoup(response.content, 'html.parser')

            div = soup.find('div', class_="mw-parser-output")

            unwanted_elements = [div.find('div', class_="toc")]
            unwanted_elements.extend(div.find('div', class_="reflist"))
            unwanted_elements.extend(div.find_all('div', class_="div-col columns column-width"))
            unwanted_elements.extend(div.find_all('table'))
            unwanted_elements.extend(div.find_all(['h1','h2','h3']))



            for element in unwanted_elements:
                if element is not None:
                    element.extract()
            title = soup.find('h1', class_="page-header__title")

            # Clean and format the title for use as a filename
            title = title.get_text(strip=True)
            title = re.sub(r'\s+', '-', title)

            # Build the file path
            path = os.path.expanduser("~/MTG-scraper/data/") + title + ".txt"

            with open(path, "w", encoding="utf-8") as file:
                for chunk in div.get_text(strip=True):
                    file.write(chunk)

    def threaded_scrape(self, max_workers):
        self.crawl()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while not self.job_queue.empty():
                executor.submit(self.scrape)


webscraper = WebScraper(seed_url="https://mtg.fandom.com/wiki/Timeline", keyword='mtg.fandom',
                        exclusions=['cite', 'Category', "Timeline", "veaction", "action", "sources"])
webscraper.crawl()
webscraper.scrape()
webscraper.scrape()
webscraper.scrape()
webscraper.scrape()