# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com

import json
import os
import sys
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi, DB_INSERT_TYPE_PAGE, DB_INSERT_TYPE_LINK
from api.backup_info import BackupInfo

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
CONFIG_FILE_NAME = SEVER_ABS_PATH + "/config.json"
NotionDump.TMP_DIR = SEVER_ABS_PATH + NotionDump.TMP_DIR
VERSION = "1.4"


class NotionBackup:
    def __init__(self, logger):
        # 配置获取
        self.config = None
        self.__read_config()

        # dump api
        self.dump_api = None

        print("log write to dump.log")
        print("start backup, it may take a long time ...")

        # 输出重定向
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        sys.stdout = logger
        sys.stderr = logger

    def restore_std(self):
        sys.stdout = self.stdout_bak
        sys.stderr = self.stderr_bak

    def __read_config(self):
        try:
            with open(CONFIG_FILE_NAME, encoding="utf-8") as conf_file_handle:
                self.config = json.load(conf_file_handle)
        except FileNotFoundError as e:
            print("\nConfiguration file does not exist\n")
            print(e)
        except JSONDecodeError as e:
            print("\nConfiguration file is corrupted\n")
            print(e)

    def get_key(self, key, prefix, default=None):
        if prefix is None:
            if key in self.config:
                return self.config.get(key)
            else:
                return default
        else:
            if prefix not in self.config:
                return default
            if key not in self.config.get(prefix):
                return default
            return self.config.get(prefix).get(key)

    def check_config(self):
        if self.config is None:
            return False
        return True

    def start_dump(self, force_auto=False):
        if not self.check_config():
            print("Config init failed, file:" + CONFIG_FILE_NAME)
            return

        # 开启DEBUG模式
        debug_mode = self.get_key("debug", None, default=False)
        if debug_mode is True:
            NotionDump.DUMP_MODE = NotionDump.DUMP_MODE_DEBUG
        self.dump_api = NotionDumpApi(debug=debug_mode)

        if self.get_key("backup_type", None) == "single":
            self.start_dump_single()
        else:
            self.start_dump_multi()

        print("backup success ~ ")
        # 恢复输出重定向
        self.restore_std()

        if not force_auto and self.get_key("auto_close", None) is False:
            # 终端停顿
            input()

    def start_dump_multi(self):
        print("server version: " + VERSION + "(m)\n")
        # 备份内容需要的token
        dump_token = self.get_key("backup_token", "multi")
        if len(dump_token) == 0:
            print("dump_token is null")
        # 备份信息页面的token
        backup_info_token = self.get_key("backup_info_token", "multi")
        if len(backup_info_token) == 0:
            print("backup_info_token is null")
        # 存储需要备份的内容的数据库id
        backup_list_id = self.get_key("backup_list_id", "multi")
        if len(backup_list_id) == 0:
            print("backup_list_id is null")
        # 存储数据库日志记录的数据库ID
        backup_log_id = self.get_key("backup_log_id", "multi")
        if len(backup_log_id) == 0:
            print("backup_log_id is null")
        # 两个数据库的对照表
        backup_list_map = self.get_key("backup_list_map", "multi")
        backup_log_map = self.get_key("backup_log_map", "multi")

        # 备份页面控制
        backup_handle = BackupInfo(
            _backup_info_token=backup_info_token,
            _backup_list_id=backup_list_id,
            _backup_log_id=backup_log_id,
            _backup_list_map=backup_list_map,
            _backup_log_map=backup_log_map
        )
        # 获取备份列表
        print("get backup list...")
        backup_list = backup_handle.get_backup_list()
        if len(backup_list) == 0:
            backup_handle.add_backup_log(status=True, log="没有需要备份的内容")
            print("没有需要备份的内容")
            return

        dump_log = ""
        success_back_list = []
        # 逐个解析需要备份的内容
        for backup in backup_list:
            item_id = backup["_page_id"]
            # 校验内容调用备份
            _page_id = backup[backup_list_map["page_id"]]
            _dump_type_str = backup[backup_list_map["page_type"]]
            _dump_type = NotionDump.DUMP_TYPE_PAGE
            if _dump_type_str == "Page":
                _dump_type = NotionDump.DUMP_TYPE_PAGE
            elif _dump_type_str == "Database":
                _dump_type = NotionDump.DUMP_TYPE_DB_TABLE
            else:
                print("unknown dump type " + _dump_type_str)
                if dump_log != "":
                    dump_log += "\n"
                dump_log += "id:" + _page_id + " unknown dump type " + _dump_type_str
                continue
            _export_child = False
            if backup[backup_list_map["export_child_page"]] == "true":
                _export_child = True
            _dump_path = SEVER_ABS_PATH + backup[backup_list_map["dump_path"]]

            # 配置错误按照默认处理
            _page_parser_type = NotionDump.PARSER_TYPE_MD
            if backup[backup_list_map["page_parser_type"]] == "Plain":
                _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
            _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
            if backup[backup_list_map["db_parser_type"]] == "Markdown":
                _db_parser_type = NotionDump.PARSER_TYPE_MD

            _db_insert_type = DB_INSERT_TYPE_PAGE
            _db_insert_type = DB_INSERT_TYPE_PAGE
            if "db_insert_type" in backup_list_map \
                    and backup_list_map["db_insert_type"] in backup \
                    and backup[backup_list_map["db_insert_type"]] == "Link":
                _db_insert_type = DB_INSERT_TYPE_LINK

            # 启动导出
            ret_status = self.dump_api.start_dump(
                token=dump_token,
                page_id=_page_id,
                dump_path=_dump_path,
                dump_type=_dump_type,
                export_child=_export_child,
                page_parser_type=_page_parser_type,
                db_parser_type=_db_parser_type,
                db_insert_type=_db_insert_type,
            )
            if dump_log != "":
                dump_log += "\n"
            if ret_status:
                success_back_list.append(item_id)
                dump_log += "id:" + _page_id + " backup success "
            else:
                dump_log += "id:" + _page_id + " backup fail "

        # 更新备份列表
        backup_handle.update_backup_list(success_back_list)

        # 新增备份日志
        if dump_log != "":
            dump_log += "\n"
        dump_log += "备份成功"
        print(dump_log)
        backup_handle.add_backup_log(status=True, log=dump_log)

    def start_dump_single(self):
        print("server version: " + VERSION + "(s)\n")
        # 获取必要的配置
        _token = self.get_key("backup_token", "single")
        _page_id = self.get_key("page_id", "single")
        _dump_type_str = self.get_key("page_type", "single")
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
        _export_child = self.get_key("export_child_page", "single")
        _dump_path = SEVER_ABS_PATH + self.get_key("dump_path", "single")

        # 配置错误按照默认处理
        _page_parser_type = NotionDump.PARSER_TYPE_MD
        if self.get_key("page_parser_type", "single") == "plain":
            _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
        _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
        if self.get_key("db_parser_type", "single") == "md":
            _db_parser_type = NotionDump.PARSER_TYPE_MD

        _db_insert_type = DB_INSERT_TYPE_PAGE
        if self.get_key("db_insert_type", "single") is not None and self.get_key("db_insert_type", "single") == "link":
            _db_insert_type = DB_INSERT_TYPE_LINK

        # 开始导出
        print("start export")
        self.dump_api.start_dump(
            token=_token,
            page_id=_page_id,
            dump_path=_dump_path,
            dump_type=_dump_type,
            export_child=_export_child,
            page_parser_type=_page_parser_type,
            db_parser_type=_db_parser_type,
            db_insert_type=_db_insert_type,
        )
