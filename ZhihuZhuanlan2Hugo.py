import os
import logging
import yaml
import api
import sys
from datetime import datetime
from markdownify import markdownify
from distutils.dir_util import copy_tree

src_list = sys.argv[1:-1]
src_template = "./site_template"
dst_base = sys.argv[-1]


logging.basicConfig(format='%(asctime)-15s|%(name)s|%(levelname)-6s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def convert_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).isoformat()


def generate_markdown(path: str, front_matter: object, content: str = "")->None:
    with open(path, mode="w", encoding="utf8") as f:
        f.write("---\n")
        f.write(yaml.dump(front_matter, allow_unicode=True, default_flow_style=False))
        f.write("---\n\n")
        f.write(content)
        f.write("\n")


# Convert a column to a content folder. Assume the destination folder exists.
def convert(column: str, destination_folder_path: str) -> None:
    logger.info("Start crawling %s to %s", column, destination_folder_path)

    # get column info
    logger.debug("Getting metadata...")
    j = api.get_column_metadata(column)
    index_metadata = {
        "title": j["title"],
        "description": j["description"],
        "author": j["author"]["name"],
    }
    generate_markdown(os.path.join(destination_folder_path, "_index.md"), index_metadata)

    # get files
    for article in api.articles(column):
        pid = article["id"]
        logger.info("Downloading article #%d %s - %s", pid, article["title"], article["author"]["name"])
        os.makedirs(os.path.join(destination_folder_path, str(pid)), exist_ok=True)
        generate_markdown(os.path.join(destination_folder_path, str(pid), "index.md"), {
            # official
            "title": article["title"],
            "author": article["author"]["name"],
            "isCJKLanguage": True,
            "date": convert_time(article["created"]),
            "lastmod": convert_time(article["updated"]),
            "tags": [x["name"] for x in article["topics"]],

            # custom
            "origin_url": article["url"],
        }, markdownify(article["content"]))


if __name__ == "__main__":
    # generate site skeleton
    logger.info("Copying site template...")
    copy_tree(src_template, dst_base)
    # download files
    for col in src_list:
        dst_dir = os.path.join(dst_base, "content", col)
        os.makedirs(dst_dir, exist_ok=True)
        convert(col, dst_dir)
