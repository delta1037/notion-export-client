import json
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi

CONFIG_FILE_NAME = "./config.json"


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
    _token = config.get_key("token")
    _page_id = config.get_key("page_id")
    _dump_type_str = config.get_key("page_type")
    _dump_type = NotionDump.DUMP_TYPE_PAGE
    if _dump_type_str == "page":
        _dump_type = NotionDump.DUMP_TYPE_PAGE
    elif _dump_type_str == "database":
        _dump_type = NotionDump.DUMP_TYPE_DB_TABLE
    elif _dump_type_str == "block":
        _dump_type = NotionDump.DUMP_TYPE_BLOCK
    else:
        print("unknown type " + _dump_type_str)
        exit(-1)
    _export_child = config.get_key("export_child_page")
    _dump_path = config.get_key("dump_path")

    # 配置错误按照默认处理
    _page_parser_type = NotionDump.PARSER_TYPE_MD
    if config.get_key("page_parser_type") == "plain":
        _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
    _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
    if config.get_key("db_parser_type") == "md":
        _db_parser_type = NotionDump.PARSER_TYPE_MD

    # 初始化 API
    dump_api = NotionDumpApi(
        token=_token,
        page_id=_page_id,
        dump_path=_dump_path,
        dump_type=_dump_type,
        export_child=_export_child,
        page_parser_type=_page_parser_type,
        db_parser_type=_db_parser_type
    )

    # 开始导出
    dump_api.start_dump()
