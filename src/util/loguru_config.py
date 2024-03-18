from loguru import logger

def setup_logger(log_title):
    logger.add(
        "/mnt/log/ChatRoom/" + log_title + "-{time:YYYY-MM-DD}.log",  # 日志文件名格式
        rotation="1 day",  # 每天轮转
        retention="10 days",  # 保留10天的日志文件
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} {level} | {message}",  # 自定义日志格式
    )

