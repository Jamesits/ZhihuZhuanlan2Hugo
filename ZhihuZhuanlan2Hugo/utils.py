import os
import typing
from datetime import datetime

import requests

user_agent = "ZhihuZhuanlan2Hugo.py (+https://github.com/Jamesits/ZhihuZhuanlan2Hugo"


def retry(func: callable, retry_times: int, *args, **kwargs) -> typing.Any:
    count = retry_times
    ex = None
    while count > 0:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ex = e
            count -= 1
    raise ex


def convert_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).isoformat()


def download_file(url: str, dst: str) -> str:
    filename = url.split("/")[-1]
    r = requests.get(url, headers={
        'User-Agent': user_agent,
    }, stream=True)
    if r.status_code == 200:
        with open(os.path.join(dst, filename), 'wb') as f:
            for chunk in r:
                f.write(chunk)
    return filename


def save_file(content: str, path: str) -> None:
    with open(path, mode="w", encoding="utf8") as f:
        f.write(content)
