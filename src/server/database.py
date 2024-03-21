"""
数据源
"""
import configparser
import mysql.connector
from mysql.connector import Error
from mysql.connector import MySQLConnection
from src.util import util
from loguru import logger as log
from pathlib import Path


# 数据库实例
database = None
# 配置项
config_host = None
config_user = None
config_passwd = None
config_database = None


def connect():
    config_init()
    global database
    try:
        database = mysql.connector.connect(
            host=config_host,
            user=config_user,
            passwd=config_passwd,
            database=config_database
        )
        # if sql is None:
        #     raise Error("无法连接到数据库")
    except Exception as e:
        log.error(f"数据库连接异常！请检查数据库配置。")
        log.error(e)
        raise e


def config_init():
    # 加载配置文件
    config = configparser.ConfigParser()
    config_file = Path('server_config.ini')
    if not config_file.exists():
        config_file = Path('../../server_config.ini')
    if not config_file.exists():
        raise FileNotFoundError(f"配置文件不存在！")
    config.read(config_file)
    global config_host, config_user, config_passwd, config_database

    config_host        = util.get_config(config, 'database', 'host', default_value=config_host)
    config_user        = util.get_config(config, 'database', 'user', default_value=config_user)
    config_passwd      = util.get_config(config, 'database', 'passwd', default_value=config_passwd)
    config_database    = util.get_config(config, 'database', 'database', default_value=config_database)


def disconnect():
    global database
    if isinstance(database, MySQLConnection):
        database.close()


def query(sql, params):
    global database
    if not isinstance(database, MySQLConnection):
        connect()
    cursor = database.cursor()
    try:
        cursor.execute(sql, tuple(params))
        result = cursor.fetchall() # 返回 a list of tuples
    except Error as e:
        log.error(f"数据库查询出错！")
        log.error(e)
        result = []
    finally:
        cursor.close()
    return result


def execute(sql, params):
    global database
    if not isinstance(database, MySQLConnection):
        connect()
    cursor = database.cursor()
    try:
        cursor.execute(sql, tuple(params))
        database.commit()  # 确认执行 INSERT、UPDATE、DELETE
        affected_rows = cursor.rowcount
    except Error as e:
        database.rollback()  # 如果出现错误，回滚
        log.error(f"数据库修改出错！")
        log.error(e)
        affected_rows = 0
    finally:
        cursor.close()
    return affected_rows
