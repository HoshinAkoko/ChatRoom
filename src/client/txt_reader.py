import json

# 写入到config文件
def write_config(name, value):
    with open("config", 'r', encoding="utf-8") as f:
        datas = json.load(f)
        f.close()
    datas[name] = value
    with open("config", 'w', encoding="utf-8") as f:
        json.dump(datas, f)
        f.close()

# 从config文件仅读取
def read_config(name):
    with open("config", 'r', encoding="utf-8") as f:
        datas = json.load(f)
        f.close()
        return datas[name]

if __name__ == "__main__":
    pass