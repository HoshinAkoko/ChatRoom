"""
缓存消息队列
"""


import threading
from src.server import dao
from src.util import constant
from loguru import logger as log


# 动态存近期的记录
msg_list = list()
# 缓存放入数据库
msg_cache = set()
# 持久化线程状态
save_event = threading.Event()


# 存入新消息
def add_msg(time, msg, uid, nick):
    global msg_list, msg_cache
    p = len(msg_list)
    while p > 0:
        if time >= msg_list[p - 1][0]:
            msg_list.insert(p, (time, msg, uid, nick))
            break
        p = p - 1
    if p == 0:
        msg_list.insert(p, (time, msg, uid, nick))
    if len(msg_list) > constant.MAX_MSG_LIST_LENGTH:
        msg_list.pop(0)
    msg_cache.add((time, msg, uid, nick))
    if len(msg_cache) >= constant.MAX_SAVE_MSG_LENGTH:
        if (len(msg_cache) - constant.MAX_SAVE_MSG_LENGTH) % 10 == 0:
            if not save_event.is_set():
                save_event.set()
                save_thread = threading.Thread(target=save_cache_all, args=(save_event,))
                save_thread.start()


# 立即持久化全部缓存消息
def save_cache_all(thread_event=None):
    global msg_cache
    length = len(msg_cache)
    if length <= 0:
        return
    log.info(f"已缓存消息数: {length}，全部进行存入...")
    fail_set = dao.save_message_set_all(msg_cache)
    if not fail_set:
        log.info(f"缓存消息保存成功！")
        return
    else:
        log.critical(f"警告！消息缓存失败，请手动保存：{str(fail_set)}")
    if thread_event is not None:
        thread_event.clear()


# 持久化单条缓存消息，周期调用
def save_cache_one():
    global msg_cache
    length = len(msg_cache)
    if length <= 0:
        return
    log.debug(f"已缓存消息数: {length}，随机存入一条...")
    msg = msg_cache.pop()
    count = dao.save_message_set_one(msg)
    if count > 0:
        pass
        # log.debug(f"缓存消息保存成功！")
    else:
        log.error(f"缓存消息保存失败！该条消息为{str(msg)}")


if __name__ == '__main__':
    add_msg(1, 'a', '001', 'm5')
    add_msg(3, 'b', '002', 'm5')
    add_msg(5, 'c', '002', 'm5')
    add_msg(4, 'd', '002', 'm5')
    add_msg(8, 'e', '001', 'm5')
    add_msg(6, 'f', '001', 'm5')
    add_msg(9, 'g', '002', 'm5')
    add_msg(7, 'h', '002', 'm5')
    add_msg(2, 'i', '001', 'm5')
    add_msg(0, 'j', '002', 'm5')
    print(f"{str(msg_list)}")
