"""
服务端主函数
"""


import threading
import re
from src.server import config
from src.server.server import start_server, shutdown
from src.util import loguru_config as log_conf, constant
from loguru import logger as log


# 入口
def main():

    # 加载服务端配置
    config.config_init()

    # 加载日志配置
    log_conf.setup_logger("server")

    # 欢迎语
    print(f"\r{constant.get_logo(constant.SERVER_TITLE, constant.SERVER_SUBTITLE, constant.SERVER_VERSION)}", end="")

    # 初始化参数
    client_dict = dict()  # 客户端列表
    user_dict = dict()  # 客户信息 key, nickname, uid
    exit_event = threading.Event()  # 退出事件

    # 启动服务端
    server_thread = threading.Thread(target=start_server, args=(exit_event, user_dict, client_dict))
    server_thread.start()

    # 等待控制台文本指令
    while True:
        new_command = input() #util.get_input()
        if exit_event.is_set():
            break
        if re.match(r'^(exit|eixt|exti|shutdown|shudtown|shutdwon)( .*|)', new_command, re.IGNORECASE):
            log.info(f"终端指令: {new_command}")
            shutdown(exit_event)  # 通知线程停止
            log.info(f"指令手动关停，请等待线程退出...")
            break
        else:
            pass


# 测试
if __name__ == "__main__":
    main()