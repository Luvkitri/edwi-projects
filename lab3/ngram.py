import csv
import re
import json
import sys

from os import path, listdir


class NGramGenerator:
    def __init__(self, source_dir: str, n: int) -> None:
        self.source_dir = source_dir
        self.layers_dirs = sorted([d for d in listdir(source_dir)])
        self.n = n

    def clear_content(self, content):
        cleared_content = re.findall(r"[a-zA-Z]+", content)
        return [word.lower() for word in cleared_content]

    def split_to_ngrams(self, content):
        n_grams = {}

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
                    output[row["URL"]]["ngrams"] = n_grams

                    for key, value in n_grams.items():
                        output["ngrams"][_id].append(
                            {"ngram": list(key), "count": value}
                        )

                index_offset += _id

        with open(f"ngrams.json", "w+") as output_file:
            json.dump(output, output_file, indent=4)
