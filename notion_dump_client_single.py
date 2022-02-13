# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -w -i notion-dump.ico notion_dump_client_single.py -p api/notion_dump_api.py
import json
import sys
import tkinter
from tkinter import *
from json import JSONDecodeError

import NotionDump
from api.notion_dump_api import NotionDumpApi

CONFIG_FILE_NAME = "./config.json"


class NotionBackupGUI:
    def __init__(self, init_window):
        # GUI
        self.init_window = init_window
        # 日志
        self.log_text = None
        self.log_label = None
        # 开始按钮
        self.start_button = None

        # 配置获取
        self.config = None
        self.__read_config()

        # dump api
        self.dump_api = None

        # 输出重定向
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        sys.stdout = self
        sys.stderr = self

    def restore_std(self):
        sys.stdout = self.stdout_bak
        sys.stderr = self.stderr_bak

    # 设置窗口
    def set_init_window(self):
        self.init_window.title("Notion自动备份_v0.1")  # 窗口名
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
        # 从配置获取输入值
        if not self.check_config():
            print("Config init failed, file:" + CONFIG_FILE_NAME)
            # 恢复按钮状态
            self.start_button["state"] = "normal"
            return
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
            # 恢复按钮状态
            self.start_button["state"] = "normal"
            return
        _export_child = self.get_key("export_child_page")
        _dump_path = self.get_key("dump_path")

        # 配置错误按照默认处理
        _page_parser_type = NotionDump.PARSER_TYPE_MD
        if self.get_key("page_parser_type") == "plain":
            _page_parser_type = NotionDump.PARSER_TYPE_PLAIN
        _db_parser_type = NotionDump.PARSER_TYPE_PLAIN
        if self.get_key("db_parser_type") == "md":
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
        print("start export")
        dump_api.start_dump()

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
