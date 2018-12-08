from datetime import datetime


def retry(func: callable, retry_times: int, *args, **kwargs) -> "Any":
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
