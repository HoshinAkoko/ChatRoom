import dict_format
from src.util import util
import printer
def execute(listed_input, uni_var):
    match listed_input[0]:
        case "msg":
            text_msg(listed_input[1], uni_var)
        case "quit" | "q":
            if uni_var["conn_flag"]:
                uni_var["send_socket"].close()
            exit()
        case "conntest" | "ct":
            connection_test(listed_input[1], uni_var)


# 向服务器发送文字信息，目前连接在未加密函数
def text_msg(text, uni_var):
    curr_dict = dict_format.text_chat(text, util.get_timestamp())
    send_unencrypted(curr_dict, uni_var)

# 向服务器发送输入的字符串，仅用于测试
def connection_test(text, uni_var):
    if not uni_var["conn_flag"]:
        printer.prt_error("未连接到服务器，无法发送")
        return
    send_msg = text.encode("utf-8")
    uni_var["send_socket"].send(send_msg)

# 向服务器发送未加密信息，仅用于测试
def send_unencrypted(dicted, uni_var):
    if not uni_var["conn_flag"]:
        printer.prt_error("未连接到服务器，无法发送")
        return
    send_msg = str(dicted).encode("utf-8")
    uni_var["send_socket"].send(send_msg)
# 向服务器发送加密信息,待补全
def send_encrypted(dicted, uni_var):
    if not uni_var["conn_flag"]:
        printer.prt_error("未连接到服务器，无法发送")
        return
    send_msg = str(dicted).encode("utf-8")
    uni_var["send_socket"].send(send_msg)
