# author: delta1037
# Date: 2022/04/15
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -c -i notion-dump.ico notion_dump_server_multi.py -p api/notion_dump_api.py -p api/backup_info.py
import json
import os
import sys
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi, DB_INSERT_TYPE_PAGE, DB_INSERT_TYPE_LINK
from api.backup_info import BackupInfo

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
CONFIG_FILE_NAME = SEVER_ABS_PATH + "/config_multi.json"
LOG_FILE = SEVER_ABS_PATH + "/dump.log"
NotionDump.TMP_DIR = SEVER_ABS_PATH + NotionDump.TMP_DIR
VERSION = "1.0(m)"


class NotionBackup:
    def __init__(self):
        # 配置获取
        self.config = None

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
        except FileNotFoundError as e:
            self.write("\nConfiguration file does not exist\n")
            self.write(e)
        except JSONDecodeError as e:
            self.write("\nConfiguration file is corrupted\n")
            self.write(e)

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
        # 读取配置
        self.__read_config()
        self.write("server version: " + VERSION + "\n")

        # 从配置获取输入值
        if not self.check_config():
            print("Config init failed, file:" + CONFIG_FILE_NAME)
            return
        # 获取一些必要的配置
        # 备份信息页面的token
        backup_info_token = self.get_key("backup_info_token")
        if len(backup_info_token) == 0:
            print("backup_info_token is null")
        # 存储需要备份的内容的数据库id
        backup_list_id = self.get_key("backup_list_id")
        if len(backup_list_id) == 0:
            print("backup_list_id is null")
        # 存储数据库日志记录的数据库ID
        backup_log_id = self.get_key("backup_log_id")
        if len(backup_log_id) == 0:
            print("backup_log_id is null")
        # 备份内容需要的token
        dump_token = self.get_key("dump_token")
        if len(dump_token) == 0:
            print("dump_token is null")
        # 两个数据库的对照表
        backup_list_map = self.get_key("backup_list_map")
        backup_log_map = self.get_key("backup_log_map")

        # 备份页面控制
        backup_handle = BackupInfo(
            _backup_info_token=backup_info_token,
            _backup_list_id=backup_list_id,
            _backup_log_id=backup_log_id,
            _backup_list_map=backup_list_map,
            _backup_log_map=backup_log_map
        )
        # 获取备份列表
        backup_list = backup_handle.get_backup_list()
        if len(backup_list) == 0:
            backup_handle.add_backup_log(status=True, log="没有需要备份的内容")
            print("没有需要备份的内容")
            return

        dump_log = ""
        # dump api
        dump_api = NotionDumpApi()
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
            ret_status = dump_api.start_dump(
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


if __name__ == '__main__':
    notion_back = NotionBackup()
    notion_back.start_dump()

    # 恢复输出重定向
    notion_back.restore_std()
