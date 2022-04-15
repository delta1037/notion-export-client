# author: delta1037
# Date: 2022/04/15
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -c -i notion-dump.ico notion_dump_server_single.py -p api/notion_dump_api.py
import json
import os
import sys
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi, DB_INSERT_TYPE_PAGE, DB_INSERT_TYPE_LINK

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
CONFIG_FILE_NAME = SEVER_ABS_PATH + "/config.json"
LOG_FILE = SEVER_ABS_PATH + "/dump.log"
NotionDump.TMP_DIR = SEVER_ABS_PATH + NotionDump.TMP_DIR
VERSION = "1.0(s)"


class NotionBackup:
    def __init__(self):
        # 配置获取
        self.config = None
        self.__read_config()

        # dump api
        self.dump_api = None

        print("log write to " + LOG_FILE)
        print("start backup, it may take a long time ...")

        # 输出重定向
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def restore_std(self):
        sys.stdout = self.stdout_bak
        sys.stderr = self.stderr_bak
        print("backup success ~ ")

    def __read_config(self):
        try:
            with open(CONFIG_FILE_NAME, encoding="utf-8") as conf_file_handle:
                self.config = json.load(conf_file_handle)
        except FileNotFoundError:
            print("Configuration file does not exist")
        except JSONDecodeError:
            print("Configuration file is corrupted")

    def get_key(self, key):
        return self.config.get(key)

    def check_config(self):
        if self.config is None:
            return False
        return True

    def write(self, log_msg):
        # 将所有内容写入到文件
        with open(LOG_FILE, 'a+', encoding='utf-8') as f:
            f.write(log_msg)
        f.close()

    def start_dump(self):
        # 从配置获取输入值
        if not self.check_config():
            print("Config init failed, file:" + CONFIG_FILE_NAME)
            return
        self.write("server version: " + VERSION + "\n")
        _token = self.get_key("token")
        _page_id = self.get_key("page_id")
        _dump_type_str = self.get_key("page_type")
        _dump_type = NotionDump.DUMP_TYPE_PAGE
        if _dump_type_str == "page":
            _dump_type = NotionDump.DUMP_TYPE_PAGE
        elif _dump_type_str == "database":
            _dump_type = NotionDump.DUMP_TYPE_DB_TABLE
        elif _dump_type_str == "block":
            _dump_type = NotionDump.DUMP_TYPE_BLOCK
        else:
            print("unknown type " + _dump_type_str)
            return
        _export_child = self.get_key("export_child_page")
        _dump_path = SEVER_ABS_PATH + self.get_key("dump_path")

        # 配置错误按照默认处理
        _page_parser_type = NotionDump.PARSER_TYPE_MD
        if self.get_key("page_parser_type") == "plain":
            _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
        _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
        if self.get_key("db_parser_type") == "md":
            _db_parser_type = NotionDump.PARSER_TYPE_MD

        _db_insert_type = DB_INSERT_TYPE_PAGE
        if self.get_key("db_insert_type") is not None and self.get_key("db_insert_type") == "link":
            _db_insert_type = DB_INSERT_TYPE_LINK

        # 初始化 API
        dump_api = NotionDumpApi(
            token=_token,
            page_id=_page_id,
            dump_path=_dump_path,
            dump_type=_dump_type,
            export_child=_export_child,
            page_parser_type=_page_parser_type,
            db_parser_type=_db_parser_type,
            db_insert_type=_db_insert_type,
        )

        # 开始导出
        print("start export")
        dump_api.start_dump()


if __name__ == '__main__':
    notion_back = NotionBackup()
    notion_back.start_dump()

    # 恢复输出重定向
    notion_back.restore_std()