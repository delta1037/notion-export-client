# author: delta1037
# Date: 2022/02/10
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -w -i notion-dump.ico notion_dump_client_multi.py -p api/notion_dump_api.py -p api/backup_info.py
import json
import sys
import tkinter
from tkinter import *
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi, DB_INSERT_TYPE_PAGE, DB_INSERT_TYPE_LINK
from api.backup_info import BackupInfo

CONFIG_FILE_NAME = "./config_multi.json"
VERSION = "1.0(m)"


class NotionBackupGUI:
    def __init__(self, init_window):
        # GUI
        self.init_window = init_window

        # 输出重定向
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        sys.stdout = self
        sys.stderr = self

        # 日志
        self.log_text = None
        self.log_label = None
        # 开始按钮
        self.start_button = None

        # 配置获取
        self.config = None

        # dump api
        self.dump_api = None

    def restore_std(self):
        sys.stdout = self.stdout_bak
        sys.stderr = self.stderr_bak

    # 设置窗口
    def set_init_window(self):
        self.init_window.title("Notion多页面导出_v" + VERSION)  # 窗口名
        # 日志
        row_index = 0
        self.log_label = Label(self.init_window, text="日志:")
        self.log_label.grid(row=row_index, sticky=tkinter.E)
        self.log_text = Text(self.init_window)
        self.log_text.grid(row=row_index, column=1, padx=10, pady=10, sticky=tkinter.E + tkinter.W)
        # 开始按钮 测试按钮
        row_index += 1
        self.start_button = Button(self.init_window, text="开始", bg="lightblue", width=10,
                                   command=self.start_button_process)  # 调用内部方法  加()为直接调用
        self.start_button.grid(row=row_index, column=1, pady=10, padx=100)

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
        with open('dump.log', 'a+', encoding='utf-8') as f:
            f.write(log_msg)
        f.close()

        log_msg_in = str(log_msg)
        self.log_text.insert(END, log_msg_in)
        self.log_text.update()
        self.log_text.see(END)

    def start_button_process(self):
        self.start_button["state"] = "disabled"
        self.log_text.delete('1.0', 'end')
        # 读取配置
        self.__read_config()
        self.write("client version: " + VERSION)

        # 从配置获取输入值
        if not self.check_config():
            print("Config init failed, file:" + CONFIG_FILE_NAME)
            # 恢复按钮状态
            self.start_button["state"] = "normal"
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
            self.start_button["state"] = "normal"
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
            _dump_path = backup[backup_list_map["dump_path"]]

            # 配置错误按照默认处理
            _page_parser_type = NotionDump.PARSER_TYPE_MD
            if backup[backup_list_map["page_parser_type"]] == "Plain":
                _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
            _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
            if backup[backup_list_map["db_parser_type"]] == "Markdown":
                _db_parser_type = NotionDump.PARSER_TYPE_MD

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

        # 恢复按钮状态
        self.start_button["state"] = "normal"


if __name__ == '__main__':
    # 实例化出一个父窗口
    _init_window = Tk()
    notion_back = NotionBackupGUI(_init_window)
    # 设置根窗口默认属性
    notion_back.set_init_window()

    # 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    _init_window.mainloop()

    # 恢复输出重定向
    notion_back.restore_std()
