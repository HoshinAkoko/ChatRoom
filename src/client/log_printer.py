import json


# 不应调用-从目标文件中读取所有记录
def ins_log(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        msg_list = []
        for line in f:
            msg_list.append(json.loads(line.strip()))
        f.close()
        return msg_list

# 可调用-打印包含所有记录的列表
def all_msg(filename, show_type_dict):
    msg_list = ins_log(filename)
    print_list(msg_list, show_type_dict)


# 可调用-打印包含特定数据的列表
def search_compare(filename, arg_type, arg_value, show_type_dict):
    msg_list = ins_log(filename)
    searched_list = []
    for i in msg_list:
        if str(i["params"][arg_type]) == arg_value:
            searched_list.append(i)
    print_list(searched_list, show_type_dict)


# 可调用-打印符合有关时间范围的列表
def search_time(filename, time, show_type_dict):
    msg_list = ins_log(filename)
    searched_list = []
    for i in msg_list:
        if time["start"] <= i["params"]["time"] <= time["end"]:
            searched_list.append(i)
    print_list(searched_list, show_type_dict)


# 不应调用-打印列表内容，待扩展功能
def print_list(msg_list, show_type_dict):
    for i in msg_list:
        msg = ""
        if show_type_dict["time"]:
            msg += f"[{i['params']['time']}]"
        if show_type_dict["nickname"]:
            msg += f"[{i['params']['nickname']}]"
        if show_type_dict["uid"]:
            msg += f"({i['params']['uid']})"
        if show_type_dict["msg"]:
            msg += f":{i['params']['msg']}"
        print(msg)


if __name__ == "__main__":
    my_show_type_dict = {"time": True, "nickname": True, "uid": True, "msg": True}
    # all_msg("simulated_logs.txt",show_type_dict)
    search_compare("simulated_logs.txt", "time", "12344", my_show_type_dict)
    input()