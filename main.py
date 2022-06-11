import json
import sys
import numpy as np


from os import path, listdir, getcwd

from lab1.crawler import Crawler
from lab2.indexer import Indexer
from lab3.ngram import NGramGenerator, NGramComparator
from lab4.idf import DBController, Scrapper, Vectorizer
from lab6.bot import send_form


def jacard_distance(first_vector, second_vector):
    jacc_num = 0 
    jacc_den = 0 
    
    for first_value, second_value in zip(first_vector, second_vector):
        if first_value != 0 or second_value != 0:
            jacc_den += max(first_value, second_value) 
            jacc_num += min(first_value, second_value) 
            
    return jacc_num / jacc_den 


def cos_distance(first_vector, second_vector):
    if len(first_vector) != len(second_vector):
        return 0

    a = np.array(first_vector)
    b = np.array(second_vector)
    return np.dot(a, b) / ((np.dot(a, a) ** 0.5) * (np.dot(b, b) ** 0.5))


def compare(db_controller: DBController, _id: int):
    document_ids = db_controller.select_ids()
    selected_doc_tf_idf = eval(
        db_controller.select_row_by_id(_id, "scrap", columns=["tfidf"])[0]
    )

    jacard_distances = {}
    cos_distances = {}

    for _id in document_ids:
        row = db_controller.select_row_by_id(*_id, "scrap", columns=["url", "tfidf"])
        url = row[0]
        tf_idf = eval(row[1])

        jacard_distances[url] = jacard_distance(selected_doc_tf_idf, tf_idf)
        cos_distances[url] = cos_distance(selected_doc_tf_idf, tf_idf)
        
    with open("lab4-jacard-distances.json", mode="w+") as jacard_file:
        json.dump(jacard_distances, jacard_file, indent=4)
        
    with open("lab4-cos-distances.json", mode="w+") as cos_file:
        json.dump(cos_distances, cos_file, indent=4) 


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


def lab3():
    # abs_path = path.abspath(getcwd())
    # content_path = path.join(abs_path, "lab1/results")

    # # Get all the results dirs
    # results_dirs = [path.join(content_path, d) for d in listdir(content_path)]
    # latest_results_dir = max(results_dirs, key=path.getmtime)

    # n_gram_generator = NGramGenerator(latest_results_dir, 1, "1-grams-mazda")
    # n_gram_generator.run()

    # n_gram_generator = NGramGenerator(latest_results_dir, 2, "2-grams-mazda")
    # n_gram_generator.run()

    # n_gram_generator = NGramGenerator(latest_results_dir, 3, "3-grams-mazda")
    # n_gram_generator.run()

    comparator = NGramComparator(
        "https://en.wikipedia.org/wiki/Mazda",
        1,
        2,
        "2-grams-mazda",
    )
    comparator.run()
    comparator.top_jacard(3)
    comparator.top_cos(3)
    
def lab4():
    db_controller = DBController()
    db_controller.create_connection()
    db_controller.drop_table(table_name="scrap")
    db_controller.create_table(
        """
                            CREATE TABLE IF NOT EXISTS scrap (
                                id INTEGER PRIMARY KEY,
                                domain TEXT NOT NULL,
                                url TEXT NOT NULL,
                                text TEXT NOT NULL,
                                words TEXT NOT NULL,
                                bow TEXT,
                                tf TEXT,
                                tfidf TEXT
                            );
        """
    )

    urls = ["realpython.com", "ft.com", "pcgamer.com", "dnd.wizards.com", "espn.com"]

    scrapper = Scrapper(
        urls=urls,
        number_of_sub_pages=100,
        db_controller=db_controller,
        table_name="scrap",
    )
    scrapper.scrap()

    vectorizer = Vectorizer(db_controller=db_controller, table_name="scrap")
    vectorizer.generate()
    
    compare(db_controller, 1)

    db_controller.close_connection()
    
def lab6():
    send_form()


def main(argv):
    # https://en.wikipedia.org/wiki/Mazda_MX-5 2

    # 5m 29s
    # ! Lab 1
    # lab1(argv)

    # 10s
    # ! Lab 2
    # lab2()

    # Pseudo word finder
    # word_finder()

    # ! Lab 3
    # lab3()
    
    # ! Lab 4
    # lab4()
    
    # ! Lab 6
    lab6()

    


if __name__ == "__main__":
    main(sys.argv[1:])
