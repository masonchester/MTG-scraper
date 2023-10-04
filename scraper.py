from bs4 import BeautifulSoup
import requests

# Using a set to store unique links and improve performance
links = set()
keywords = ["https", "http", "#cite"]
def crawl(init_url, relative_url, depth):
    try:
        full_url = init_url + relative_url

        print(full_url)

        response = requests.get(full_url, timeout=5)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            if depth > 0:
                for text in soup.find_all('p'):
                    for link in text.find_all('a'):
                        new_relative_url = link.get("href")

                        # Check if the URL is relative and not already crawled
                        if new_relative_url and new_relative_url not in links:
                            if not any(i in new_relative_url for i in keywords):
                                links.add(new_relative_url)
                                crawl(init_url, new_relative_url, depth - 1)

    except Exception as e:
        print("Error crawling website: " + full_url)

init_url = "https://mtg.fandom.com"
crawl(init_url, "/wiki/Portal:Story", 3)
