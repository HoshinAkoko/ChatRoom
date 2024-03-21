"""
用户实体类
"""


class User:
    def __init__(self, mid, uid, nickname, is_admin, password, last_updated_int, key):
        self.mid = mid
        self.uid = uid
        self.nickname = nickname
        self.is_admin = is_admin
        self.password = password
        self.last_updated_int = last_updated_int
        self.key = key