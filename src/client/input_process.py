# 读取输入，返回切分后的列表
def analyser(ipt_str):
    if ipt_str == "":
        return ["msg",""]
    if ipt_str[0] == "/":
        ipt_str = ipt_str.strip()
        ipt_str = ipt_str[1:]
        ipt_listed = ipt_str.split(" ")
    else:
        ipt_listed = ["msg",ipt_str]
    return ipt_listed



