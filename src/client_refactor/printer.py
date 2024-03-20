"""
prt_message：Msg
prt_error：Error
prt_warning：Warning
prt_info：Info
prt_security：Security
prt_request:Request
prt_default:Default
prt_clr()
"""
def prt_color(msg,color=37,label="Default"):
    """
黑色：0 红色：31 绿色：32 黄色：33 蓝色：34 品红：35 青色：36 白色：37
    """
    prt_msg = f"\033[{str(color)}m[{label}]\033[0m{msg}"
    print(prt_msg)

def prt_message(msg):
    prt_msg = "\033[32m[Msg]\033[0m" + msg
    print(prt_msg)

def prt_default(msg):
    prt_msg = "\037[32m[Default]\033[0m" + msg
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
    prt_color("你好",33,"33")
