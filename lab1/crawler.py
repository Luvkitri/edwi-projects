import csv
import email
import re
import requests


from os import path, makedirs
from collections import deque
from datetime import datetime

"""TODO
    relative paths with / or without
    ignore writing ro if no mail found for given url
    write email for given url one by one? maybe
    Request filtering content-type text/html, request timeout would be nice, ignore 400 and 500 requests, request head (just to check if those are gucci)
    DONE: Ignore scripts and styles etc (mainly body)
    more info in queue
    indexing
"""


class Crawler:
    def __init__(self, initial_url: str, depth: int) -> None:
        self.initial_url = initial_url
        self.depth = depth
        self.default_url = re.search(r"(?:.+?(?=/)){3}", initial_url).group()
        self.url_queue = deque()
        self.visited_urls = set()

        default_path = "lab1/results/results"
        current_date = datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%f%z")

        self.RESULTS_PATH = f"{default_path}-{current_date}"

        makedirs(self.RESULTS_PATH)

    def retrive_emails(self, text):
        # ?<= non-capturing group - match what precedes mailto:
        return set(re.findall(r"(?<=mailto:).+?(?=\")", text))

    def retrive_urls(self, text):
        relative_paths = set(re.findall(r"(?<=href=\")(?:/).+?(?=\")", text))
        external_urls = set(re.findall(r"(?<=href=\")(?:https|http).+?(?=\")", text))

        internal_urls = {self.default_url + path for path in relative_paths}

        return internal_urls | external_urls

    def retrive_content(self, text):
        p = re.compile(
            r"(<script.*?>[\S\s]*?</script>)|(<style.*?>[\S\s]*?</style>)|(<[\S\s]*?>)|(&nbsp;)"
        )

        # Remove tags
        content = p.sub("", text)

        # Remove unnecessary spaces
        content = re.sub("\s\s+", " ", content)

        return content

    def pretty_print(self, req, error=False, error_message="", additional_info=""):
        if error:
            print(
                "{}\n{}\n{}\n{}\n{}".format(
                    "------------ERROR------------",
                    error_message,
                    "-----------REQUEST-----------",
                    "GET " + str(req.status_code) + " " + req.url,
                    additional_info,
                )
            )
        else:
            print(
                "{}\n{}\n{}".format(
                    "-----------REQUEST-----------",
                    "GET " + str(req.status_code) + " " + req.url,
                    additional_info,
                )
            )
            
        print()

    def run(self) -> None:
        self.url_queue.append(self.initial_url)

        i = 0

        while self.url_queue and i < self.depth:
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

                    # Get the request head
                    try:
                        req_head = requests.head(current_url, timeout=10)
                    except:
                        self.pretty_print(
                            req_head,
                            error=True,
                            error_message="Request timeout",
                        )
                        continue
                    if req_head.status_code >= 400:
                        self.pretty_print(
                            req_head,
                            error=True,
                            error_message="Bad status code",
                            additional_info=req_head.headers["Content-type"],
                        )
                        continue

                    if "Content-Type" in req_head.headers:
                        if "text/html" not in req_head.headers["Content-Type"]:
                            self.pretty_print(
                                req_head,
                                error=True,
                                error_message="Bad Content-Type",
                                additional_info=req_head.headers["Content-Type"],
                            )
                            continue
                    elif "Content-type" in req_head.headers:
                        if "text/html" not in req_head.headers["Content-type"]:

                            self.pretty_print(
                                req_head,
                                error=True,
                                error_message="Bad Content-Type",
                                additional_info=req_head.headers["Content-type"],
                            )
                            continue
                    elif "content-type" in req_head.headers:
                        if "text/html" not in req_head.headers["content-type"]:
                            self.pretty_print(
                                req_head,
                                error=True,
                                error_message="Bad Content-Type",
                                additional_info=req_head.headers["content-type"],
                            )
                            continue

                    req = requests.get(current_url, timeout=10)

                    original_content = req.text

                    # Retrive necessary data
                    emails = self.retrive_emails(original_content)
                    urls = self.retrive_urls(original_content)
                    content = self.retrive_content(original_content)

                    urls_buffer = urls_buffer | urls

                    # Save extracted data

                    if content:
                        content_writer.writerow(
                            {"URL": current_url, "Content": content}
                        )

                    if emails:
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
