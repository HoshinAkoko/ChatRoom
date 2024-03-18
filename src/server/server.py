"""
服务端
"""
import socket
import threading
from src.util import util, loguru_config as log_conf
from loguru import logger as log

default_key = "0123456789ABCDEF"
sign_key = "OPSTART"

# 主业务
def main_service(params_json, addr):
    params_dict = util.verify_to_dict(params_json, sign_key)
    if not params_dict:
        log.warning(f"用户{addr}验签失败！")
        return error_msg("验签失败！")


# 返回单条错误信息
def error_msg(msg):
    error_dict = {
        "type": -1,
        "params": {
            "code": -1,
            "msg": f"{msg}"
        }
    }
    return error_dict


# 处理每个客户端连接
def handle_client(stop_event, client_socket, addr):
    log.info(f"新连接: {addr}")
    log.info(f"当前连接数：{len(client_list)}")
    client_socket.settimeout(3.0)
    while True:
        # 接受数据，若空则关闭
        try:
            receive = client_socket.recv(1024)
            if not receive:
                break
            receive = receive.decode('utf-8')
            receive = util.aes_decrypt(receive, key_dict.get(addr) if key_dict.get(addr) is not None else default_key)
            log.info(f"接受用户{addr}的信息：{receive}")
            # 业务处理
            respond_dict = main_service(receive, addr)
            respond_dict["timestamp"] = util.get_timestamp
            respond = util.sign_to_json(respond_dict, sign_key)
            respond = util.aes_encrypt(respond, key_dict.get(addr) if key_dict.get(addr) is not None else default_key)
            respond.encode('utf-8')
            client_socket.send(respond)
        except socket.timeout:
            pass
        except ConnectionResetError:
            log.warning(f"用户中断连接！连接{addr}强制关闭...")
            break
        except Exception as e:
            log.error(f"未知异常！连接{addr}强制关闭...")
            client_list.remove(client_socket)
            log.info(f"当前连接数：{len(client_list)}")
            client_socket.close()
            raise e
        finally:
            if stop_event.is_set():
                break
    # 关闭连接
    client_socket.close()
    log.info(f"连接已关闭: {addr}")
    client_list.remove(client_socket)
    log.info(f"当前连接数：{len(client_list)}")


# 启动服务器
def start_server(stop_event, host, port, max_listen):
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(3.0)
    server_socket.bind((host, port))
    server_socket.listen(max_listen)
    log.info(f"ChatRoom服务端启动于{host}:{port}...")
    while True:
        try:
            # 等待一个新连接
            client_socket, addr = server_socket.accept()
            # 为这个连接创建一个新的线程
            client_thread = threading.Thread(target=handle_client, args=(stop_event, client_socket, addr))
            client_list.append(client_socket)
            client_thread.start()
        except socket.timeout:
            pass
        except Exception as e:
            log.critical(f"未知异常！服务端强制关闭...")
            stop_event.set()
            server_socket.close()
            log.warning(f"Socket服务端已关闭")
            raise e
        finally:
            if stop_event.is_set():
                break
    server_socket.close()
    log.warning(f"Socket服务端已关闭")


if __name__ == "__main__":
    log_conf.setup_logger("server")
    print("\r====================== CHAT ROOM ======================")
    HOST = "0.0.0.0"
    PORT = 8919
    # 停止时间
    exit_event = threading.Event()
    server_thread = threading.Thread(target=start_server, args=(exit_event, HOST, PORT, 5))
    client_list = []
    key_dict = {}
    server_thread.start()
    while True:
        new_command = input()
        if "exit".upper() == new_command.upper():
            exit_event.set()  # 通知线程停止
            log.info(f"等待线程退出...")
            break
        else:
            pass
