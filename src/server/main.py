"""
服务端
"""
import socket
import threading
import configparser
import re
from src.server import service, database
from src.server.service import error_msg
from src.util import util, loguru_config as log_conf, constant
from loguru import logger as log
from pathlib import Path


# 全局变量
client_list = []                        # 客户端列表
user_dict = {}                          # 客户信息 key, nickname, uid
exit_event = threading.Event()          # 退出事件
# 默认配置
host = "0.0.0.0"                        # 服务端ip
port = 9999                             # 服务端端口
max_client = 3                          # 每轮监听等待时间
common_key = "0123456789ABCDEF0123456789ABCDEF"         # 默认消息密钥
sign_key = "OPSTART"                    # 验签密钥


# 主业务
def main_service(request_json, addr, user):
    request_dict = util.verify_to_dict(request_json, sign_key)
    if not request_dict:
        log.warning(f"客户端 {addr} 验签失败！")
        return error_msg("验签失败！")
    if "params" not in request_dict or "type" not in request_dict:
        return error_msg("参数错误！")
    if request_dict["type"] != constant.CLIENT_MSG_TYPE_LOGIN_IN and user is None:
        log.warning(f"客户端 {addr} 非法请求，需要先登录。")
        return error_msg("非法请求！请先登录。")
    if request_dict["type"] == constant.CLIENT_MSG_TYPE_LOGIN_IN:
        if user is not None:
            log.warning(f"客户端 {addr} 已登录，接收到重复的登录请求。")
            return error_msg("您已登录。如果要切换用户，请先登出。")
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
            return error_msg("未知请求！")


# 处理每个客户端连接
def handle_client(client_socket, addr):
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
            user = None
            aes_key = common_key
            if addr in user_dict:
                user = user_dict[addr]
                if user.key is not None:
                    aes_key = user_dict[addr].key
            receive = util.aes_decrypt(receive, aes_key)
            log.debug(f"接收客户端: {addr} ：{receive}")
            # 业务处理
            respond_dict = main_service(receive, addr, user)
            if respond_dict is None:
                respond_dict = error_msg(f"未知错误！")
            respond_dict["timestamp"] = util.get_timestamp()
            respond = util.sign_to_json(respond_dict, sign_key)
            log.debug(f"服务端发送：{respond}")
            respond = util.aes_encrypt(respond, aes_key)
            respond = respond.encode('utf-8')
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
            log.error(e)
            raise e
        finally:
            if exit_event.is_set():
                break
    # 关闭连接
    client_socket.close()
    log.info(f"连接已关闭: {addr}")
    client_list.remove(client_socket)
    user_dict.pop(addr)
    log.info(f"当前连接数：{len(client_list)}")


# 启动服务器
def start_server():
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(3.0)
    server_socket.bind((host, port))
    server_socket.listen(max_client)
    log.info(f"ChatRoom 服务端启动于{host}:{port}...")
    while True:
        try:
            # 等待一个新连接
            client_socket, addr = server_socket.accept()
            # 为这个连接创建一个新的线程
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_list.append(client_socket)
            client_thread.start()
        except socket.timeout:
            pass
        except Exception as e:
            log.critical(f"未知异常！服务端强制关闭...")
            shutdown(press_enter=True)
            server_socket.close()
            log.warning(f"ChatRoom 服务端已关闭")
            log.error(e)
            raise e
        finally:
            if exit_event.is_set():
                break
    server_socket.close()
    log.warning(f"ChatRoom 服务端已关闭")


# 入口
def main():
    # 服务器启动
    config_init()
    log_conf.setup_logger("server")
    print(f"\r{constant.get_logo(constant.SERVER_TITLE, constant.SERVER_SUBTITLE, constant.SERVER_VERSION)}", end="")
    server_thread = threading.Thread(target=start_server, args=())
    server_thread.start()
    # 等待接收指令
    while True:
        new_command = input()
        if exit_event.is_set():
            break
        if re.match(r'^(exit|eixt|exti|shutdown|shudtown|shutdwon)( .*|)', new_command, re.IGNORECASE):
            shutdown()  # 通知线程停止
            log.info(f"指令手动关停，请等待线程退出...")
            break
        else:
            pass


# 关闭服务端
def shutdown(press_enter=False):
    exit_event.set()
    database.disconnect()
    if press_enter:
        print(f"请按回车退出。")


# 读取配置
def config_init():
    # 加载配置文件
    config = configparser.ConfigParser()
    config_file = Path('server_config.ini')
    if not config_file.exists():
        config_file = Path('../../server_config.ini')
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在！")
    config.read(config_file)
    global host, port, max_client, common_key, sign_key

    host            = util.get_config(config, 'server', 'host', default_value=host)
    port            = util.get_config(config, 'server', 'port', default_value=port, is_int=True)
    max_client      = util.get_config(config, 'server', 'max_client', default_value=max_client, is_int=True)
    common_key      = util.get_config(config, 'server', 'common_key', default_value=common_key)
    sign_key        = util.get_config(config, 'server', 'sign_key', default_value=sign_key)


# 测试
if __name__ == "__main__":
    main()
    # log_conf.setup_logger("server")
    # log.info("test_log")