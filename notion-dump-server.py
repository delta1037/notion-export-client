import json
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi
from api.backup_info import BackupInfo

CONFIG_FILE_NAME = "./config_multi.json"


class Config:
    def __init__(self):
        self.config = None
        self.__read_config()

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


if __name__ == '__main__':
    config = Config()
    if not config.check_config():
        print("Config init failed, file:" + CONFIG_FILE_NAME)
        exit(-1)

    # 获取一些必要的配置
    # 备份信息页面的token
    backup_info_token = config.get_key("backup_info_token")
    if len(backup_info_token) == 0:
        print("backup_info_token is null")
    # 存储需要备份的内容的数据库id
    backup_list_id = config.get_key("backup_list_id")
    if len(backup_list_id) == 0:
        print("backup_list_id is null")
    # 存储数据库日志记录的数据库ID
    backup_log_id = config.get_key("backup_log_id")
    if len(backup_log_id) == 0:
        print("backup_log_id is null")
    # 备份内容需要的token
    dump_token = config.get_key("dump_token")
    if len(dump_token) == 0:
        print("dump_token is null")
    # 两个数据库的对照表
    backup_list_map = config.get_key("backup_list_map")
    backup_log_map = config.get_key("backup_log_map")

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
        exit(0)

    dump_log = ""
    # dump api
    dump_api = NotionDumpApi()
    # 逐个解析需要备份的内容
    for backup in backup_list:
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
            dump_log += "unknown dump type " + _dump_type_str
            continue
        _export_child = False
        if backup[backup_list_map["export_child_page"]] == "true":
            _export_child = True
        _dump_path = backup[backup_list_map["dump_path"]]

        # 配置错误按照默认处理
        _page_parser_type = NotionDump.PARSER_TYPE_MD
        if backup[backup_list_map["page_parser_type"]] == "Plain":
            _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
        _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
        if backup[backup_list_map["db_parser_type"]] == "Markdown":
            _db_parser_type = NotionDump.PARSER_TYPE_MD

        # 启动导出
        dump_api.start_dump(
            token=dump_token,
            page_id=_page_id,
            dump_path=_dump_path,
            dump_type=_dump_type,
            export_child=_export_child,
            page_parser_type=_page_parser_type,
            db_parser_type=_db_parser_type)

    # 更新备份列表
    backup_handle.update_backup_list()

    # 新增备份日志
    if dump_log != "":
        dump_log += "\n"
    dump_log += "备份成功"
    print(dump_log)
    backup_handle.add_backup_log(status=True, log=dump_log)
