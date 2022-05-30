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
        self.master_ngrams = {"1-grams": set(), "2-grams": set(), "3-grams": set()}
        self.output_file_name = output_file_name
        self.vectorize = vectorize

    def clear_content(self, content):
        cleared_content = re.findall(r"[a-zA-Z]+", content)
        return [word.lower() for word in cleared_content]

    def split_to_ngrams(self, content, n):
        n_grams = set()

        for i in range((len(content) - n + 1)):
            n_grams.add(tuple(content[i : i + n]))

        return n_grams

    def vectorize_ngrams(self):
        pass

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

                        if self.vectorize:
                            self.master_ngrams[f"{n}-grams"].update(combined_n_grams)

                index_offset += _id

                csv_content_file.close()

        if self.vectorize:
            for url in output:
                for i in range(1, self.n + 1):
                    vector = []
                    for n_gram in self.master_ngrams[f"{i}-grams"]:
                        if n_gram in output[url][f"{i}-grams"]:
                            vector.append(1)
                        else:
                            vector.append(0)

                    output[url][f"{i}-grams-vector"] = vector

        with open(f"{self.output_file_name}.json", "w+") as output_file:
            json.dump(output, output_file, indent=4)
            output_file.close()

        if self.vectorize:
            with open(f"master-ngrams.json", "w+") as master_ngrams_file:
                for i in range(1, self.n + 1):
                    self.master_ngrams[f"{n}-grams"] = list(
                        self.master_ngrams[f"{n}-grams"]
                    )
                json.dump(self.master_ngrams, master_ngrams_file, indent=4)
                master_ngrams_file.close()


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
        self.output_file_name = "ngrams-comparator"
        self.source_file_name = source_file_name
        self.n = n
        self.master_ngrams = {"1-grams": set(), "2-grams": set(), "3-grams": set()}
        self.jacard_distances = {
            "1-grams": dict(),
            "2-grams": dict(),
            "3-grams": dict(),
        }
        self.cos_distances = {"1-grams": dict(), "2-grams": dict(), "3-grams": dict()}

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
            self.source_dir, 2, self.output_file_name, False
        )
        ngram_generator.run()

    def jacard_distance(self, first_set, second_set):
        return float(
            len(first_set.intersection(second_set)) / len(first_set.union(second_set))
        )

    def cos_distance(self, first_vector, second_vector):
        a = np.array(first_vector)
        b = np.array(second_vector)
        return np.dot(a, b) / ((np.dot(a, a) ** 0.5) * (np.dot(b, b) ** 0.5))

    def top_jacard(self, top: int):
        for i in range(1, self.n + 1):
            for index, (key, value) in enumerate(
                self.jacard_distances[f"{i}-grams"].items()
            ):
                if index == top:
                    return

                print(f"{key} - {value}")

    def top_cos(self, top: int):
        for i in range(1, self.n + 1):
            for index, (key, value) in enumerate(
                self.cos_distances[f"{i}-grams"].items()
            ):
                if index == top:
                    return
                
                print(f"{key} - {value}")

    def get_master_ngrams(self):
        with open(f"{self.source_file_name}.json", mode="r") as ngrams_file:
            source = json.load(ngrams_file)

            for key in source:
                for i in range(1, self.n + 1):
                    self.master_ngrams[f"{i}-grams"].update(source[key][f"{i}-grams"])

            ngrams_file.close()

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
        self.get_master_ngrams()

        with open(f"{self.output_file_name}.json", mode="r") as ngrams_file:
            data = json.load(ngrams_file)
            for key in data:
                for i in range(1, self.n + 1):
                    vector = []
                    for n_gram in self.master_ngrams[f"{i}-grams"]:
                        if n_gram in data[key][f"{i}-grams"]:
                            vector.append(1)
                        else:
                            vector.append(0)

                    data[key][f"{i}-grams-vector"] = vector

            ngrams_file.close()

        with open(f"{self.source_file_name}.json", mode="r") as source_ngrams_file:
            source = json.load(source_ngrams_file)

            for url in source:
                for i in range(1, self.n + 1):
                    source_ngram = source[url][f"{i}-grams"]
                    source_vector = source[url][f"{i}-grams-vector"]
                    input_ngram = data[self.url][f"{i}-grams"]
                    input_vector = data[self.url][f"{i}-grams-vector"]

                    self.jacard_distances[f"{i}-grams"][url] = self.jacard_distance(
                        set(source_ngram), set(input_ngram)
                    )
                    self.cos_distances[f"{i}-grams"][url] = self.cos_distance(
                        source_vector, input_vector
                    )

            source_ngrams_file.close()

        for i in range(1, self.n + 1):
            self.jacard_distances[f"{i}-grams"] = dict(
                sorted(
                    self.jacard_distances[f"{i}-grams"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            )
            self.cos_distances[f"{i}-grams"] = dict(
                sorted(
                    self.cos_distances[f"{i}-grams"].items(),
                    key=lambda x: x[1],
                    reverse=True,
                )
            )

        with open("jacard_distance.json", mode="w+") as jacard_file:
            json.dump(self.jacard_distances, jacard_file, indent=4)
            jacard_file.close()

        with open("cos_distance.json", mode="w+") as cos_file:
            json.dump(self.cos_distances, cos_file, indent=4)
            cos_file.close()
