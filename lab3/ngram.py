import csv
import re
import json
import numpy as np
import requests

from os import getcwd, path, listdir

from lab1.crawler import Crawler


class NGramGenerator:
    def __init__(self, source_dir: str, n: int) -> None:
        self.source_dir = source_dir
        self.layers_dirs = sorted([d for d in listdir(source_dir)])
        self.n = n
        self.master_ngrams = {"1-grams": set(), "2-grams": set(), "3-grams": set()}

    def clear_content(self, content):
        cleared_content = re.findall(r"[a-zA-Z]+", content)
        return [word.lower() for word in cleared_content]

    def split_to_ngrams(self, content, n):
        n_grams = set()

        for i in range((len(content) - n + 1)):
            n_grams.add(tuple(content[i : i + n]))

        return n_grams

    def run(self):
        output = {}

        index_offset = 0

        for file_index, layer_dir in enumerate(self.layers_dirs):
            with open(
                path.join(self.source_dir, layer_dir, f"content{file_index}.csv"),
                mode="r",
            ) as csv_content_file:
                content_reader = csv.DictReader(csv_content_file, delimiter="|")

                for row in content_reader:
                    _id = int(row["index"])
                    output[row["URL"]] = {}
                    output[row["URL"]]["id"] = _id + index_offset

                    content = self.clear_content(row["Content"])

                    for n in range(1, self.n + 1):
                        n_grams = self.split_to_ngrams(content, n)
                        combined_n_grams = [" ".join(n_gram) for n_gram in n_grams]

                        output[row["URL"]][f"{n}-grams"] = combined_n_grams

                        self.master_ngrams[f"{n}-grams"] |= set(combined_n_grams)

                index_offset += _id

                csv_content_file.close()
                
        for url in output:
            for n in range(1, self.n + 1):
                vector = []
                for n_gram in self.master_ngrams[f'{n}-grams']:
                    if n_gram in output[url][f'{n}-grams']:
                        vector.append(1)
                    else:
                        vector.append(0)
                        
                output[url][f'{n}-grams-vector'] = vector

        with open("ngrams.json", "w+") as output_file:
            json.dump(output, output_file, indent=4)
            output_file.close()


class NGramComparator:
    def __init__(self, url, depth) -> None:
        self.url = url
        self.depth = depth

    def clear_content(self, content):
        cleared_content = re.findall(r"[a-zA-Z]+", content)
        return [word.lower() for word in cleared_content]

    def fetch_data(self):
        crawler = Crawler(self.url, self.depth, "lab3/source/source")
        crawler.run()

        abs_path = path.abspath(getcwd())
        content_path = path.join(abs_path, "lab3/source")

        # Get all the source dirs
        results_dirs = [path.join(content_path, d) for d in listdir(content_path)]
        self.source_dir = max(results_dirs, key=path.getmtime)
        self.layers_dirs = sorted([d for d in listdir(self.source_dir)])

    def create_ngrams(self):
        ngram_generator = NGramGenerator(self.source_dir, 2)
        source_ngrams = ngram_generator.run(save_file=False)
        return source_ngrams

    def run(self):
        # Save the url data to compare
        self.fetch_data()
        source_ngrams = self.create_ngrams()

        # source_words = set()

        # for file_index, layer_dir in enumerate(self.layers_dirs):
        #     with open(
        #         path.join(self.source_dir, layer_dir, f"content{file_index}.csv"),
        #         mode="r",
        #     ) as csv_content_file:
        #         content_reader = csv.DictReader(csv_content_file, delimiter="|")

        #         for row in content_reader:
        #             source_words |= set(self.clear_content(row['Content']))

        with open("ngrams.json", mode="r") as ngrams_file:
            data = json.load(ngrams_file)
            for i in range(1, 3):
                for key in data:
                    vector = []
                    for n_gram in data[key][f"{i}-grams"]:
                        if n_gram in source_ngrams[self.url][f"{i}-grams"]:
                            vector.append(1)
                        else:
                            vector.append(0)

                    data[key]["1-grams-vector"] = vector

            ngrams_file.close()

        print(data["https://en.wikipedia.org/wiki/Mazda_MX-5"]["1-grams-vector"])
