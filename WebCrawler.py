import threading
from queue import Queue
import requests
from bs4 import BeautifulSoup

class WebCrawler:
    def __init__(self, seed_urls, max_threads=5):
        self.seed_urls = seed_urls
        self.max_threads = max_threads
        self.url_queue = Queue()
        self.visited_urls = set()

    def crawl(self):
        for url in self.seed_urls:
            self.url_queue.put(url)

        threads = []
        for _ in range(self.max_threads):
            thread = threading.Thread(target=self._worker)
            thread.start()
            threads.append(thread)

        self.url_queue.join()

        for _ in range(self.max_threads):
            self.url_queue.put(None)

        for thread in threads:
            thread.join()

    def _worker(self):
        while True:
            url = self.url_queue.get()
            if url is None:
                break

            try:
                if url not in self.visited_urls:
                    self._download_and_parse(url)
                    self.visited_urls.add(url)
            except Exception as e:
                print(f"Error processing {url}: {e}")

            print(f"Processed: {url}")
            self.url_queue.task_done()

    def _download_and_parse(self, url):
        response = requests.get(url)
        response.raise_for_status()

        html_content = response.text
        self._parse(html_content)

    def _parse(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        quotes = [quote.text for quote in soup.find_all('span', class_='text')]
        print(f"Quotes extracted from {len(quotes)} found: {quotes}")

# Example usage with the quotes.toscrape.com website
seed_urls = ['http://quotes.toscrape.com']
crawler = WebCrawler(seed_urls)
crawler.crawl()