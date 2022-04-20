from lab1.crawler import Crawler


def main():
    crawler = Crawler("https://p.lodz.pl/en/about-tul/contact")
    crawler.run()


if __name__ == "__main__":
    main()
