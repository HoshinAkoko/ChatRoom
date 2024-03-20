import config_op
import socket
import threading
from src.util import util
import dict_format
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