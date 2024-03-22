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
        return error_msg(addr, f"用户名或密码不能为空！")
    username = params_dict['username']
    password = params_dict['password']
    user = dao.get_chat_user_by_name(username)
    if user is None:
        return error_msg(addr, f"用户名或密码不正确！")
    if get_md5(password) != user.password:
        return error_msg(addr, f"用户名或密码不正确！")
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
    response_dict = response_msg(response_params_dict, 1, f"登陆成功！上次登陆时间{date_int_to_str(user.last_updated_int)}",
                 constant.SERVER_MSG_TYPE_LOGIN_INFO)
    # 更新最后登陆时间
    last_update(user)
    return response_dict


def receive_msg(params_dict, addr, user_dict):
    if "msg" not in params_dict or "time" not in params_dict:
        return error_msg(addr, f"消息格式错误！")
    if addr not in user_dict:
        return error_msg(addr, f"登陆状态异常，请重新登陆！")
    user = user_dict[addr]
    if user.uid is None:
        return error_msg(addr, f"登陆状态异常，请重新登陆！")
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
def error_msg(addr, msg):
    log.warning(f"返回错误信息->{addr}: {msg}")
    error_dict = {
        "type": -1,
        "params": {
            "code": -1,
            "msg": f"{msg}"
        }
    }
    return error_dict


def response_msg(params_dict, code, msg, msg_type):
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
    log.debug(f"服务端发送：{send}")
    respond = util.aes_encrypt(send, aes_key)
    respond = respond.encode('utf-8')
    client_dict[addr].send(respond)