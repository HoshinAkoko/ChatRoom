"""
服务端服务
"""


from src.server import message
from src.server import dao
from src.util import constant, util
from src.util.util import get_md5, get_new_key, get_timestamp
from src.util.date_util import date_int_to_str
from src.server import config
from loguru import logger as log


def login(params_dict, addr, user_dict):
    if "username" not in params_dict or "password" not in params_dict:
        return response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, addr, f"用户名或密码不能为空！", constant.CODE_ERROR)
    username = params_dict['username']
    password = params_dict['password']
    user = dao.get_chat_user_by_name(username)
    if user is None:
        return response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, addr, f"用户名或密码不正确！", constant.CODE_ERROR)
    if get_md5(password) != user.password:
        return response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, addr, f"用户名或密码不正确！", constant.CODE_ERROR)
    # 登陆成功，检查是否已在别的位置登录，存在则强制顶下线(不影响TCP连接)
    for k, v in user_dict.items():
        if v.mid == user.mid:
            user_dict.pop(k) #[k] = None
    key = get_new_key()
    user.key = key
    user_dict[addr] = user
    response_params_dict = {
        "key": key,
        "nickname": user.nickname,
        "uid": user.uid
    }
    response_dict = response_msg(constant.SERVER_MSG_TYPE_LOGIN_INFO, 
                                 addr, 
                                 f"登陆成功！上次登陆时间{date_int_to_str(user.last_updated_int)}", 
                                 constant.CODE_NORMAL, 
                                 params=response_params_dict
    )
    # 更新最后登陆时间
    last_update(user)
    return response_dict


def receive_msg(params_dict, addr, user_dict):
    if "msg" not in params_dict or "time" not in params_dict:
        return response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"消息格式错误！", constant.CODE_ERROR)
    if addr not in user_dict:
        return response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"登陆状态异常，请重新登陆！", constant.CODE_ERROR)
    user = user_dict[addr]
    if user.uid is None:
        return response_msg(constant.SERVER_MSG_TYPE_ERROR_MSG, addr, f"登陆状态异常，请重新登陆！", constant.CODE_ERROR)
    msg = params_dict['msg']
    time = params_dict['time']
    uid = user.uid
    message.receive_msg(time, msg, uid)
    return None


def change_nickname(params_dict, addr, user_dict):
    return None


def change_setting(params_dict, addr, user_dict):
    return None


def request_history(params_dict, addr, user_dict):
    return None


# 返回单条错误信息
def response_msg(msg_type, addr, msg, code, params=None):
    if params is None:
        params = {}
    if msg_type == constant.SERVER_MSG_TYPE_ERROR_MSG or code == constant.CODE_ERROR:
        log.warning(f"返回错误信息->{addr}: {msg}")
    else:
        log.info(f"返回信息->{addr}: {msg}")
    params["code"] = code
    params["msg"] = msg
    error_dict = {
        "type": msg_type,
        "params": params
    }
    return error_dict


def response_msg1(params_dict, code, msg, msg_type):
    params_dict["code"] = code
    params_dict["msg"] = msg
    response_dict = {
        "type": msg_type,
        "params": params_dict
    }
    return response_dict


def last_update(user):
    unix_timestamp = get_timestamp() / 1000
    dao.update_user_last_updated_int_by_mid(user.mid, unix_timestamp)


def send_msg(send_dict, addr, client_dict, user_dict):
    if addr not in client_dict:
        log.error(f"信息发送失败，客户端 {addr} 已断线！")
    aes_key = config.common_key
    if addr in user_dict and user_dict[addr].key is not None:
        aes_key = user_dict[addr].key
    send_dict["timestamp"] = get_timestamp()
    send = util.sign_to_json(send_dict, config.sign_key)
    log.debug(f"服务端发送->{addr}：{send}")
    respond = util.aes_encrypt(send, aes_key)
    respond = respond.encode('utf-8')
    util.socket_send(client_dict[addr], respond)