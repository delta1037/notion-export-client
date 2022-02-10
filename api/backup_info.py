import time
import datetime

from NotionDump.Notion.Notion import NotionQuery
from NotionDump.Dump.database import Database
from notion_client import Client


class BackupInfo:
    def __init__(self, _backup_info_token, _backup_list_id, _backup_log_id, _backup_list_map, _backup_log_map):
        self.__backup_info_token = _backup_info_token
        self.__backup_list_id = _backup_list_id
        self.__backup_log_id = _backup_log_id
        self.__backup_list_map = _backup_list_map
        self.__backup_log_map = _backup_log_map
        # 初始化notion操作handle
        self.db_handle = Database(database_id=self.__backup_list_id,
                                  query_handle=NotionQuery(token=self.__backup_info_token))
        self.notion = Client(auth=self.__backup_info_token)
        self.backup_id_list = []

    def add_backup_log(self, status=False, log="备份正常"):
        backup_status = "失败"
        if status is True:
            backup_status = "成功"

        backup_title = str(int(time.time()))
        # 备份历史中新增一条记录
        backup_log = {
            self.__backup_log_map["title"]: {
                "title": [
                    {
                        "type": "text",
                        "text": {
                            "content": backup_title
                        }
                    }
                ]
            },
            self.__backup_log_map["date"]: {
                "date": {
                    "start": datetime.datetime.now().isoformat(),
                    "time_zone": "Asia/Shanghai"
                }
            },
            self.__backup_log_map["status"]: {
                "select": {
                    "name": backup_status
                }
            },
            self.__backup_log_map["log"]: {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": log
                        }
                    }
                ]
            }
        }
        parent = {
            "type": "database_id",
            "database_id": self.__backup_log_id
        }
        self.notion.pages.create(parent=parent, properties=backup_log)

    def get_backup_list(self):
        # 获取操作列表
        for item_line in self.db_handle.dump_to_dic():
            if item_line[self.__backup_list_map["dump_status"]] == "true":
                self.backup_id_list.append(item_line)
        return self.backup_id_list

    def update_backup_list(self, id_list):
        properties = {self.__backup_list_map["dump_status"]: {"checkbox": False}}
        for _id in id_list:
            # 更新每一个页面的备份状态
            self.notion.pages.update(page_id=_id, properties=properties)

