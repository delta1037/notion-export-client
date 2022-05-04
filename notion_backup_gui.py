# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -w -i notion-dump.ico notion_backup_gui.py -p api/notion_dump.py -p api/notion_dump_api.py -p api/backup_info.py
import os
import sys
import time

from api.notion_dump import NotionBackup
import tkinter
from tkinter import *

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
LOG_FILE = SEVER_ABS_PATH + "/dump.log"


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

        # dump api
        self.notion_backup = NotionBackup(logger=self)
        # 日志文件句柄
        self.log = open(LOG_FILE, "a+", encoding='utf-8')
        # 输出备份的时间
        backup_time = time.strftime('backup_time: %Y-%m-%d %H:%M:%S\n', time.localtime(time.time()))
        self.log.write("\n###################################################\n")
        self.log.write(backup_time)
        self.log.flush()

    # 设置窗口
    def set_init_window(self):
        self.init_window.title("Notion页面备份")  # 窗口名
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

    def write(self, message):
        # 文件输出
        self.log.write(message)
        self.log.flush()

        # 窗口输出
        log_msg_in = str(message)
        self.log_text.insert(END, log_msg_in)
        self.log_text.update()
        self.log_text.see(END)

    def start_button_process(self):
        self.start_button["state"] = "disabled"
        self.log_text.delete('1.0', 'end')

        self.notion_backup.start_dump(force_auto=True)

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

