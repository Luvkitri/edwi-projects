import csv
import re
import json
import sys

from os import path, listdir

csv.field_size_limit(sys.maxsize)


class Indexer:
    def __init__(self, source_dir: str) -> None:
        self.source_dir = source_dir
        self.layers_dirs = sorted([d for d in listdir(source_dir)])

    def clear_content(self, content):
        cleared_content = re.findall(r"[a-zA-Z]+", content)
        return [word.lower() for word in cleared_content]

    def run(self):
        output = {}
        output["urls"] = {}
        output["invertedIndex"] = {}

        index_offset = 0

        for file_index, layer_dir in enumerate(self.layers_dirs):
            with open(
                path.join(self.source_dir, layer_dir, f"content{file_index}.csv"),
                mode="r",
            ) as csv_content_file:
                content_reader = csv.DictReader(csv_content_file, delimiter="|")

                for row in content_reader:
                    url_index = int(row["index"])
                    output["urls"][url_index + index_offset] = row["URL"]
                    content_words = self.clear_content(row["Content"])

                    # Without word location only count
                    # for word in content_words:
                    #     if word in output["inverted_index"]:
                    #         if url_index in output["inverted_index"][word]:
                    #             output["inverted_index"][word][url_index] += 1
                    #         else:
                    #             output["inverted_index"][word][url_index] = 1
                    #     else:
                    #         output["inverted_index"][word] = {}
                    #         output["inverted_index"][word][url_index] = 1

                    # Word position versions
                    for index, word in enumerate(content_words):
                        if word in output["invertedIndex"]:
                            if url_index in output["invertedIndex"][word]:
                                output["invertedIndex"][word][url_index].append(index)
                            else:
                                output["invertedIndex"][word][url_index] = [index]
                        else:
                            output["invertedIndex"][word] = {}
                            output["invertedIndex"][word][url_index] = [index]

                index_offset += url_index

        with open("invertedIndex.json", "w+") as output_file:
            json.dump(output, output_file, indent=4)
