"""
服务端服务
"""


from src.server import message, config, dao
from src.util import constant, util
from src.util.util import get_md5, get_new_key, get_timestamp
from src.util.date_util import date_int_to_str
from loguru import logger as log


# 主业务
def main_service(request_json, addr, user, user_dict, client_dict):
    request_dict = util.verify_to_dict(request_json, config.sign_key)
    if not request_dict:
        log.warning(f"客户端 {addr} 验签失败！")
        return cons_resp_msg(f"验签失败！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR)
    if "params" not in request_dict or "type" not in request_dict:
        return cons_resp_msg(f"参数错误！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR)
    if request_dict["type"] != constant.CLIENT_MSG_TYPE_LOGIN_IN and user is None:
        log.warning(f"客户端 {addr} 非法请求，需要先登录。")
        return cons_resp_msg(f"非法请求！请先登录。", addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_ERROR)
    if request_dict["type"] == constant.CLIENT_MSG_TYPE_LOGIN_IN:
        if user is not None:
            log.warning(f"客户端 {addr} 已登录，接收到重复的登录请求。")
            return cons_resp_msg(f"您已登录。如果要切换用户，请先登出。", addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_ERROR)
        return login(request_dict["params"], addr, user_dict)
    match request_dict["type"]:
        case constant.CLIENT_MSG_TYPE_SINGLE_MSG:
            return receive_msg(request_dict["params"], addr, user_dict, client_dict)
        case constant.CLIENT_MSG_TYPE_CHANGE_NICKNAME:
            return change_nickname(request_dict["params"], addr, user_dict)
        case constant.CLIENT_MSG_TYPE_CHANGE_SETTING:
            return change_setting(request_dict["params"], addr, user_dict)
        case constant.CLIENT_MSG_TYPE_REQUEST_HISTORY:
            return request_history(request_dict["params"], addr, user_dict)
        case _:
            return cons_resp_msg(f"未知请求！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR)


# 登陆业务
def login(params_dict, addr, user_dict):
    if "username" not in params_dict or "password" not in params_dict:
        return cons_resp_msg(f"用户名或密码不能为空！", addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_ERROR)
    username = params_dict['username']
    password = params_dict['password']
    user = dao.get_chat_user_by_name(username)
    if user is None:
        return cons_resp_msg(f"用户名或密码不正确！", addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_ERROR)
    if get_md5(password) != user.password:
        return cons_resp_msg(f"用户名或密码不正确！", addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_ERROR)
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
    response_dict = cons_resp_msg(f"登陆成功！上次登陆时间{date_int_to_str(user.last_updated_int)}",
                                  addr, constant.SERVER_MSG_TYPE_LOGIN_INFO, constant.CODE_NORMAL, params=response_params_dict)
    # 更新最后登陆时间
    last_update(user)
    return response_dict


# 消息业务，接收消息并广播
def receive_msg(params_dict, addr, user_dict, client_dict):
    if "msg" not in params_dict or "time" not in params_dict:
        return cons_resp_msg(f"消息格式错误！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR)
    if addr not in user_dict:
        return cons_resp_msg(f"登陆状态异常，请重新登陆！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR)
    user = user_dict[addr]
    if user.uid is None:
        return cons_resp_msg(f"登陆状态异常，请重新登陆！", addr, constant.SERVER_MSG_TYPE_ERROR_MSG, constant.CODE_ERROR)
    msg = params_dict['msg']
    time = params_dict['time']
    uid = user.uid
    nick = user.nickname if user.nickname is not None else "佚名"
    message.add_msg(time, msg, uid, nick)
    broadcast_recent(client_dict, user_dict)
    return None


# 广播最新消息
def broadcast_recent(client_dict, user_dict):
    recent = list()
    length = len(message.msg_list)
    while len(recent) < constant.SERVER_BROADCAST_RECENT_LENGTH and length > 0:
        length = length - 1
        msg = {
            "time": message.msg_list[length][0],
            "msg": message.msg_list[length][1],
            "uid": message.msg_list[length][2],
            "nick": message.msg_list[length][3]
        }
        recent.append(msg)
    send_params_dict = {
        "recent": recent
    }
    send_dict = cons_brod_msg(f"", "全体", constant.SERVER_MSG_TYPE_CHAT_BROADCAST, constant.CODE_NORMAL, params=send_params_dict)
    broadcast(send_dict, client_dict, user_dict)


def change_nickname(params_dict, addr, user_dict):
    return None


def change_setting(params_dict, addr, user_dict):
    return None


def request_history(params_dict, addr, user_dict):
    return None


# 发送广播信息，批量调用 send_msg()
def broadcast(send_dict, client_dict, user_dict):
    for k, v in client_dict.items():
        send_msg(send_dict, k, client_dict, user_dict, is_broadcast=True)


# 拼装单条信息，返回 dict 类型
def cons_resp_msg(msg, addr, msg_type, code, params=None):
    if params is None:
        params = {}
    if msg_type == constant.SERVER_MSG_TYPE_ERROR_MSG or code == constant.CODE_ERROR:
        log.warning(f"返回错误信息->{addr}: {msg}")
    else:
        log.info(f"返回信息->{addr}: {msg}")
    params["code"] = code
    params["msg"] = msg
    response_dict = {
        "type": msg_type,
        "params": params
    }
    return response_dict


# 拼装广播信息，返回 dict 类型
def cons_brod_msg(msg, target, msg_type, code, params=None):
    if params is None:
        params = {}
    if msg_type == constant.SERVER_MSG_TYPE_ERROR_MSG or code == constant.CODE_ERROR:
        log.warning(f"发送错误广播信息->{target}: {msg}")
    elif msg:
        log.debug(f"发送广播信息->{target}: {msg}")
    params["code"] = code
    params["msg"] = msg
    broadcast_dict = {
        "type": msg_type,
        "params": params
    }
    return broadcast_dict


# 更新用户最后登录时间
def last_update(user):
    unix_timestamp = get_timestamp() / 1000
    dao.update_user_last_updated_int_by_mid(user.mid, unix_timestamp)


# 发送 socket 信息到指定客户机
def send_msg(send_dict, addr, client_dict, user_dict, is_broadcast=False):
    if addr not in client_dict:
        log.error(f"{'广播' if is_broadcast else ''}信息发送失败，客户端 {addr} 已断线！")
    aes_key = config.common_key
    if addr in user_dict and user_dict[addr].key is not None:
        aes_key = user_dict[addr].key
    send_dict["timestamp"] = get_timestamp()
    send = util.sign_to_json(send_dict, config.sign_key)
    if not is_broadcast:
        log.debug(f"服务端发送->{addr}：{send}")
    respond = util.aes_encrypt(send, aes_key)
    respond = respond.encode('utf-8')
    util.socket_send(client_dict[addr], respond)