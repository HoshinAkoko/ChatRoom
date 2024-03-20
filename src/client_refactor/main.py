import command
import printer
import config_op
import socket
# 持续监听控制台 input ，解析并传递给 command
def main(uni_var):
    uni_var["conn_flag"] = False
    while True:
        try:
            listed_input = analyser(input())
            if listed_input[0] == "connect" or listed_input[0] == "conn" or listed_input[0] == "c":
                connect(listed_input,uni_var)
            else:
                command.execute(listed_input, uni_var)
        except Exception as e:
            printer.prt_error(f"{e}")

# 连接到socket
def connect(listed_input,uni_var):
    if len(listed_input) == 1:
        default_addr = uni_var["config"]["default_addr"]
        ip = default_addr.split(":")[0]
        port = default_addr.split(":")[1]
    elif len(listed_input) == 2:
        ip = listed_input[1].split(":")[0]
        port = listed_input[1].split(":")[1]
    elif len(listed_input) == 3:
        ip = listed_input[1]
        port = listed_input[2]
    else:
        print("参数错误")
        return
    printer.prt_info(f"尝试连接：{ip}:{port}")
    uni_var["send_socket"] = socket.socket()
    uni_var["send_socket"].connect((ip, int(port)))
    printer.prt_info(f"已连接到{ip}:{port}")
    uni_var["conn_flag"] = True


# 解析输入的命令
def analyser(input_str):
    if input_str == "":
        return ["msg", ""]
    if input_str[0] == "/":
        ipt_str = input_str.strip()
        ipt_str = ipt_str[1:]
        ipt_listed = ipt_str.split(" ")
    else:
        ipt_listed = ["msg", input_str]
    return ipt_listed