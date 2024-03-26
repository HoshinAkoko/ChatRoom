"""
服务端
"""


import socket
import threading
from src.server import database, message, config, receive
from src.util import constant
from loguru import logger as log


# 启动服务器
def start_server(stop_event, user_dict, client_dict):
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(2.0)
    server_socket.bind((config.host, config.port))
    server_socket.listen(config.max_client)
    log.info(f"{constant.PROJECT_NAME} 服务端启动于 {config.host}:{config.port}...")
    while True:
        try:
            # 等待一个新连接
            client_socket, addr = server_socket.accept()
            client_dict[addr] = client_socket
            # 为这个连接创建一个新的线程
            client_thread = threading.Thread(target=receive.handle_client, args=(addr, stop_event, user_dict, client_dict))
            client_thread.start()
        except socket.timeout:
            pass
        except Exception as e:
            log.critical(f"未知异常！服务端强制关闭...")
            log.error(e)
            shutdown(stop_event, press_enter=True)
            break
        finally:
            message.save_cache_one()
            if stop_event.is_set():
                break
    server_socket.close()
    log.warning(f"{constant.PROJECT_NAME} 服务端已关闭")


# 关闭服务端
def shutdown(exit_event, press_enter=False):
    exit_event.set()
    message.save_cache_all()
    database.disconnect()
    if press_enter:
        print(f"请按回车退出。")