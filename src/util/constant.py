"""
常量表
"""


#项目名称
PROJECT_NAME = "ChatRoom"


# 客户端请求
CLIENT_MSG_TYPE_LOGIN_OUT           = -1
CLIENT_MSG_TYPE_LOGIN_IN            = 0
CLIENT_MSG_TYPE_SINGLE_MSG          = 1
CLIENT_MSG_TYPE_CHANGE_NICKNAME     = 2
CLIENT_MSG_TYPE_CHANGE_SETTING      = 3
CLIENT_MSG_TYPE_REQUEST_HISTORY     = 4

# 服务端发送
SERVER_MSG_TYPE_ERROR_MSG           = -1
SERVER_MSG_TYPE_LOGIN_INFO          = 0
SERVER_MSG_TYPE_CHAT_BROADCAST      = 1
SERVER_MSG_TYPE_NICKNAME_INFO       = 2
SERVER_MSG_TYPE_SETTING_INFO        = 3
SERVER_MSG_TYPE_HISTORY_INFO        = 4

# 消息 CODE 标识
CODE_ERROR                          = -1
CODE_NORMAL                         = 0
CODE_SUCCESS                        = 1

# 服务端缓存消息数量
MAX_MSG_LIST_LENGTH                 = 100   # 服务端各种即时业务覆盖的消息长度
MAX_SAVE_MSG_LENGTH                 = 50    # 超出这个数就会尝试进行一次数据库存储
MAX_CACHE_ERROR_CLEAR_LENGTH        = 100   # 缓存的最大保存数量，超过这个数还没有成功存入数据库就会强制清除

# LOGO
SERVER_TITLE = "Server"
SERVER_SUBTITLE = "Indev"
SERVER_VERSION = "0.1"

CLIENT_TITLE = "Client"
CLIENT_SUBTITLE = "Indev"
CLIENT_VERSION = "0.1"

CHATROOM_LOGO = r"""
===# A Python Project #==============================
  ____ _           _     ____                        
 / ___| |__   __ _| |_  |  _ \  ___   ___  _ __ ___  
| |   | '_ \ / _` | __| | |_) |/ _ \ / _ \| '_ ` _ \ 
| |___| | | | (_| | |_  |  _ <| (_) | (_) | | | | | |
 \____|_| |_|\__,_|\__| |_| \_\\___/ \___/|_| |_| |_|
==============================# Client Indev 0.1 #===
"""
def get_logo(title, sub_title, version):
    bottom = "==============================# Client Indev 0.1 #==="
    detail = f"# {title} {sub_title} {version} #==="
    r = range(len(bottom) - len(detail))
    filler = ""
    for i in range(len(r)):
        filler += "="
    return CHATROOM_LOGO.replace(bottom, filler + detail)


if __name__ == "__main__":
    print(get_logo("Server", "Indev", "0.1"))