import config_op
import socket
import threading
from src.util import util
import dict_format


# 解析输入切片到list中
def analyser(ipt_str):
    if ipt_str == "":
        return ["msg", ""]
    if ipt_str[0] == "/":
        ipt_str = ipt_str.strip()
        ipt_str = ipt_str[1:]
        ipt_listed = ipt_str.split(" ")
    else:
        ipt_listed = ["msg", ipt_str]
    return ipt_listed


# 解析命令内容并分流到对应函数
def execute(cmd_list):
    match cmd_list[0]:
        case "msg":
            print(f"[{nickname}]{cmd_list[1]}")
            text_msg(cmd_list[1])
        case "quit" | "q":
            global conn_flag
            if conn_flag:
                disconnect()
            input("按任意键退出")
            exit()
        case "connect" | "conn" | "c":
            connect(cmd_list)
        case "connection_test" | "ct":
            connection_test(cmd_list)
        case "disconnect" | "disconn" | "dc":
            disconnect()


# 连接到服务器
def connect(cmd_list):
    if len(cmd_list) == 1:
        default_addr = txt_reader.read_config("default_addr")
        ip = default_addr.split(":")[0]
        port = default_addr.split(":")[1]
    elif len(cmd_list) == 2:
        ip = cmd_list[1].split(":")[0]
        port = cmd_list[1].split(":")[1]
    elif len(cmd_list) == 3:
        ip = cmd_list[1]
        port = cmd_list[2]
    else:
        print("参数错误")
        return
    print(f"连接到{ip}:{port}")
    global socket_client
    socket_client = socket.socket()
    socket_client.connect((ip, int(port)))
    global conn_flag
    conn_flag = True

# 用于向服务器发送测试消息
def connection_test(cmd_list):
    if not conn_flag:
        print("未连接到服务器，无法发送")
        return
    send_msg = cmd_list[1].encode("utf-8")
    socket_client.send(send_msg)


# 发送文本信息
def text_msg(text):
    send_encrypted(dict_format.text_chat(text,util.get_timestamp()))


# 发送加密信息，待补全
def send_encrypted(dicted):
    if not conn_flag:
        print("未连接到服务器，无法发送")
        return
    send_msg = str(dicted).encode("utf-8")
    socket_client.send(send_msg)


# 断开连接
def disconnect():
    socket_client.close()
    print("已断开连接")


# 启动命令
nickname = txt_reader.read_config("nickname")
conn_flag = False
while True:
    try:
        listed_input = analyser(input())
        execute(listed_input)
    except Exception as e:
        print(f"错误：{e}")