"""
时间类工具
"""


from datetime import datetime


def date_int_to_str(date_int):
    date_format = '%Y-%m-%d %H:%M:%S'
    dt = datetime.fromtimestamp(date_int)
    return dt.strftime(date_format)