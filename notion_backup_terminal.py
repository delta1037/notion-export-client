# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com
# 终端-打包代码 pyinstaller -F -c -i notion-dump.ico notion_backup_terminal.py -p api/notion_dump.py -p api/notion_dump_api.py -p api/backup_info.py
# 终端-打包代码 pyinstaller notion_backup_terminal.spec
# 后台-打包代码 pyinstaller -F -i notion-dump.ico notion_backup_terminal.py -p api/notion_dump.py -p api/notion_dump_api.py -p api/backup_info.py
# 后台-打包代码 pyinstaller notion_backup_background.spec
import os
import sys
import time

from NotionDump import NotionBackupLogger

from api.notion_dump import NotionBackup

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
LOG_FILE = SEVER_ABS_PATH + "/dump.log"


class Logger(NotionBackupLogger):
    def __init__(self):
        super().__init__()
        self.terminal = sys.stdout
        self.__log = open(LOG_FILE, "a+", encoding='utf-8')
        # 输出备份的时间
        backup_time = time.strftime('backup_time: %Y-%m-%d %H:%M:%S\n', time.localtime(time.time()))
        if self.terminal is not None:
            self.terminal.write(backup_time)
        self.__log.write("\n###################################################\n")
        self.__log.write(backup_time)
        self.__log.flush()

    def log_debug(self, log_str):
        self.log_info(log_str)

    def log_info(self, message):
        self.log("[EXPORT KERNEL] " + str(message))

    def log(self, message):
        if self.terminal is not None:
            self.terminal.write(message + "\n")
        self.__log.write(message + "\n")
        self.__log.flush()

    def flush(self):
        pass


if __name__ == '__main__':
    notion_back = NotionBackup(logger=Logger())
    # 开始备份
    notion_back.start_dump()
