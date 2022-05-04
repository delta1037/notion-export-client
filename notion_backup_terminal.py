# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -c -i notion-dump.ico notion_backup_terminal.py -p api/notion_dump.py -p api/notion_dump_api.py -p api/backup_info.py
import os
import sys
import time

from api.notion_dump import NotionBackup

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
LOG_FILE = SEVER_ABS_PATH + "/dump.log"


class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(LOG_FILE, "a+", encoding='utf-8')
        # 输出备份的时间
        backup_time = time.strftime('backup_time: %Y-%m-%d %H:%M:%S\n', time.localtime(time.time()))
        self.terminal.write(backup_time)
        self.log.write("\n###################################################\n")
        self.log.write(backup_time)
        self.log.flush()

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        pass


if __name__ == '__main__':
    notion_back = NotionBackup(logger=Logger())
    # 开始备份
    notion_back.start_dump()
