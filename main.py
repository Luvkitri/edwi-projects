import json
import sys


from os import path, listdir, getcwd
from lab1.crawler import Crawler
from lab2.indexer import Indexer
from lab3.ngram import NGramGenerator, NGramComparator


def word_finder():
    with open("invertedIndex.json") as inverted_index_file:
        data = json.load(inverted_index_file)

        while True:
            search_word = input("Search for word: ")

            if search_word in data["invertedIndex"]:
                for key, value in data["invertedIndex"][search_word].items():
                    url = data["urls"][key]
                    print(
                        f"URL {url}\nNumber of occurrences: {len(value)}\nPositions: {value}\n"
                    )


def lab1(argv):
    url = ""
    depth = 100

    try:
        if len(argv) == 2:
            url = argv[0]
            depth = argv[1]
        elif len(argv) == 1:
            url = argv[0]
        else:
            raise Exception("No url provided")

        crawler = Crawler(url, int(depth))
        crawler.run()
    except Exception as error:
        print(repr(error))


def lab2():
    abs_path = path.abspath(getcwd())
    content_path = path.join(abs_path, "lab1/results")

    # Get all the results dirs
    results_dirs = [path.join(content_path, d) for d in listdir(content_path)]
    latest_results_dir = max(results_dirs, key=path.getmtime)

    indexer = Indexer(latest_results_dir)
    indexer.run()        
    


def lab3_generator():
    abs_path = path.abspath(getcwd())
    content_path = path.join(abs_path, "lab1/results")

    # Get all the results dirs
    results_dirs = [path.join(content_path, d) for d in listdir(content_path)]
    latest_results_dir = max(results_dirs, key=path.getmtime)

    n_gram_generator = NGramGenerator(latest_results_dir, 2)
    n_gram_generator.run()
    
def lab3_comparator():
    comparator = NGramComparator('https://en.wikipedia.org/wiki/Mazda', 1)
    comparator.run()

def main(argv):
    # https://en.wikipedia.org/wiki/Mazda_MX-5 2

    # ! Lab 1
    # lab1(argv)

    # ! Lab 2
    # lab2()

    # Pseudo word finder
    # word_finder()

    # ! lab 3
    lab3_generator()


if __name__ == "__main__":
    main(sys.argv[1:])
