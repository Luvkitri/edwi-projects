import csv
import email
import re
import requests

from os import path, makedirs
from collections import deque


class Crawler:
    def __init__(self, initial_url: str) -> None:
        self.initial_url = initial_url
        self.default_url = re.search(r"(?:.+?(?=/)){3}", initial_url).group()
        self.url_queue = deque()
        self.visited_urls = set()

        self.RESULTS_PATH = "lab1/results"

    def retrive_emails(self, text):
        # ?<= non-capturing group - match what precedes mailto:
        return set(re.findall(r"(?<=mailto:).+?(?=\")", text))

    def retrive_urls(self, text):
        relative_paths = set(re.findall(r"(?<=href=\")(?:/).+?(?=\")", text))
        external_urls = set(re.findall(r"(?<=href=\")(?:https|http).+?(?=\")", text))

        internal_urls = {self.default_url + path for path in relative_paths}

        return internal_urls | external_urls

    def retrive_content(self, text):
        return re.findall(r"(?:\s*<.*?>)*(.*?)\s*(?:<.*?>\s*)", text)

    def run(self) -> None:
        self.url_queue.append(self.initial_url)

        i = 0

        while self.url_queue or i < self.depth:
            makedirs(path.join(self.RESULTS_PATH, f"layer{i}"), exist_ok=True)
            with open(
                path.join(self.RESULTS_PATH, f"layer{i}", f"content{i}.csv"),
                mode="w+",
                newline="",
            ) as csv_content_file, open(
                path.join(self.RESULTS_PATH, f"layer{i}", f"emails{i}.csv"),
                mode="w+",
                newline="",
            ) as csv_email_file:
                # Init content writer
                content_writer = csv.DictWriter(
                    csv_content_file, delimiter="|", fieldnames=["URL", "Content"]
                )

                # Add the headers
                content_writer.writeheader()

                # Init email writer
                email_writer = csv.DictWriter(
                    csv_email_file, delimiter="|", fieldnames=["URL", "Emails"]
                )

                # Add the headers
                email_writer.writeheader()

                urls_buffer = set()

                while self.url_queue:
                    # Pop the first in queue url
                    current_url = self.url_queue.pop()

                    # Get the html content
                    req = requests.get(current_url)
                    original_content = req.text

                    # Retrive necessary data
                    emails = self.retrive_emails(original_content)
                    urls = self.retrive_urls(original_content)
                    content = self.retrive_content(original_content)

                    urls_buffer = urls_buffer | urls

                    # Save extracted data
                    content_writer.writerow(
                        {"URL": current_url, "Content": " ".join(content)}
                    )
                    email_writer.writerow(
                        {"URL": current_url, "Emails": " ".join(emails)}
                    )

                    # Add to visited urls
                    self.visited_urls.add(current_url)

                for url in urls_buffer:
                    self.url_queue.appendleft(url)

                i += 1

                csv_content_file.close()
                csv_email_file.close()
