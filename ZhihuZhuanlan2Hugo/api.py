from ZhihuZhuanlan2Hugo.utils import *


def get_column_metadata(slug: str) -> typing.Dict:
    r = retry(requests.get, 3, "https://zhuanlan.zhihu.com/api/columns/%s" % slug, headers={
        'User-Agent': user_agent,
    })
    return r.json()


def get_column_article_list(slug: str, limit: int, offset: int) -> typing.Dict:
    r = retry(requests.get, 3, "https://zhuanlan.zhihu.com/api/columns/%s/articles" % slug, headers={
        'User-Agent': user_agent,
    }, params={
        # "include": "data%5B%2A%5D.admin_closed_comment%2Ccomment_count%2Csuggest_edit%2Cis_title_image_full_screen%2Ccan_comment%2Cupvoted_followees%2Ccan_open_tipjar%2Ccan_tip%2Cvoteup_count%2Cvoting%2Ctopics%2Creview_info%2Cauthor.is_following%2Cis_labeled%2Clabel_info",
        "limit": limit,
        "offset": offset,
    })
    return r.json()


def get_article(id: int) -> typing.Dict:
    r = retry(requests.get, 3, "https://zhuanlan.zhihu.com/api/posts/%d" % id, headers={
        'User-Agent': user_agent,
    })
    return r.json()


def articles(slug: str) -> (typing.Dict, typing.Dict):
    """
    An iterator to get all articles.
    :param slug: column slug
    :return: (article_metadata, article_content), all is dict
    """
    start = 0
    limit = 10
    while True:
        article_list = get_column_article_list(slug, limit, start)
        for article in article_list["data"]:
            yield article, get_article(int(article["id"]))
        if article_list["paging"]["is_end"]:
            break
        start += limit
