import time
from src.util import util

# 本模块用于将输入的信息转为和服务器通讯的标准dict格式
# 消息代码1 普通文本消息
def text_chat(text,send_time=0):
    correct_dict = {"type":1,
                    "timestamp":util.get_timestamp(),
                    "params":{
                        "msg":text,
                        "time":send_time}}
    return correct_dict