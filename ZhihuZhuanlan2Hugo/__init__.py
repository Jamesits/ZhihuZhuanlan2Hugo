import json
import logging
from distutils.dir_util import copy_tree

import yaml

from ZhihuZhuanlan2Hugo import api
from ZhihuZhuanlan2Hugo.markdownify import markdownify
from ZhihuZhuanlan2Hugo.utils import *

logging.basicConfig(format='%(asctime)-15s|%(name)s|%(levelname)-6s: %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def generate_markdown(path: str, front_matter: object, content: str = "") -> None:
    with open(path, mode="w", encoding="utf8") as f:
        f.write("---\n")
        f.write(yaml.dump(front_matter, allow_unicode=True, default_flow_style=False))
        f.write("---\n\n")
        f.write(content)
        f.write("\n")


def convert(column: str, destination_folder_path: str) -> None:
    """
    Convert a column to a content folder.
    :param column: column slug
    :param destination_folder_path: path to a folder (assume the destination folder exists)
    :return: None
    """
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

    # get individual articles
    for article_metadata, article in api.articles(column):
        pid = article["id"]
        logger.info("Downloading article #%d %s - %s", pid, article["title"], article["author"]["name"])
        article_base_dir = os.path.join(destination_folder_path, str(pid))
        os.makedirs(article_base_dir, exist_ok=True)
        # save a copy of the original response
        save_file(json.dumps(article_metadata, ensure_ascii=False),
                  os.path.join(article_base_dir, "article_metadata.json"))
        save_file(json.dumps(article, ensure_ascii=False), os.path.join(article_base_dir, "article.json"))
        # save the transformed document
        generate_markdown(os.path.join(article_base_dir, "index.md"), {
            # official
            "title": article["title"],
            "author": article["author"]["name"],
            "isCJKLanguage": True,
            "date": convert_time(article["created"]),
            "lastmod": convert_time(article["updated"]),
            "tags": [x["name"] for x in article["topics"]],

            # custom
            "origin_url": article["url"],
        }, markdownify(article["content"], os.path.join(destination_folder_path, str(pid))))


def main(*args) -> None:
    if len(args) < 2:
        logger.fatal("Too few arguments")

    src_list = args[1:-1]
    src_template = "./site_template"
    dst_base = args[-1]

    # generate site skeleton
    logger.info("Copying site template...")
    copy_tree(src_template, dst_base)
    # download files
    for col in src_list:
        dst_dir = os.path.join(dst_base, "content", col)
        os.makedirs(dst_dir, exist_ok=True)
        convert(col, dst_dir)
