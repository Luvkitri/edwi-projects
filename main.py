from lab1.crawler import Crawler


def main():
    crawler = Crawler("https://sopython.com/canon/97/writing-csv-adds-blank-lines-between-rows/")
    crawler.run()


if __name__ == "__main__":
    main()
