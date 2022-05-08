import sys


from os import path, listdir
from lab1.crawler import Crawler


def main(argv):
    # ! Lab 1
    # url = ''
    # depth = 100

    # try:
    #     if len(argv) == 2:
    #         url = argv[0]
    #         depth = argv[1]
    #     elif len(argv) == 1:
    #         url = argv[0]
    #     else:
    #         raise Exception('No url provided')

    #     crawler = Crawler(url, int(depth))
    #     crawler.run()
    # except Exception as error:
    #     print(repr(error))

    # ! Lab 2

    # Get all the results dirs
    results_dirs = [d for d in listdir("./lab1/results") if path.isdir(d)]
    
    


if __name__ == "__main__":
    main(sys.argv[1:])
