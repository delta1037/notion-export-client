# author: delta1037
# Date: 2022/01/08
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -w -i notion-dump.ico notion-dump.py

import copy
import json
import logging
import os
import shutil
import sys
import tkinter
from json import JSONDecodeError

import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

from tkinter import *
import time

TOKEN_TEST = "secret_WRLJ9xyEawNxzRhVHVWfciTl9FAyNCd29GMUvr2hQD4"
PAGE_MIX_ID = "950e57e0507b4448a55a13b2f47f031f"
DB_ID = "3b40cf6b60fc49edbe25740dd9a74af7"

# 子目录的定制
CHILD_PAGES_PATH = "./child_pages/"
DATABASE_PATH = "./databases/"
# 导出根目录默认是当前目录
CONFIG_FILE_NAME = "./config.json"
LOG_DEBUG = 1
LOG_INFO = 2


class NotionBackupGUI:
    def __init__(self, init_window):
        # GUI
        self.init_window = init_window
        # 日志
        self.log_text = None
        self.log_label = None
        # 开始按钮
        self.start_button = None
        # 测试按钮
        self.test_button = None

        # 变量部分
        self.token = None
        self.page_id = None
        self.dump_type = None
        self.export_child = None
        self.dump_path = None
        self.page_parser_type = NotionDump.PARSER_TYPE_MD
        self.db_parser_type = NotionDump.PARSER_TYPE_PLAIN

        # 配置获取
        self.config = None

        # 输出重定向
        self.stdout_bak = sys.stdout
        self.stderr_bak = sys.stderr
        sys.stdout = self
        sys.stderr = self

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
        self.start_button.grid(row=row_index, column=1, pady=10, padx=100, sticky=tkinter.E)
        self.test_button = Button(self.init_window, text="测试", bg="lightblue", width=10,
                                  command=self.test_button_process)  # 调用内部方法  加()为直接调用
        self.test_button.grid(row=row_index, column=1, pady=10, padx=100, sticky=tkinter.W)

    def get_key(self, key):
        return self.config.get(key)

    def _read_config(self):
        try:
            with open(CONFIG_FILE_NAME, encoding="utf-8") as conf_file_handle:
                self.config = json.load(conf_file_handle)
        except FileNotFoundError:
            self.debug_log("Configuration file does not exist", level=LOG_INFO)
        except JSONDecodeError:
            self.debug_log("Configuration file is corrupted", level=LOG_INFO)

    def restore_std(self):
        sys.stdout = self.stdout_bak
        sys.stderr = self.stderr_bak

    def start_button_process(self):
        self.test_button["state"] = "disabled"
        self.log_text.delete('1.0', 'end')
        # 从配置获取输入值
        self._read_config()
        if self.config is None:
            self.debug_log("Config read failed", level=LOG_INFO)
            return
        self.token = self.get_key("token")
        self.page_id = self.get_key("page_id")
        type_str = self.get_key("page_type")
        if type_str == "page":
            self.dump_type = NotionDump.DUMP_TYPE_PAGE
        elif type_str == "database":
            self.dump_type = NotionDump.DUMP_TYPE_DB_TABLE
        elif type_str == "block":
            self.dump_type = NotionDump.DUMP_TYPE_BLOCK
        else:
            self.debug_log("unknown type " + type_str)
            return
        self.export_child = self.get_key("export_child_page")
        self.dump_path = self.get_key("dump_path") + "/"

        # 配置错误按照默认处理
        if self.get_key("page_parser_type") == "plain":
            self.page_parser_type = NotionDump.PARSER_TYPE_PLAIN
        if self.get_key("db_parser_type") == "md":
            self.page_parser_type = NotionDump.PARSER_TYPE_MD

        self.show_param()
        self.start_export()
        self.test_button["state"] = "normal"

    def test_button_process(self):
        self.test_button["state"] = "disabled"
        self.log_text.delete('1.0', 'end')
        self.token = TOKEN_TEST
        self.page_id = PAGE_MIX_ID
        self.dump_type = NotionDump.DUMP_TYPE_PAGE
        self.export_child = True
        self.dump_path = "./dumped_file/"

        self.show_param()
        self.start_export()
        self.test_button["state"] = "normal"

    def show_param(self):
        self.debug_log("  token:" + self.token, level=LOG_INFO)
        self.debug_log("page_id:" + self.page_id)
        type_str = "unknown"
        if self.dump_type == NotionDump.DUMP_TYPE_PAGE:
            type_str = "DUMP_TYPE_PAGE"
        elif self.dump_type == NotionDump.DUMP_TYPE_DB_TABLE:
            type_str = "DUMP_TYPE_DB_TABLE"
        elif self.dump_type == NotionDump.DUMP_TYPE_BLOCK:
            type_str = "DUMP_TYPE_BLOCK"
        self.debug_log("   type:" + type_str, level=LOG_INFO)
        self.debug_log("  recur:" + str(self.export_child), level=LOG_INFO)
        self.debug_log("   path:" + self.dump_path, level=LOG_INFO)
        page_parser_s = "md"
        if self.page_parser_type == NotionDump.PARSER_TYPE_PLAIN:
            page_parser_s = "plain"
        db_parser_s = "plain"
        if self.db_parser_type == NotionDump.PARSER_TYPE_MD:
            db_parser_s = "plain"
        self.debug_log("page_parser:" + page_parser_s, level=LOG_INFO)
        self.debug_log("  db_parser:" + db_parser_s, level=LOG_INFO)

    def start_export(self):
        query_handle = NotionQuery(token=self.token)
        if query_handle is None:
            self.debug_log("query handle init error, check your token", level=LOG_INFO)
            return
        self.debug_log("notion query handle init success", level=LOG_INFO)
        page_handle = Dump(
            dump_id=self.page_id,
            query_handle=query_handle,
            export_child_pages=self.export_child,
            dump_type=self.dump_type
        )
        # 将解析内容存储到文件中；返回内容存储为json文件
        self.debug_log("start dump to file ..., it may take a long time if you page is too big", level=LOG_INFO)
        page_detail_json = page_handle.dump_to_file()
        json_name = ".tmp/page_parser_result.json"
        common_op.save_json_to_file(handle=page_detail_json, json_name=json_name)
        self.debug_log("page dump success, file info save at " + json_name, level=LOG_INFO)
        # 生成文件目录
        self.gen_dir()
        main_page_list = [self.page_id]

        # 利用一下json里的page_recursion变量
        for p_id in page_detail_json:
            page_detail_json[p_id]["page_recursion"] = False
        self.debug_log("start relocate link in file...", level=LOG_INFO)
        self.relocate_child_page(page_detail_json, main_page_list, is_main=True)
        self.debug_log("file link relocate success, check path :" + self.dump_path, level=LOG_INFO)

    # 获取当前时间
    @staticmethod
    def get_current_time():
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        return current_time

    # 日志动态打印
    def debug_log(self, debug_str, level=LOG_DEBUG):
        # if level == LOG_INFO:
        self.write(debug_str)

        with open('dump.log', 'a+', encoding='utf-8') as f:
            f.write(debug_str + "\n")
        f.close()

    def write(self, log_msg):
        current_time = self.get_current_time()
        log_msg_in = str(current_time) + " " + str(log_msg) + "\n"  # 换行
        self.log_text.insert(END, log_msg_in)
        self.log_text.update()
        self.log_text.see(END)

    # 创建文件目录
    def gen_dir(self):
        if not os.path.exists(self.dump_path):
            os.mkdir(self.dump_path)

        CHILD_PATH = self.dump_path + CHILD_PAGES_PATH
        if not os.path.exists(CHILD_PATH):
            os.mkdir(CHILD_PATH)

        DB_PATH = self.dump_path + DATABASE_PATH
        if not os.path.exists(DB_PATH):
            os.mkdir(DB_PATH)

    @staticmethod
    def add_page_file_suffix(page_type, page_name):
        if page_type == "page":
            page_name += ".md"
        elif page_type == "database":
            page_name += ".csv"
        else:
            logging.exception("unknown page type, use none")
        return page_name

    def relocate_link(self, file_name, src_str, des_str):
        self.debug_log("@ in file:" + file_name + " " + src_str + " -> " + des_str, level=LOG_INFO)
        file = open(file_name, 'r', encoding='utf-8')
        all_lines = file.readlines()
        file.close()

        file = open(file_name, 'w+', encoding='utf-8')
        for line in all_lines:
            line = line.replace(src_str, des_str)
            file.writelines(line)
        file.close()

    def find_dump_path(self, pages_handle, page_id):
        if page_id not in pages_handle:
            return ""
        if pages_handle[page_id]["link_id"] != "":
            return self.find_dump_path(pages_handle, pages_handle[page_id]["link_id"])
        else:
            return pages_handle[page_id]["local_path"]

    def find_true_id(self, pages_handle, page_id):
        if pages_handle[page_id]["link_id"] != "":
            return self.find_true_id(pages_handle, pages_handle[page_id]["link_id"])
        else:
            return page_id

    # 获取页面的链接 [页面名称](页面链接)  页面dump路径 页面系统路径
    def get_child_info(self, pages_handle, child_info, child_id, root_main=False, root_type="page"):
        self.debug_log("> [START] get_child_info " + child_id)
        self.debug_log("> [START] root_main :" + str(root_main))
        self.debug_log("> [START] root_type :" + root_type)

        child_main = child_info["main_page"]

        # 获取页面名称
        # 链接页面会获取到链接名称，如果没有就用id做名称（一般链接不存在没有名称的情况）
        # 实际页面会获取到页面名，如果没有，主页面就用main_page,其它页面就用id
        child_name = child_info["page_name"]
        if child_name == "":
            # 是主页而不是主页过来的链接才起个主页名；否则用id做名字
            if root_main and not common_op.is_link_page(child_id, pages_handle[child_id]):
                child_name = "main_page"
            else:
                child_name = child_id

        # 如果子页面是一个链接类型
        # 页面名称 用链接的名称
        # 页面位置 用实际的
        # dump路径 用实际的
        # TODO 系统路径 （所以对于链接类型应该拷贝到哪？ 即 如何确定一个系统路径）
        if common_op.is_link_page(child_id, pages_handle[child_id]):
            self.debug_log("> page id:" + child_id + " is link page, get true page")
            self.debug_log("> link id:" + child_info["link_id"])
            # 向真正的页面传递
            l_name, l_link, l_dump_path, l_os_path = \
                self.get_child_info(
                    pages_handle=pages_handle,
                    child_info=pages_handle[child_info["link_id"]],
                    child_id=child_info["link_id"],
                    root_main=root_main,
                    root_type=root_type
                )
            return child_name, l_link, l_dump_path, l_os_path

        # 到了这之后可以认为都是子页面（非链接）
        # 获取页面后缀
        page_name_suffix = copy.deepcopy(child_name)
        page_name_suffix = self.add_page_file_suffix(child_info["type"], page_name_suffix)
        # 获取页面链接
        child_link = ""
        if root_main and child_main:
            # 主页里面包含了自己（这里是主页里面有链接是自己）
            child_link = "./" + page_name_suffix
        elif root_main and not child_main:
            # 主页中的子页面，重定位链接
            if root_type == "page" and child_info["type"] == "page":
                child_link = "./" + CHILD_PAGES_PATH + page_name_suffix
            elif root_type == "page" and child_info["type"] == "database":
                # 主页面嵌套数据库
                child_link = "./" + DATABASE_PATH + page_name_suffix
            elif root_type == "database" and child_info["type"] == "page":
                # 数据库中的子页面
                child_link = "./" + CHILD_PAGES_PATH + page_name_suffix
            else:
                # 数据库不能嵌套数据库
                self.debug_log("there may be a error")
        elif not root_main and child_main:
            # 子页面中调用了主页面
            child_link = "../" + page_name_suffix
        else:
            if root_type == "page" and child_info["type"] == "page":
                # 子页面中的子页面
                child_link = "./" + page_name_suffix
            elif root_type == "page" and child_info["type"] == "database":
                # 子页面嵌套数据库
                child_link = "../" + DATABASE_PATH + page_name_suffix
            elif root_type == "database" and child_info["type"] == "page":
                # 数据库中的子页面
                child_link = "../" + CHILD_PAGES_PATH + page_name_suffix
            else:
                # 数据库不能嵌套数据库
                self.debug_log("there may be a error")

        # 获取系统路径
        if root_main and child_main:  # child_info["main_page"]
            page_os_path = self.dump_path + page_name_suffix
        else:
            if child_info["type"] == "page":
                page_os_path = self.dump_path + CHILD_PAGES_PATH + page_name_suffix
            else:
                page_os_path = self.dump_path + DATABASE_PATH + page_name_suffix
        # 判断系统路径合法性
        if os.path.exists(page_os_path):
            self.debug_log("> page " + page_os_path + " exist in local, dont need copy")
            page_os_path = ""

        self.debug_log("> [END] get_child_info page id " + child_id)
        self.debug_log("> [END] get_child_info child_name :" + child_name)
        self.debug_log("> [END] get_child_info child_link :" + child_link)
        self.debug_log("> [END] get_child_info local_path :" + child_info["local_path"])
        self.debug_log("> [END] get_child_info os_path :" + page_os_path)
        return child_name, child_link, child_info["local_path"], page_os_path

    # 获取主页信息（导出的系统路径）
    def get_root_info(self, page_info, page_id):
        self.debug_log("= [START] get_root_info " + page_id + " param info:")
        self.debug_log("= [START] root_main :" + str(page_info["main_page"]))
        # 获取页面名称
        page_name = page_info["page_name"]
        if page_name == "":
            if page_info["main_page"]:
                page_name = "main_page"
            else:
                page_name = page_id

        # 给页面加个后缀
        page_name_suffix = copy.deepcopy(page_name)
        page_name_suffix = self.add_page_file_suffix(page_info["type"], page_name_suffix)

        # 获取系统路径
        if page_info["main_page"]:
            page_os_path = self.dump_path + page_name_suffix
        else:
            if page_info["type"] == "page":
                page_os_path = self.dump_path + CHILD_PAGES_PATH + page_name_suffix
            else:
                page_os_path = self.dump_path + DATABASE_PATH + page_name_suffix
        self.debug_log("= [END] get_root_info page_id " + page_id)
        self.debug_log("= [END] get_root_info page_os_path :" + page_os_path)
        return page_os_path

    # 该操作需要递归进行
    # 传入一个下载好的文件相关信息，需要操作的列表，重定位新路径默认是当前路径
    def relocate_child_page(self, pages_handle, page_list, is_main=False):
        for page_id in page_list:
            # 设置标志位，防止嵌套页面死循环（或者在处理链接死循环）
            if pages_handle[page_id]["page_recursion"]:
                continue
            pages_handle[page_id]["page_recursion"] = True

            # 要不要最后再处理 没有处理到的页面
            # 区分链接页面和非链接页面,link_id是链接页面ID,page_id是实际页面ID
            if common_op.is_link_page(page_id, pages_handle[page_id]):
                true_id = self.find_true_id(pages_handle, page_id)
                print("% relocate_child_page page id is:" + page_id)
                print("% relocate_child_page true_id is:" + true_id)
                self.relocate_child_page(
                    pages_handle=pages_handle,
                    page_list=[true_id],
                    is_main=pages_handle[true_id]["main_page"]
                )
                # 链接类型处理完这正的页面就返回
                continue

            # 能走到这说明下面的都是实际链接
            # page_info是一个实际子页面
            page_info = pages_handle[page_id]
            # 判断实际页面是否成功导出
            if not page_info["dumped"]:
                self.debug_log("% page:" + page_id + " not export success", level=LOG_INFO)
                return False

            # 链接页面校准
            if page_info["main_page"] != is_main:
                self.debug_log("% page:" + page_id + " page attribute main_page conflict", level=LOG_INFO)
                return False
            # 根路径是不是主页，如果链接到主页面那么程序不会到这里的，前面已经置flag了
            root_page_main = page_info["main_page"]
            self.debug_log("% page id " + page_id + " main page flag " + str(root_page_main))

            # 获取主页的系统路径（根据导出位置计算） # 拷贝dump的文件到导出位置
            root_os_path = self.get_root_info(page_info=page_info, page_id=page_id)
            if not os.path.exists(root_os_path):
                shutil.copyfile(page_info["local_path"], root_os_path)
            else:
                self.debug_log("file " + root_os_path + " is exist ???")

            # 对数据库类型生成同路径md辅助文件
            root_md = None
            if page_info["type"] == "database":
                # 数据库类型，生成同路径md文件，辅助做数据库中的链接定位
                root_md_name = root_os_path[0:root_os_path.rfind(".")] + ".md"
                root_md = open(root_md_name, "w+", encoding="utf-8")

            # 开始处理该页面下的所有链接，并将主页中的内容重定位
            # 获取到所有的子页面id 将主页中的子页面进行重定位，获取实际链接
            for child_id in page_info["child_pages"]:
                # 计算子页面名称和链接
                child_name, child_link, child_dump_path, child_os_path = \
                    self.get_child_info(
                        pages_handle=pages_handle,
                        child_info=pages_handle[child_id],
                        child_id=child_id,
                        root_main=page_info["main_page"],
                        root_type=page_info["type"]
                    )
                # 文件没有下载
                if child_dump_path == "":
                    self.debug_log("% relocate_child_page page " + child_id + " not dump success")
                    continue
                if child_os_path != "":
                    shutil.copyfile(child_dump_path, child_os_path)
                    self.debug_log("% relocate_child_page copy " + child_dump_path + " to " + child_os_path, level=LOG_INFO)

                # 重定位主页中的链接
                src_link = "[" + child_id + "]()"
                des_link = "[" + child_name + "](" + child_link + ")"
                self.relocate_link(root_os_path, src_link, des_link)

                # 写入数据库辅助定位信息
                if root_md is not None:
                    root_md.write(des_link + "\n\n")

            if root_md is not None:
                root_md.close()

            # 递归处理子页面,链接页面不会递归
            self.relocate_child_page(pages_handle, page_info["child_pages"])
        return True


def gui_start():
    # 实例化出一个父窗口
    init_window = Tk()
    notion_back = NotionBackupGUI(init_window)
    # 设置根窗口默认属性
    notion_back.set_init_window()
    # 父窗口进入事件循环，可以理解为保持窗口运行，否则界面不展示
    init_window.mainloop()

    notion_back.restore_std()


if __name__ == '__main__':
    gui_start()
