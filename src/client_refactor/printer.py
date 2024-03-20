def prt_message(msg):
    prt_msg = "\033[32m[Msg]\033[0m" + msg
    print(prt_msg)

def prt_error(msg):
    prt_msg = "\033[31m[Error]\033[0m" + msg
    print(prt_msg)

def prt_warning(msg):
    prt_msg = "\033[33m[Warning]\033[0m" + msg
    print(prt_msg)

def prt_info(msg):
    prt_msg = "\033[34m[Info]\033[0m" + msg
    print(prt_msg)

def prt_security(msg):
    prt_msg = "\033[35m[Security]\033[0m" + msg
    print(prt_msg)

def prt_request(msg):
    prt_msg = "\033[36m[Request]\033[0m" + msg
    print(prt_msg)

if __name__ == "__main__":
    prt_message("[14:15:12][可莉](10001):你好")
    prt_error("尚未连接到服务器")
    prt_warning("上一条信息发送时间过长")
    prt_info("连接到服务器127.0.0.1")
    prt_security("更改密码成功")
    prt_request("请输入密码：")
