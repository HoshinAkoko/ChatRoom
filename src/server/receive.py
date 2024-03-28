"""
接收&分发客户端信息
"""


import socket
import threading
from loguru import logger as log
from src.server import service, config
from src.util import util, constant
from src.server.service import cons_resp_msg


# 处理每个客户端连接
def handle_client(addr, stop_event, user_dict, client_dict):
    client_socket = client_dict[addr]
    log.info(f"新连接: {addr}")
    log.info(f"当前连接数：{len(client_dict)}")
    client_last_updated_int = util.get_timestamp()
    client_socket.settimeout(3.0)
    service.send_msg(cons_resp_msg(f"连接服务器成功，请登陆！(1分钟后超时)", addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_NORMAL), addr, client_dict, user_dict)
    msg_queue = list()
    deal_event = threading.Event()
    while True:
        # 判断是否未登录且超过 1 分钟未活动
        if addr not in user_dict and util.get_timestamp() - client_last_updated_int > 1 * 60 * 1000:
            service.send_msg(cons_resp_msg(f"登入超时！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR), addr, client_dict, user_dict)
            log.warning(f"用户 {addr} 登入超时，连接强制关闭...")
            break

        try:
            receive = util.socket_recv(client_socket)
            if not receive:
                log.warning(f"用户 {addr} 主动断开连接，正在关闭...")
                break
            if len(msg_queue) > config.receive_cache_max_length:
                service.send_msg(cons_resp_msg(f"拒绝请求，已超出最大请求缓存数！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR), addr, client_dict, user_dict)
            msg_queue.insert(0, receive)
            client_last_updated_int = util.get_timestamp()
        except socket.timeout:
            pass
        except ConnectionResetError:
            log.warning(f"用户 {addr} 强制中断连接！连接正在关闭...")
            break
        except Exception as e:
            log.error(f"未知异常！用户 {addr} 连接强制关闭...")
            log.error(e)
            break
        finally:
            if stop_event.is_set():
                log.warning(f"服务端关机中，用户 {addr} 连接强制关闭...")
                break
            if len(msg_queue) > 0 and not deal_event.is_set():
                deal_event.set()
                deal_thread = threading.Thread(target=deal, args=(addr, msg_queue, deal_event, stop_event, user_dict, client_dict))
                deal_thread.start()

    # 关闭连接
    if client_socket is not None:
        client_socket.close()
    log.info(f"连接已关闭: {addr}")
    if addr in client_dict:
        client_dict.pop(addr)
    if addr in user_dict:
        user_dict.pop(addr)
    log.info(f"当前连接数：{len(client_dict)}")


def deal(addr, msg_queue, deal_event, stop_event, user_dict, client_dict):
    client_socket = client_dict[addr]
    while True:
        try:
            if len(msg_queue) == 0:
                break
            receive = msg_queue.pop()

            # 接收到数据，尝试解码解密验签
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
            respond_dict = service.main_service(receive, addr, user, user_dict, client_dict)
            if respond_dict is not None:
                respond_dict["timestamp"] = util.get_timestamp()
                respond = util.sign_to_json(respond_dict, config.sign_key)
                log.debug(f"服务端回复->{addr}：{respond}")
                respond = util.aes_encrypt(respond, aes_key)
                respond = respond.encode('utf-8')
                util.socket_send(client_socket, respond)

            if stop_event.is_set():
                break
        except Exception as e:
            log.error(f"处理客户端{addr}的信息出错！")
            log.error(e)
    deal_event.clear()