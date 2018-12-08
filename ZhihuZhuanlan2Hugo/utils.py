import os
import typing
from datetime import datetime

import requests

user_agent = "ZhihuZhuanlan2Hugo.py (+https://github.com/Jamesits/ZhihuZhuanlan2Hugo"


def retry(func: callable, retry_times: int, *args, **kwargs) -> typing.Any:
    count = retry_times
    e = None
    while count > 0:
        try:
            return func(*args, **kwargs)
        except Exception as e:
            count -= 1
    raise e


def convert_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp).isoformat()


def download_file(url: str, dst: str) -> None:
    filename = url.split("/")[-1]
    r = requests.get(url, headers={
        'User-Agent': user_agent,
    }, stream=True)
    if r.status_code == 200:
        with open(os.path.join(dst, filename), 'wb') as f:
            for chunk in r:
                f.write(chunk)
    return filename
