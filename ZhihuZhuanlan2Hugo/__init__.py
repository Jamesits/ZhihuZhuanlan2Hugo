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


def convert_column_info(info: typing.Dict, assets_folder: str) -> typing.Dict:
    """
    Convert column info to a dict.
    :param info: a column info dict. Example:
        {
            "updated": 1438759721,
            "description": "",
            "can_manage": false,
            "intro": "",
            "is_following": false,
            "url_token": "computers",
            "id": "computers",
            "articles_count": 61,
            "accept_submission": true,
            "title": "About Computers",
            "url": "https://zhuanlan.zhihu.com/computers",
            "comment_permission": "all",
            "created": 1394632777,
            "image_url": "https://pic2.zhimg.com/008a19032e74677b9dcc1946e520b63f_b.jpg",
            "author": {
                "is_followed": false,
                "name": "James Swineson",
                "headline": "已而！已而！",
                "gender": 1,
                "user_type": "people",
                "url_token": "james-swineson",
                "url": "/people/72036ce918812daac46c75d7cac1e7d2",
                "avatar_url": "https://pic3.zhimg.com/4ad478c148b4e9ccbe312cfa53402b0f_l.jpg",
                "is_following": false,
                "type": "people",
                "id": "72036ce918812daac46c75d7cac1e7d2"
            },
            "followers": 2036,
            "type": "column"
        }
    :param assets_folder: where to download images
    :return: an organized dict
    """
    img = info["image_url"]
    local_img = download_file(img, assets_folder)
    return {
        "title": info["title"],
        "url": info["url"],
        "description": info["description"],
        "image_url": local_img,
    }


def convert_people_info(info: typing.Dict, assets_folder: str) -> typing.Dict:
    """
    Convert user info to a dict.
    :param info: a user info dict. Example:
        {
            "is_followed": false,
            "name": "James Swineson",
            "headline": "已而！已而！",
            "type": "people",
            "user_type": "people",
            "url_token": "james-swineson",
            "url": "/people/72036ce918812daac46c75d7cac1e7d2",
            "avatar_url": "https://pic3.zhimg.com/4ad478c148b4e9ccbe312cfa53402b0f_l.jpg",
            "is_following": false,
            "gender": 1,
            "badge": [],
            "id": "72036ce918812daac46c75d7cac1e7d2"
        }
    :param assets_folder: where to download images
    :return: an organized dict
    """
    img = info["avatar_url"]
    local_img = download_file(img, assets_folder)
    return {
        "name": info["name"],
        "description": info["headline"],
        "id": info["id"],
        "slug": info["url_token"],
        "url": "https://www.zhihu.com" + info["url"],
        "image_url": local_img,
    }


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
        document_meta = {
            # official
            "title": article["title"],
            "author": article["author"]["name"],
            "isCJKLanguage": True,
            "date": convert_time(article["created"]),
            "lastmod": convert_time(article["updated"]),
            "tags": [x["name"] for x in article["topics"]],
            "draft": False if article["state"] == "published" else True,

            # custom
            "origin_url": article["url"],
            "id": article["id"],
            # 作者
            "author_detail": convert_people_info(article["author"], article_base_dir),
            # 赞同数
            "upvotes": article["voteup_count"],
            # 当前专栏信息
            "current_column": convert_column_info(article["column"], article_base_dir),
            # 所有收录专栏信息
            "all_columns": [convert_column_info(x["column"], article_base_dir) for x in article["contributions"]],
        }
        if article["image_url"] != "":
            document_meta["title_image_url"] = download_file(article["image_url"], article_base_dir)
        # save the transformed document
        generate_markdown(os.path.join(article_base_dir, "index.md"), document_meta,
                          markdownify(article["content"], os.path.join(destination_folder_path, str(pid))))


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

    logger.info("Download finished")
