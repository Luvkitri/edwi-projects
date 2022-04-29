from lab1.crawler import Crawler


def main():
    crawler = Crawler("https://www.wordstream.com/blog/ws/2015/02/09/how-to-write-a-blog-post", 2)
    crawler.run()


if __name__ == "__main__":
    main()
