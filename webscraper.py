from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from queue import Queue
import requests
import os
import re


class WebScraper():
    """Class for creating a webscraper object to scrape"""
    def __init__(self, seed_url, keyword, exclusions):

        self.seed_url = seed_url
        self.keyword = keyword
        self.exclusions = exclusions
        self.job_queue = Queue()
        self.found_urls = set()

    def crawl(self):
        """Function for crawling the seed_url and extracting all relevant URL's"""
        response = requests.get(self.seed_url, timeout=5)

        if response.status_code == 200:

            soup = BeautifulSoup(response.content, 'html.parser')

            div = soup.find('div', class_="mw-parser-output")

            unwanted_elements = [div.find('div', class_="toc")]
            unwanted_elements.extend(div.find('div', class_="references"))

            for element in unwanted_elements:
                if element is not None:
                    element.extract()

            urls = div.find_all('a', href=True)
            for found_url in urls:
                url = found_url['href']
                full_url = urljoin(self.seed_url, url)
                if full_url not in self.found_urls:
                    if self.keyword in full_url:
                        if not any(exclusion in full_url for exclusion in self.exclusions):
                            self.job_queue.put(full_url)
                            self.found_urls.add(full_url)

    def scrape(self):
        """Function for scraping found urls in seed_url."""

        url = self.job_queue.get()

        response = requests.get(url, timeout=5)

        if response.status_code == 200:

            soup = BeautifulSoup(response.content, 'html.parser')

            div = soup.find('div', class_="mw-parser-output")

            unwanted_elements = [div.find('div', class_="toc"), 
                                 div.find('ul', class_="gallery mw-gallery-traditional"),
                                 div.find('dl')]
            unwanted_elements.extend(div.find('div', class_="reflist"))
            unwanted_elements.extend(div.find_all(
                'div', class_="div-col columns column-width"))
            unwanted_elements.extend(div.find_all('table'))
            unwanted_elements.extend(div.find_all(['h1', 'h2', 'h3', "h4"]))
            unwanted_elements.extend(div.find_all('sup', class_="reference"))

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
                for chunk in div.get_text():
                    file.write(chunk)

    def threaded_scrape(self, max_workers):
        """runs the scrape method on the number of thread specified by max_workers"""
        self.crawl()
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            while not self.job_queue.empty():
                executor.submit(self.scrape)


webscraper = WebScraper(seed_url="https://mtg.fandom.com/wiki/Timeline", keyword='mtg.fandom',
                        exclusions=['cite',
                                    'Category', 
                                    "Timeline", 
                                    "veaction", 
                                    "action", 
                                    "sources"])

webscraper.threaded_scrape(max_workers=4)
