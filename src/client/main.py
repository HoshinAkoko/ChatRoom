import txt_reader
import socket
import threading
import input_process
# 解析命令内容并分流到对应函数
def execute(cmd_list):
    match cmd_list[0]:
        case "msg":
            print(cmd_list[1])
            # 待实现：msg_send(cmd_list[1])
        case "exit":
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
# 用于向服务器发送输入的消息
def connection_test(cmd_list):
    send_msg = cmd_list[1].encode("utf-8")
    socket_client.send(send_msg)
# 断开连接
def disconnect():
    socket_client.close()
    print("已断开连接")








# 启动命令
while True:
    listed_input = input_process.analyser(input())
    execute(listed_input)