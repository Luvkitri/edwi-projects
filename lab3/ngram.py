import csv
import re
import json
import numpy as np
import requests

from os import getcwd, path, listdir

from lab1.crawler import Crawler


class NGramGenerator:
    def __init__(
        self, source_dir: str, n: int, output_file_name: str, vectorize=True
    ) -> None:
        self.source_dir = source_dir
        self.layers_dirs = sorted([d for d in listdir(source_dir)])
        self.n = n
        self.master_ngrams = {f"{self.n}-grams": set()}
        self.output_file_name = output_file_name
        self.vectorize = vectorize

    def clear_content(self, content):
        cleared_content = re.findall(r"[a-zA-Z]+", content)
        return [word.lower() for word in cleared_content]

    def split_to_ngrams(self, content):
        n_grams = dict()

        for i in range((len(content) - self.n + 1)):
            n_gram = tuple(content[i : i + self.n])
            if n_gram in n_grams:
                n_grams[n_gram] += 1
            else:
                n_grams[n_gram] = 1

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

                    n_grams = self.split_to_ngrams(content)
                    output[row["URL"]][f"{self.n}-grams"] = dict(
                        [(" ".join(n_gram), count) for n_gram, count in n_grams.items()]
                    )

                    if self.vectorize:
                        self.master_ngrams[f"{self.n}-grams"].update(
                            output[row["URL"]][f"{self.n}-grams"].keys()
                        )

                index_offset += _id

        if self.vectorize:
            for url in output:
                vector = []
                for n_gram in self.master_ngrams[f"{self.n}-grams"]:
                    if n_gram in output[url][f"{self.n}-grams"]:
                        vector.append(output[url][f"{self.n}-grams"][n_gram])
                    else:
                        vector.append(0)

                output[url][f"{self.n}-grams-vector"] = vector

        with open(f"{self.output_file_name}.json", "w+") as output_file:
            json.dump(output, output_file, indent=4)

        if self.vectorize:
            with open(f"master-{self.n}-grams.json", "w+") as master_ngrams_file:
                self.master_ngrams[f"{self.n}-grams"] = list(
                    self.master_ngrams[f"{self.n}-grams"]
                )

                json.dump(self.master_ngrams, master_ngrams_file, indent=4)


class NGramComparator:
    def __init__(
        self,
        url,
        depth,
        n: int,
        source_file_name: str,
        master_ngrams=None,
    ) -> None:
        self.url = url
        self.depth = depth
        self.master_ngrams = master_ngrams
        self.n = n
        self.output_file_name = f"{self.n}-grams-comparator"
        self.source_file_name = source_file_name
        self.master_ngrams = {"1-grams": set(), "2-grams": set(), "3-grams": set()}
        self.jacard_distances = {
            f"{self.n}-grams": dict(),
        }
        self.cos_distances = {
            f"{self.n}-grams": dict(),
        }

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

    def create_ngrams(self):
        ngram_generator = NGramGenerator(
            self.source_dir, self.n, self.output_file_name, False
        )
        ngram_generator.run()

    def jacard_distance(self, first_set, second_set):
        return float(
            len(first_set.intersection(second_set)) / len(first_set.union(second_set))
        )

    def cos_distance(self, first_vector, second_vector):
        if len(first_vector) != len(second_vector):
            return 0

        a = np.array(first_vector)
        b = np.array(second_vector)
        return np.dot(a, b) / ((np.dot(a, a) ** 0.5) * (np.dot(b, b) ** 0.5))

    def top_jacard(self, top: int):
        for index, (key, value) in enumerate(
            self.jacard_distances[f"{self.n}-grams"].items()
        ):
            if index == top:
                return

            print(f"{key} - {value}")

    def top_cos(self, top: int):
        for index, (key, value) in enumerate(
            self.cos_distances[f"{self.n}-grams"].items()
        ):
            if index == top:
                return

            print(f"{key} - {value}")

    def get_master_ngrams(self):
        with open(f"{self.source_file_name}.json", mode="r") as ngrams_file:
            source = json.load(ngrams_file)

            for key in source:
                self.master_ngrams[f"{self.n}-grams"].update(
                    source[key][f"{self.n}-grams"]
                )

            ngrams_file.close()

    def get_master_ngrams_from_file(self):
        with open(f"master-{self.n}-grams.json", mode="r") as ngrams_file:
            source = json.load(ngrams_file)
            self.master_ngrams = source[f"{self.n}-grams"]

    def read_master_ngrams(self):
        with open(f"{self.source_file_name}.json", mode="r") as ngrams_file:
            self.master_ngrams = json.load(ngrams_file)
            ngrams_file.close()

    def run(self):
        # Save the url data to compare
        print("Fetching source data")
        self.fetch_data()
        print("Creating ngrams")
        self.create_ngrams()
        print("Retrieving master ngrams")
        self.get_master_ngrams_from_file()

        with open(f"{self.output_file_name}.json", mode="r") as ngrams_file:
            data = json.load(ngrams_file)
            for key in data:
                vector = []
                for n_gram in self.master_ngrams:
                    if n_gram in data[key][f"{self.n}-grams"]:
                        vector.append(data[key][f"{self.n}-grams"][n_gram])
                    else:
                        vector.append(0)

                    data[key][f"{self.n}-grams-vector"] = vector

        with open(f"{self.source_file_name}.json", mode="r") as source_ngrams_file:
            source = json.load(source_ngrams_file)

            for url in source:
                source_ngram = source[url][f"{self.n}-grams"]
                source_vector = source[url][f"{self.n}-grams-vector"]
                input_ngram = data[self.url][f"{self.n}-grams"]
                input_vector = data[self.url][f"{self.n}-grams-vector"]

                self.jacard_distances[f"{self.n}-grams"][url] = self.jacard_distance(
                    set(source_ngram), set(input_ngram)
                )
                self.cos_distances[f"{self.n}-grams"][url] = self.cos_distance(
                    source_vector, input_vector
                )

            source_ngrams_file.close()

            self.jacard_distances[f"{self.n}-grams"] = dict(
                sorted(
                    self.jacard_distances[f"{self.n}-grams"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            )
            self.cos_distances[f"{self.n}-grams"] = dict(
                sorted(
                    self.cos_distances[f"{self.n}-grams"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            )

        with open(f"{self.n}-jacard_distance.json", mode="w+") as jacard_file:
            json.dump(self.jacard_distances, jacard_file, indent=4)
            jacard_file.close()

        with open(f"{self.n}-cos_distance.json", mode="w+") as cos_file:
            json.dump(self.cos_distances, cos_file, indent=4)
            cos_file.close()
