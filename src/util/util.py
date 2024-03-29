# 工具函数

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from datetime import datetime
from loguru import logger as log
import base64
import hashlib
import json
import os
import binascii
import struct


# 签名并转为 json
def sign_to_json(unsorted_dict_raw, sign_key):
    unsorted_dict = dict(unsorted_dict_raw)
    unsorted_dict["key"] = f"{sign_key}"
    sorted_dict = {key: unsorted_dict[key] for key in sorted(unsorted_dict)}
    key_json = json.dumps(sorted_dict)
    sign = get_md5(key_json)
    unsorted_dict.pop("key")
    unsorted_dict["sign"] = f"{sign}"
    signed_dict = {key: unsorted_dict[key] for key in sorted(unsorted_dict)}
    # log.debug(f"原始dict:{str(signed_dict)}")
    signed_json = json.dumps(signed_dict, ensure_ascii=False)
    # log.debug(f"转换json:{str(signed_json)}")
    return signed_json


# 验签并转为 dict
def verify_to_dict(signed_json, sign_key):
    unsorted_dict = json.loads(signed_json)
    if not "sign" in unsorted_dict:
        return False
    sign = unsorted_dict.pop("sign")
    unsorted_dict["key"] = f"{sign_key}"
    sorted_dict = {key: unsorted_dict[key] for key in sorted(unsorted_dict)}
    key_json = json.dumps(sorted_dict)
    verify_sign = get_md5(key_json)
    if verify_sign == sign:
        unsorted_dict.pop("key")
        return unsorted_dict
    else:
        return False


# 获取 md5
def get_md5(data):
    md5 = hashlib.md5()  # 创建一个md5对象
    md5.update(data.encode('utf-8'))  # 使用utf-8编码更新数据
    return md5.hexdigest().upper()  # 返回十六进制的哈希值


# 获取时间戳，毫秒单位
def get_timestamp():
    now = datetime.now()
    timestamp_milliseconds = int(now.timestamp() * 1000)
    return timestamp_milliseconds


# AES 加密
def aes_encrypt(data, hex_key):
    key = bytes.fromhex(hex_key)  # base64.b64decode(base64_key)
    if len(key) not in [16, 24, 32]:
        raise ValueError("Key size must be either 16, 24, or 32 bytes.")
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted_data = cipher.encrypt(pad(data.encode(), AES.block_size))
    return base64.b64encode(iv + encrypted_data).decode()


# AES 解密
def aes_decrypt(encrypted_data, hex_key):
    # log.debug(f"待解密内容:{encrypted_data} 密钥:{hex_key}")
    key = bytes.fromhex(hex_key)
    encrypted_data_bytes = base64.b64decode(encrypted_data)
    iv = encrypted_data_bytes[:16]
    encrypted_data_only = encrypted_data_bytes[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(encrypted_data_only), AES.block_size).decode()
    return decrypted_data


# 带消息长度前缀的 socket 发送
def socket_send(socket, message):
    message_length = len(message)
    length_prefix = struct.pack('>I', message_length)  # '>I'表示大端模式的无符号整型
    socket.sendall(length_prefix + message)


# 带消息长度前缀的 socket 接收
def socket_recv(socket):
    # 首先读取消息长度的前缀（4字节）
    length_prefix = socket.recv(4)
    if not length_prefix:
        return None  # 连接关闭
    message_length = struct.unpack('>I', length_prefix)[0]

    # 根据消息长度读取完整的消息
    message = b''
    while len(message) < message_length:
        chunk = socket.recv(message_length - len(message))
        if not chunk:
            raise Exception("Expected length of message not received")
        message += chunk
    return message


# 读取配置项
def get_config(config, section, option, default_value, is_int=False):
    try:
        value = config[section][option]
        if value is None and default_value is None and is_int:
            return 0
        if value is None and default_value is None and not is_int:
            return None
        if value is None and default_value is not None:
            value = default_value
        if is_int:
            return int(value)
        return value
    except KeyError or TypeError or ValueError:
        try:
            if is_int:
                return int(default_value)
            return default_value
        except TypeError or ValueError:
            return 0


# 生成一个随机 AES KEY
def get_new_key():
    aes_key = os.urandom(16)
    hex_key = binascii.hexlify(aes_key).decode('ascii')
    return hex_key


if __name__ == "__main__":
    # test_dict = {
    #     "aaa": "123",
    #     "ccc": 321,
    #     "bbb": 231
    # }
    # test_json = sign_to_json(test_dict, "sign_key")
    # print(f"signed json: {test_json}")
    # verify_dict = verify_to_dict(test_json, "sign_key")
    # if not verify_dict:
    #     print(f"check failed!")
    # else:
    #     print(f"check sign success! dict is {verify_dict}")
    # my_key = str(get_new_key())
    # print(my_key)
    # decrypted_data = "hello"
    # encrypted_data = aes_encrypt(decrypted_data, my_key)
    # print(encrypted_data)
    pass

