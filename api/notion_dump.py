# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com
import os
import sys


from api.configuration import CONFIG_FILE_PATH, Configuration
from api.notion_dump_api import NotionDumpApi, DB_INSERT_TYPE_PAGE, DB_INSERT_TYPE_LINK
from api.backup_info import BackupInfo
import NotionDump

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
NotionDump.TMP_DIR = os.path.normpath(SEVER_ABS_PATH + "/buffer_file") + "/"
NotionDump.BUFFER_FILE = os.path.normpath(NotionDump.TMP_DIR + "/notion_download_buffer.json")

VERSION = "3.0.1"


class NotionBackup:
    def __init__(self, logger=None, config=None):
        # 配置获取
        if config is None:
            self.config = Configuration(CONFIG_FILE_PATH, self)
        else:
            self.config = config

            # dump api
        self.dump_api = None

        if logger is not None:
            NotionDump.LOGGER = logger
        self.logger = NotionDump.LOGGER

        self.backup_root = ""

    def log(self, msg):
        if self.logger is not None:
            self.logger.log("[EXPORT CLIENT] " + str(msg))
        else:
            print("[EXPORT CLIENT] " + str(msg))

    def start_dump(self, force_auto=False):
        self.log("log write to dump.log")
        self.log("start backup, it may take a long time ...")

        if not self.config.check():
            self.log("Config init failed")
            return

        # 开启DEBUG模式
        debug_mode = self.config.get_key("debug", None, default=False)
        if debug_mode is True:
            NotionDump.DUMP_MODE = NotionDump.DUMP_MODE_DEBUG
        else:
            NotionDump.DUMP_MODE = NotionDump.DUMP_MODE_DEFAULT
        # Page是否导出属性表的配置
        NotionDump.S_PAGE_PROPERTIES = self.config.get_key("page_properties", None, default=True)
        # 输出时间格式
        NotionDump.FORMAT_DATETIME = self.config.get_key("datetime_formate", None, default="%Y/%m/%d-%H:%M:%S")
        NotionDump.FORMAT_DATE = self.config.get_key("date_formate", None, default="%Y/%m/%d")
        # 主题格式
        NotionDump.S_THEME_TYPE = self.config.get_key("color_theme", None, default="default")
        if NotionDump.S_THEME_TYPE == "self_define":
            NotionDump.S_THEME_SELF_DEFINE = self.config.get_key("your_color_theme", None, default="default")
            if NotionDump.S_THEME_SELF_DEFINE == "default":
                NotionDump.S_THEME_TYPE = "default"
        # 是否下载所有链接文件
        NotionDump.FILE_WITH_LINK = self.config.get_key("file_with_link", None, default=False)
        # 是否启用缓存
        NotionDump.USE_BUFFER = self.config.get_key("use_buffer", None, default=True)

        self.dump_api = NotionDumpApi(debug=debug_mode, logger=self.logger)

        self.backup_root = self.config.get_key("backup_root_path", default="")
        # print(self.backup_root)
        if self.backup_root == "":
            self.backup_root = SEVER_ABS_PATH

        if self.config.get_key("*backup_type", None) == "single":
            self.start_dump_single()
        else:
            self.start_dump_multi()

        self.log("backup success ~ ")

        if not force_auto and self.config.get_key("auto_close", None) is False:
            # 终端停顿
            input()

    def start_dump_multi(self):
        self.log("server version: " + VERSION + "(m)\n")
        # 备份内容需要的token
        dump_token = self.config.get_key("*backup_token", "multi")
        if len(dump_token) == 0:
            self.log("dump_token is null")
        # 备份信息页面的token
        backup_info_token = self.config.get_key("*backup_info_token", "multi")
        if len(backup_info_token) == 0:
            self.log("backup_info_token is null")
        # 存储需要备份的内容的数据库id
        backup_list_id = self.config.get_key("*backup_list_id", "multi")
        if len(backup_list_id) == 0:
            self.log("backup_list_id is null")
        # 存储数据库日志记录的数据库ID
        backup_log_id = self.config.get_key("*backup_log_id", "multi")
        if len(backup_log_id) == 0:
            self.log("backup_log_id is null")
        # 两个数据库的对照表
        backup_list_map = self.config.get_key("backup_list_map", "multi")
        backup_log_map = self.config.get_key("backup_log_map", "multi")

        # 备份页面控制
        backup_handle = BackupInfo(
            _backup_info_token=backup_info_token,
            _backup_list_id=backup_list_id,
            _backup_log_id=backup_log_id,
            _backup_list_map=backup_list_map,
            _backup_log_map=backup_log_map
        )
        # 获取备份列表
        self.log("get backup list...")
        backup_list = backup_handle.get_backup_list()
        if len(backup_list) == 0:
            backup_handle.add_backup_log(status=True, log="没有需要备份的内容")
            self.log("没有需要备份的内容")
            return

        dump_status = True
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
                self.log("unknown dump type " + _dump_type_str)
                if dump_log != "":
                    dump_log += "\n"
                dump_log += "id:" + _page_id + " unknown dump type " + _dump_type_str
                continue
            _export_child = True
            _dump_path = os.path.normpath(self.backup_root + "/" + backup[backup_list_map["dump_path"]])

            # 配置错误按照默认处理
            _page_parser_type = NotionDump.PARSER_TYPE_MD
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
                dump_status = False

        # 更新备份列表
        auto_check_off = self.config.get_key("auto_check_off", "multi", default=True)
        if auto_check_off:
            backup_handle.update_backup_list(success_back_list)

        # 新增备份日志
        if dump_log != "":
            dump_log += "\n"
        if dump_status:
            dump_log += "备份成功"
        else:
            dump_log += "部分备份失败"
        self.log(dump_log)
        backup_handle.add_backup_log(status=dump_status, log=dump_log)

    def start_dump_single(self):
        self.log("server version: " + VERSION + "(s)\n")
        # 获取必要的配置
        _token = self.config.get_key("*backup_token", "single")
        _page_id = self.config.get_key("*page_id", "single")
        _dump_type_str = self.config.get_key("-page_type", "single")
        _dump_type = NotionDump.DUMP_TYPE_PAGE
        if _dump_type_str == "page":
            _dump_type = NotionDump.DUMP_TYPE_PAGE
        elif _dump_type_str == "database":
            _dump_type = NotionDump.DUMP_TYPE_DB_TABLE
        elif _dump_type_str == "block":
            _dump_type = NotionDump.DUMP_TYPE_BLOCK
        else:
            self.log("unknown type " + _dump_type_str)
            return
        _export_child = self.config.get_key("export_child_page", "single")
        _dump_path = os.path.normpath(self.backup_root + "/" + self.config.get_key("-dump_path", "single"))

        # 配置错误按照默认处理
        _page_parser_type = NotionDump.PARSER_TYPE_MD
        _db_parser_type = NotionDump.PARSER_TYPE_MD

        _db_insert_type = DB_INSERT_TYPE_PAGE
        if self.config.get_key("db_insert_type", "single") is not None and self.config.get_key("db_insert_type", "single") == "link":
            _db_insert_type = DB_INSERT_TYPE_LINK

        # 开始导出
        self.log("start export")
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
