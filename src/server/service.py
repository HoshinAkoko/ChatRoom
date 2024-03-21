"""
服务端服务
"""


from src.server import dao
from src.util import constant
from src.util.util import get_md5, get_new_key, get_timestamp
from src.util.date_util import date_int_to_str


def login(params_dict, addr, user_dict):
    username = params_dict['username']
    password = params_dict['password']
    if username is None or password is None:
        return error_msg("用户名或密码不能为空！")
    user = dao.get_chat_user_by_name(username)
    if user is None:
        return error_msg("用户名或密码不正确！")
    if get_md5(password) != user.password:
        return error_msg("用户名或密码不正确！")
    # 登陆成功，检查是否已在别的位置登录，存在则强制顶下线(不影响TCP连接)
    for k, v in user_dict.items():
        if v.mid == user.mid:
            user_dict[k] = None
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
    return None


def change_nickname(params_dict, addr, user_dict):
    return None


def change_setting(params_dict, addr, user_dict):
    return None


def request_history(params_dict, addr, user_dict):
    return None

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