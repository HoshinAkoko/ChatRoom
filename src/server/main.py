"""
服务端
"""
import socket
import threading
import configparser
import re
import service
from src.util import util, loguru_config as log_conf, constant
from loguru import logger as log


# 全局变量
client_list = []                        # 客户端列表
user_dict = {}                          # 客户信息 key, nickname, uid
exit_event = threading.Event()          # 退出事件
# 默认配置
host = "0.0.0.0"                        # 服务端ip
port = 9999                             # 服务端端口
max_client = 3                          # 每轮监听等待时间
common_key = "0123456789ABCDEF"         # 默认消息密钥
sign_key = "OPSTART"                    # 验签密钥


# 主业务
def main_service(params_json, addr, user):
    params_dict = util.verify_to_dict(params_json, sign_key)
    if not params_dict:
        log.warning(f"客户端{addr}验签失败！")
        return error_msg("验签失败！")
    if params_dict["type"] != constant.CLIENT_MSG_TYPE_LOGIN_IN and user is None:
        log.warning(f"客户端{addr}非法请求，需要先登录。")
        return error_msg("非法请求！请先登录。")
    if params_dict["type"] == constant.CLIENT_MSG_TYPE_LOGIN_IN:
        if user is not None:
            log.warning(f"客户端{addr}已登录，接收到重复的登录请求。")
            return error_msg("您已登录。如果要切换用户，请先登出。")
        service.login(params_dict, addr, user_dict)




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
            receive = util.aes_decrypt(receive, user_dict[addr].key if user_dict[addr].key is not None else common_key)
            log.info(f"接受客户端{addr}的信息：{receive}")
            # 业务处理
            respond_dict = main_service(receive, addr, user_dict[addr])
            respond_dict["timestamp"] = util.get_timestamp
            respond = util.sign_to_json(respond_dict, sign_key)
            respond = util.aes_encrypt(respond, user_dict[addr].key if user_dict[addr].key is not None else common_key)
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
            log.error(e)
            raise e
        finally:
            if exit_event.is_set():
                break
    # 关闭连接
    client_socket.close()
    log.info(f"连接已关闭: {addr}")
    client_list.remove(client_socket)
    log.info(f"当前连接数：{len(client_list)}")


# 启动服务器
def start_server():
    # 创建 socket 对象
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.settimeout(3.0)
    server_socket.bind((host, port))
    server_socket.listen(max_client)
    log.info(f"ChatRoom服务端启动于{host}:{port}...")
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
            shutdown()
            server_socket.close()
            log.warning(f"Socket服务端已关闭")
            log.error(e)
            raise e
        finally:
            if exit_event.is_set():
                break
    server_socket.close()
    log.warning(f"Socket服务端已关闭")


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
        if re.match(r'^(exit|eixt|exti|shutdown|shudtown|shutdwon).*', new_command, re.IGNORECASE):
            shutdown()  # 通知线程停止
            log.info(f"等待线程退出...")
            break
        else:
            pass


# 关闭服务端
def shutdown():
    exit_event.set()


# 读取配置
def config_init():
    # 加载配置文件
    config = configparser.ConfigParser()
    config.read('server_config.ini')
    if __name__ == "__main__":
        config.read('../../server_config.ini')
    global client_list, key_dict, common_key, sign_key, host, port, max_client

    def get_config(section, option, default_value, is_int=False):
        try:
            value = config[section][option]
            if value is None and default_value is None and is_int:
                return 0
            if value is None and default_value is None and not is_int:
                return None
            if value is None and default_value is not None:
                value = default_value
            if is_int:
                return int(value)
            return value
        except KeyError or TypeError:
            try:
                if is_int:
                    return int(default_value)
                return default_value
            except ValueError:
                return 0

    host            = get_config('server', 'host', default_value=host)
    port            = get_config('server', 'port', default_value=port, is_int=True)
    max_client      = get_config('server', 'max_client', default_value=max_client, is_int=True)
    common_key      = get_config('server', 'common_key', default_value=common_key)
    sign_key        = get_config('server', 'sign_key', default_value=sign_key)


# 测试
if __name__ == "__main__":
    main()
    # log_conf.setup_logger("server")
    # log.info("test_log")