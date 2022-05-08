import csv

from os import path, listdir


class Indexer:
    def __init__(self, source_dir: str) -> None:
        self.layers_dirs = [d for d in listdir(source_dir) if path.isdir(d)]

    def run(self):
        for index, layer_dir in enumerate(self.layers_dirs):
            with open(
                path.join(layer_dir, f"content{index}"), mode="r"
            ) as csv_content_file:
                content_reader = csv.DictReader(csv_content_file)

                for row in content_reader:
                    print(row["index"], row["URL"], row["Content"])
