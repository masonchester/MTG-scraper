from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from queue import Queue
import requests


visited_urls = set([])
thread_queue = Queue()

keywords = ["wikipedia", "cite", "scryfall"]
def crawl(url, depth):
    try:

        print("Crawling: ",  url)
        response = requests.get(url, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if depth > 0:
                for text in soup.find_all('p'):
                    for link in text.find_all('a'):
                        rel_url = link.get("href")

                        if rel_url and rel_url not in visited_urls:
                            if not any(i in rel_url for i in keywords):
                                new_url = urljoin(url, rel_url)
                                thread_queue.put(new_url)
                                visited_urls.add(new_url)
                                crawl(new_url, depth - 1)

    except Exception as e:
        print("Error crawling website: " + full_url)


def threaded_crawl(url, depth, max_workers):
    thread_queue.put(url)

    executor = ThreadPoolExecutor(max_workers=max_workers)
    while not thread_queue.empty():
        current_url = thread_queue.get()
        executor.submit(crawl,current_url, depth)


url = "https://mtg.fandom.com/wiki/Portal:Story"
threaded_crawl(url, depth=3, max_workers=5)



