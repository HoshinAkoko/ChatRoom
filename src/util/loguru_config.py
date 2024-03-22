"""
loguru 配置类
"""


from loguru import logger
import sys


def custom_console_format(record):
    # 处理line，固定占4格，右对齐
    record["extra"]["line"] = f"{record['line']:>4}"

    # 处理name，对齐到4的整数倍，右对齐
    name = record["name"]
    short_name = name.split('.')[-1] if '.' in name else name
    name_length = len(short_name) + (4 - len(short_name) % 4) % 4

    # 处理function，对齐到4的整数倍，右对齐
    function = record["function"]
    function_length = len(function) + (4 - len(function) % 4) % 4

    if len(short_name) > 4 and len(function) > 12:
        name_length = 8 if name_length < 8 else name_length
        function_length = 16 if function_length < 16 else function_length
    elif len(short_name) <= 4 and len(function) > 16:
        name_length = 4 if name_length < 4 else name_length
        function_length = 20 if function_length < 20 else function_length
    elif len(short_name) > 8 and len(function) <= 12:
        name_length = 12 if name_length < 12 else name_length
        function_length = 12 if function_length < 12 else function_length

    record["extra"]["name"] = f"{short_name: >{name_length}}"
    record["extra"]["function"] = f"{function: >{function_length}}"

    # 转义message中的大括号
    # 将单个大括号替换为双大括号，以避免被视为格式化标记
    record["message"] = record["message"].replace("{", "{{").replace("}", "}}")

    # 定义自定义的日志格式
    custom_format = (
        "<magenta>{time:YYYY-MM-DD HH:mm:ss}</magenta> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[name]}</cyan>: <cyan>{extra[function]}</cyan>:<cyan>{extra[line]}</cyan> - <level>{message}</level>\n"
    )
    return custom_format.format(**record)


def setup_logger(log_title):

    file_format = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"

    logger.remove()

    logger.add(
        "/mnt/logs/ChatRoom/" + log_title + "-{time:YYYY-MM-DD}.log",  # 日志文件名格式
        level="INFO",
        rotation="1 day",  # 每天轮转
        retention="100 days",  # 保留100天的日志文件
        compression="zip",
        format=file_format  # 自定义日志格式
    )

    logger.add(
        sys.stdout,
        level="DEBUG",
        format=custom_console_format
    )

