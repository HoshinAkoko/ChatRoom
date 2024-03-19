from loguru import logger
import sys

def setup_logger(log_title):

    file_format = "{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}"

    console_format = (
        "<green>{time:YYYY-MM-DD at HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

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
        format=console_format
    )

