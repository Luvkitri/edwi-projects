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
        self.visited_urls = {}

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
        pattern = re.compile(r"<.*?>")
        return pattern.sub("", text)

    def run(self) -> None:
        self.url_queue.append(self.initial_url)

        # Create an initial csv file

        i = 0

        while i < 1:
            makedirs(path.join(self.RESULTS_PATH, f"layer{i}"))
            with open(
                path.join(self.RESULTS_PATH, f"layer{i}", f"content{i}.csv"),
                mode="w+",
            ) as csv_content_file, open(
                path.join(self.RESULTS_PATH, f"layer{i}", f"emails{i}.csv"), mode="w+"
            ) as csv_email_file:
                # Init content writer
                content_writer = csv.DictWriter(
                    csv_content_file, delimiter="`", fieldnames=["URL", "Content"]
                )

                # Add the headers
                content_writer.writeheader()

                # Init email writer
                email_writer = csv.DictWriter(
                    csv_email_file, delimiter="`", fieldnames=["URL", "Emails"]
                )

                # Add the headers
                email_writer.writeheader()

                # Start crawling
                current_url = self.url_queue.pop()
                req = requests.get(current_url)
                original_content = req.text

                emails = self.retrive_emails(original_content)
                urls = self.retrive_urls(original_content)
                content = self.retrive_content(original_content)

                content_writer.writerow({"URL": current_url, "Content": content})
                email_writer.writerow({"URL": current_url, "Emails": " ".join(emails)})

                csv_content_file.close()
                csv_email_file.close()

            i += 1
