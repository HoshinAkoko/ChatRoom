"""
服务端
"""


import socket
import threading

import re
from src.server import service, database, message, config
from src.server.service import response_msg
from src.util import util, loguru_config as log_conf, constant
from loguru import logger as log


# 全局变量
client_dict = dict()                    # 客户端列表
user_dict = dict()                      # 客户信息 key, nickname, uid
exit_event = threading.Event()          # 退出事件


# 主业务
def main_service(request_json, addr, user):
    request_dict = util.verify_to_dict(request_json, config.sign_key)
    if not request_dict:
        log.warning(f"客户端 {addr} 验签失败！")
        return response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"验签失败！", constant.CODE_ERROR)
    if "params" not in request_dict or "type" not in request_dict:
        return response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"参数错误！", constant.CODE_ERROR)
    if request_dict["type"] != constant.CLIENT_MSG_TYPE_LOGIN_IN and user is None:
        log.warning(f"客户端 {addr} 非法请求，需要先登录。")
        return response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, addr, f"非法请求！请先登录。", constant.CODE_ERROR)
    if request_dict["type"] == constant.CLIENT_MSG_TYPE_LOGIN_IN:
        if user is not None:
            log.warning(f"客户端 {addr} 已登录，接收到重复的登录请求。")
            return response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, addr, f"您已登录。如果要切换用户，请先登出。", constant.CODE_ERROR)
        return service.login(request_dict["params"], addr, user_dict)
    match request_dict["type"]:
        case constant.CLIENT_MSG_TYPE_SINGLE_MSG:
            return service.receive_msg(request_dict["params"], addr, user_dict)
        case constant.CLIENT_MSG_TYPE_CHANGE_NICKNAME:
            return service.change_nickname(request_dict["params"], addr, user_dict)
        case constant.CLIENT_MSG_TYPE_CHANGE_SETTING:
            return service.change_setting(request_dict["params"], addr, user_dict)
        case constant.CLIENT_MSG_TYPE_REQUEST_HISTORY:
            return service.request_history(request_dict["params"], addr, user_dict)
        case _:
            return response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"未知请求！", constant.CODE_ERROR)


# 处理每个客户端连接
def handle_client(addr):
    client_socket = client_dict[addr]
    log.info(f"新连接: {addr}")
    log.info(f"当前连接数：{len(client_dict)}")
    client_last_updated_int = util.get_timestamp()
    client_socket.settimeout(3.0)
    service.send_msg(response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, addr, f"连接服务器成功，请登陆！(1分钟后超时)", constant.CODE_NORMAL), addr, client_dict, user_dict)
    while True:
        # 接收数据，若空则关闭
        try:
            # 判断是否未登录且超过 1 分钟未活动
            if addr not in user_dict and util.get_timestamp() - client_last_updated_int > 1 * 60 * 1000:
                service.send_msg(response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"登入超时！", constant.CODE_ERROR), addr, client_dict, user_dict)
                break
            receive = util.socket_recv(client_socket)
            if not receive:
                break
            client_last_updated_int = util.get_timestamp()
            receive = receive.decode('utf-8')
            user = None
            aes_key = config.common_key
            if addr in user_dict:
                user = user_dict[addr]
                if user.key is not None:
                    aes_key = user.key
            receive = util.aes_decrypt(receive, aes_key)
            log.debug(f"接收客户端<-{addr}：{receive}")
            # 业务处理
            respond_dict = main_service(receive, addr, user)
            if respond_dict is not None:
                #respond_dict = response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"未知错误！", constant.CODE_ERROR)
                respond_dict["timestamp"] = util.get_timestamp()
                respond = util.sign_to_json(respond_dict, config.sign_key)
                log.debug(f"服务端发送->{addr}：{respond}")
                respond = util.aes_encrypt(respond, aes_key)
                respond = respond.encode('utf-8')
                util.socket_send(client_socket, respond)
        except socket.timeout:
            pass
        except ConnectionResetError:
            log.warning(f"用户中断连接！连接 {addr} 强制关闭...")
            break
        except Exception as e:
            log.error(f"未知异常！连接 {addr} 强制关闭...")
            log.info(f"当前连接数：{len(client_dict)}")
            client_socket.close()
            log.error(e)
            break
            # raise e
        finally:
            if exit_event.is_set():
                break
    # 关闭连接
    if client_socket is not None:
        client_socket.close()
    log.info(f"连接已关闭: {addr}")
    if addr in client_dict:
        client_dict.pop(addr)
    if addr in user_dict:
        user_dict.pop(addr)
    log.info(f"当前连接数：{len(client_dict)}")


# 启动服务器
def start_server():
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(3.0)
    server_socket.bind((config.host, config.port))
    server_socket.listen(config.max_client)
    log.info(f"{constant.PROJECT_NAME} 服务端启动于 {config.host}:{config.port}...")
    while True:
        try:
            # 等待一个新连接
            client_socket, addr = server_socket.accept()
            client_dict[addr] = client_socket
            # 为这个连接创建一个新的线程
            client_thread = threading.Thread(target=handle_client, args=(addr,))
            client_thread.start()
        except socket.timeout:
            pass
        except Exception as e:
            log.critical(f"未知异常！服务端强制关闭...")
            log.error(e)
            shutdown(press_enter=True)
            break
            # raise e
        finally:
            if exit_event.is_set():
                break
    server_socket.close()
    log.warning(f"{constant.PROJECT_NAME} 服务端已关闭")


# 入口
def main():
    # 服务器启动
    config.config_init()
    log_conf.setup_logger("server")
    print(f"\r{constant.get_logo(constant.SERVER_TITLE, constant.SERVER_SUBTITLE, constant.SERVER_VERSION)}", end="")
    server_thread = threading.Thread(target=start_server, args=())
    server_thread.start()
    # 等待接收指令
    while True:
        new_command = input() #util.get_input()
        if exit_event.is_set():
            break
        if re.match(r'^(exit|eixt|exti|shutdown|shudtown|shutdwon)( .*|)', new_command, re.IGNORECASE):
            log.info(f"终端指令: {new_command}")
            shutdown()  # 通知线程停止
            log.info(f"指令手动关停，请等待线程退出...")
            break
        else:
            pass


# 关闭服务端
def shutdown(press_enter=False):
    exit_event.set()
    database.disconnect()
    message.save_cache()
    if press_enter:
        print(f"请按回车退出。")


# 测试
if __name__ == "__main__":
    main()
    # log_conf.setup_logger("server")
    # log.info("test_log")