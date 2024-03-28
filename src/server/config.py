"""
服务端配置项
"""


import configparser
from pathlib import Path
from src.util.util import get_config


# 默认配置
host = "0.0.0.0"                                    # 服务端ip
port = 9999                                         # 服务端端口
max_client = 3                                      # 每轮监听等待时间
common_key = "0123456789ABCDEF0123456789ABCDEF"     # 默认消息密钥
sign_key = "OPSTART"                                # 验签密钥
receive_cache_max_length = 100                      # 每个客户端最大缓冲请求数


# 读取配置
def config_init():
    # 加载配置文件
    config = configparser.ConfigParser()
    config_file = Path('server_config.ini')
    if not config_file.exists():
        config_file = Path('../../server_config.ini')
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在！")
    config.read(config_file)
    global host, port, max_client, common_key, sign_key, receive_cache_max_length

    host                        = get_config(config, 'server', 'host', default_value=host)
    port                        = get_config(config, 'server', 'port', default_value=port, is_int=True)
    max_client                  = get_config(config, 'server', 'max_client', default_value=max_client, is_int=True)
    common_key                  = get_config(config, 'server', 'common_key', default_value=common_key)
    sign_key                    = get_config(config, 'server', 'sign_key', default_value=sign_key)
    receive_cache_max_length    = get_config(config, 'server', 'receive_cache_max_length', default_value=receive_cache_max_length, is_int=True)

if __name__ == '__main__':
    config_init()