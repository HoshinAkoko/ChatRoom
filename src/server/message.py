"""
缓存消息队列
"""


from src.server import dao
from src.util import constant
from loguru import logger as log


# 动态存近期的记录
msg_list = list()
# 缓存放入数据库
msg_cache = set()


def save_cache():
    global msg_cache
    length = len(msg_cache)
    log.info(f"已缓存消息数: {length}，达到存储数量，开始进行存入...")
    count = dao.save_message_set(msg_cache)
    if count >= length:
        log.info(f"消息保存成功！")
        return
    else:
        log.critical(f"警告！消息缓存失败，请手动保存：{str(msg_cache)}")
        if len(msg_cache) > constant.MAX_CACHE_ERROR_CLEAR_LENGTH:
            log.critical(f"消息缓存超过最大上限，强制清除！")
            msg_cache.clear()


def receive_msg(time, msg, uid):
    global msg_list, msg_cache
    p = len(msg_list)
    while p > 0:
        if time >= msg_list[p - 1][0]:
            msg_list.insert(p, (time, msg, uid))
            break
        p = p - 1
    if p == 0:
        msg_list.insert(p, (time, msg, uid))
    if len(msg_list) > constant.MAX_MSG_LIST_LENGTH:
        msg_list.pop(0)
    msg_cache.add((time, msg, uid))
    if len(msg_cache) >= constant.MAX_SAVE_MSG_LENGTH:
        if (len(msg_cache) - constant.MAX_SAVE_MSG_LENGTH) % 10 == 0:
            save_cache()

if __name__ == '__main__':
    receive_msg(1, 'a', '001')
    receive_msg(3, 'b', '002')
    receive_msg(5, 'c', '002')
    receive_msg(4, 'd', '002')
    receive_msg(8, 'e', '001')
    receive_msg(6, 'f', '001')
    receive_msg(9, 'g', '002')
    receive_msg(7, 'h', '002')
    receive_msg(2, 'i', '001')
    receive_msg(0, 'j', '002')
    print(f"{str(msg_list)}")


