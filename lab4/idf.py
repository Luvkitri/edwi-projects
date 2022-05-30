import re
import requests
import sqlite3

from sqlite3 import Error
from collections import deque


class DBController:
    def __init__(self) -> None:
        self.connection = None

    def create_connection(self, db_file="data.db"):
        try:
            self.connection = sqlite3.connect(db_file)
            print(sqlite3.version)
        except Error as e:
            print(e)
            if self.connection:
                self.connection.close()

    def create_table(self, sql):
        try:
            cursor = self.connection.cursor()
            cursor.execute(sql)
        except Error as e:
            print(e)

    def insert_row(self, table_name, data):
        sql = f"""INSERT INTO {table_name}({','.join(data.keys())})
              VALUES({','.join('?' for _ in data.keys())}) """

        if not self.connection:
            print("connection not established")
            return

        cursor = self.connection.cursor()
        cursor.execute(sql, tuple(data.values()))
        self.connection.commit()
        return cursor.lastrowid

    def clear_table(self, table_name):
        sql = f"""DELETE FROM {table_name};"""

        cursor = self.connection.cursor()
        cursor.execute(sql)
        print("We have deleted", cursor.rowcount, "records from the table.")
        self.connection.commit()
        self.connection.execute("VACUUM")

    def close_connection(self):
        self.connection.close()


class Scrapper:
    def __init__(
        self, urls: list, number_of_sub_pages: int, db_controller: DBController
    ) -> None:
        self.urls = urls
        self.number_of_sub_pages = number_of_sub_pages
        self.db_controller = db_controller

    def retrieve_inner_urls(self, text, domain: str):
        relative_paths = set(re.findall(r"(?<=href=\")(?:/).+?(?=\")", text))
        urls = set(
            re.findall(
                f'(?<=href=")(?:https|http)(?:://)(?:www.)?(?:{domain}).+?(?=")', text
            )
        )

        internal_urls = {"https://" + domain + path for path in relative_paths}

        return urls | internal_urls

    def retrieve_content(self, text):
        p = re.compile(
            r"(<script.*?>[\S\s]*?</script>)|(<style.*?>[\S\s]*?</style>)|(<[\S\s]*?>)|(&nbsp;)|[|]"
        )

        # Remove tags
        content = p.sub("", text)

        # Remove unnecessary spaces
        content = re.sub("\s\s+", " ", content)

        # Remove new lines
        content = re.sub("\n", " ", content)

        return content

    def get_domain(self, url):
        for domain in self.urls:
            if domain in url:
                return domain

        return None

    def pretty_print(
        self, req=None, error=False, error_message="", additional_info="", url=""
    ):
        if error:
            if req != None:
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
                    "{}\n{}\n{}\n{}\n{}".format(
                        "-------------ERROR--------------",
                        error_message,
                        "-----------REQUEST TO-----------",
                        url,
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

    def fetch_data(self, url: str):
        try:
            # Get request head
            req_head = requests.head(url, timeout=10)
            req_head.raise_for_status()
        except requests.exceptions.Timeout:
            self.pretty_print(error=True, error_message="Request timeout", url=url)
            return None
        except requests.exceptions.TooManyRedirects:
            self.pretty_print(error=True, error_message="Incorrect URL", url=url)
            return None
        except requests.exceptions.HTTPError:
            self.pretty_print(
                req_head,
                error=True,
                error_message="Bad status code",
            )
            return None
        except requests.exceptions.RequestException as e:
            self.pretty_print(error=True, error_message=str(e), url=url)
            return None

        if "Content-Type" in req_head.headers:
            if "text/html" not in req_head.headers["Content-Type"]:
                self.pretty_print(
                    req_head,
                    error=True,
                    error_message="Bad Content-Type",
                    additional_info=req_head.headers["Content-Type"],
                )
                return None
        elif "Content-type" in req_head.headers:
            if "text/html" not in req_head.headers["Content-type"]:
                self.pretty_print(
                    req_head,
                    error=True,
                    error_message="Bad Content-Type",
                    additional_info=req_head.headers["Content-type"],
                )
                return None
        elif "content-type" in req_head.headers:
            if "text/html" not in req_head.headers["content-type"]:
                self.pretty_print(
                    req_head,
                    error=True,
                    error_message="Bad Content-Type",
                    additional_info=req_head.headers["content-type"],
                )
                return None

        if req_head.status_code == 204:
            self.pretty_print(
                req_head,
                error=True,
                error_message="Bad status code",
            )
            return None

        req = requests.get(url, timeout=10)

        return req.text

    def scrap(self):
        self.db_controller.clear_table("scrap")

        url_queue = deque()
        total_visited_pages = set()

        for url in self.urls:
            url_queue.append(f"https://{url}")

            visited_pages = set()

            while url_queue and len(visited_pages) < self.number_of_sub_pages:
                current_url = url_queue.pop()

                page_text = self.fetch_data(current_url)

                if not page_text:
                    continue
                
                visited_pages.add(current_url)

                domain = self.get_domain(url=current_url)
                urls = self.retrieve_inner_urls(text=page_text, domain=domain)
                content = self.retrieve_content(text=page_text)

                for url in urls:
                    if url not in url_queue and url not in total_visited_pages:
                        url_queue.appendleft(url)

                self.db_controller.insert_row(
                    "scrap",
                    {
                        "domain": domain,
                        "url": current_url,
                        "text": content,
                        "bow": str([]),
                        "tfidf": str([]),
                    },
                )

            total_visited_pages |= visited_pages
            url_queue.clear()

        self.db_controller.close_connection()
