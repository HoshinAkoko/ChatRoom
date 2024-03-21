"""
持久化
"""


from src.server.database import query, execute
from src.server.user import User
from src.util.util import get_timestamp


def get_all_chat_user_by_name_list(name_list):
    result = query(f"SELECT HEX(cu.id) as mid, cu.uid, cu.nickname, cu.is_admin, u.password, u.last_updated_int FROM chat_users cu LEFT JOIN users u ON u.id = cu.user_id WHERE u.name IN {get_placeholder_in_list(name_list)}", name_list)
    user_list = []
    for row in result:
        user_list.append(User(row[0], row[1], row[2], row[3], row[4], "")) if row is not None else None
    return user_list


def get_chat_user_by_name(name):
    result = query(f"SELECT HEX(cu.id) as mid, cu.uid, cu.nickname, cu.is_admin, u.password, u.last_updated_int FROM chat_users cu LEFT JOIN users u ON u.id = cu.user_id WHERE u.name = %s", [name])
    row = result[0] if len(result) > 0 else None
    return User(row[0], row[1], row[2], row[3], row[4], row[5], "") if row else None


def update_user_last_updated_int_by_mid(mid, unix_timestamp):
    execute_count = execute(f"UPDATE chat_users SET last_updated_int = %s WHERE id = UNHEX(%s)", [unix_timestamp, mid])
    return execute_count


if __name__ == '__main__':
    user_name = "admin"
    user = get_chat_user_by_name(user_name)
    print(f"get name {user_name}'s chat user's nickname:{user.nickname if user is not None else 'error'}")
    print(f"get name {user_name}'s chat user's mid:{user.mid if user is not None else 'error'}")
    print(f"sql count {update_user_last_updated_int_by_mid(user.mid, get_timestamp() / 1000)}")


def get_placeholder_in_list(params_list):
    placeholders = ', '.join(['%s'] * len(params_list))
    return f"({placeholders})"

