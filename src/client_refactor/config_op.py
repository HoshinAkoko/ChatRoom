import json

# 写入到config文件
def write_config(name, value):
    with open("config.json", 'r', encoding="utf-8") as f:
        datas = json.load(f)
        f.close()
    datas[name] = value
    with open("config.json", 'w', encoding="utf-8") as f:
        json.dump(datas, f)
        f.close()

# 从config文件读取所有配置
def read_all_config():
    with open("config.json", 'r', encoding="utf-8") as f:
        datas = json.load(f)
        f.close()
        return datas

if __name__ == "__main__":
    pass