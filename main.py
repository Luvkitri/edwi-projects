import sys
from lab1.crawler import Crawler


def main(argv):
    url = ''
    depth = 100
    
    try:
        if len(argv) == 2:
            url = argv[0]
            depth = argv[1]
        elif len(argv) == 1:
            url = argv[0]
        else:
            raise Exception('No url provided')
            
        crawler = Crawler(url, int(depth))
        crawler.run()
    except Exception as error:
        print(repr(error))

if __name__ == "__main__":
    main(sys.argv[1:])
