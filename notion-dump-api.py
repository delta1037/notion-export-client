# author: delta1037
# Date: 2022/01/14
# mail:geniusrabbit@qq.com

import copy
import logging
import os
import shutil
import time
import json
from json import JSONDecodeError

import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

# 配置位置
CONFIG_FILE_NAME = "./config.json"
# 子目录的定制
CHILD_PAGES_PATH = "./child_pages/"
DATABASE_PATH = "./databases/"

# 日志等级
LOG_DEBUG = 1
LOG_INFO = 2


def show_log(debug_str, level=LOG_DEBUG):
    if level == LOG_INFO:
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        log_msg_in = str(current_time) + " " + str(debug_str)
        print(log_msg_in)

    with open('dump.log', 'a+', encoding='utf-8') as f:
        f.write(debug_str + "\n")
    f.close()


class NotionDumpApi:
    def __init__(
            self,
            token=None,
            page_id=None,
            dump_path="./dumped_file",
            dump_type=NotionDump.DUMP_TYPE_PAGE,
            export_child=False,
            page_parser_type=NotionDump.PARSER_TYPE_MD,
            db_parser_type=NotionDump.PARSER_TYPE_PLAIN
    ):

        self.__token = token
        self.__page_id = page_id
        self.__dump_path = dump_path + "/"

        self.__dump_type = dump_type
        self.__export_child = export_child

        self.__page_parser_type = page_parser_type
        self.__db_parser_type = db_parser_type

        self.__query_handle = self.__init_query_handle()

    def __init_query_handle(self):
        if self.__token is None:
            return None
        query_handle = NotionQuery(token=self.__token)
        if query_handle is None:
            show_log("query handle init error, check your token", level=LOG_INFO)
            return None
        show_log("notion query handle init success", level=LOG_INFO)
        return query_handle

    # 开始之前校验变量
    def __check_variable(self):
        if self.__query_handle is None:
            return False
        if self.__page_id is None:
            show_log("page_id is null", level=LOG_INFO)
            return False
        if self.__dump_path is None:
            show_log("dump_path is null", level=LOG_INFO)
            return False
        if self.__dump_type != NotionDump.DUMP_TYPE_PAGE:
            show_log("dump only support page now", level=LOG_INFO)
            return False
        if self.__export_child is not True or self.__export_child is not False:
            show_log("export_child type error", level=LOG_INFO)
            return False
        if self.__page_parser_type != NotionDump.PARSER_TYPE_MD or self.__page_parser_type != NotionDump.PARSER_TYPE_PLAIN:
            show_log("page_parser_type error", level=LOG_INFO)
            return False
        if self.__db_parser_type != NotionDump.PARSER_TYPE_MD or self.__db_parser_type != NotionDump.PARSER_TYPE_PLAIN:
            show_log("db_parser_type error", level=LOG_INFO)
            return False
        return True

    # 重设变量
    def reset_param(
            self,
            token=None,
            page_id=None,
            dump_path=None,
            dump_type=None,
            export_child=None,
            page_parser_type=None,
            db_parser_type=None
    ):
        if token is not None:
            self.__token = token
            self.__query_handle = self.__init_query_handle()
        if page_id is not None:
            self.__page_id = page_id
        if dump_path is not None:
            self.__dump_path = dump_path + "/"
        if dump_type is not None:
            self.__dump_type = dump_type
        if export_child is not None:
            self.__export_child = export_child
        if export_child is not None:
            self.__export_child = export_child
        if page_parser_type is not None:
            self.__page_parser_type = page_parser_type
        if page_id is not None:
            self.__db_parser_type = db_parser_type

    def start_dump(
            self,
            token=None,
            page_id=None,
            dump_path=None,
            dump_type=None,
            export_child=None,
            page_parser_type=None,
            db_parser_type=None
    ):
        self.reset_param(
            token=token,
            page_id=page_id,
            dump_path=dump_path,
            dump_type=dump_type,
            export_child=export_child,
            page_parser_type=page_parser_type,
            db_parser_type=db_parser_type,
        )
        # 导出前先显示参数
        self.show_param()
        if not self.__check_variable():
            show_log("param check fail, return")

        # 开始导出
        self.__start_export()

    def show_param(self):
        show_log("  token:" + self.__token, level=LOG_INFO)
        show_log("page_id:" + self.__page_id)
        type_str = "unknown"
        if self.__dump_type == NotionDump.DUMP_TYPE_PAGE:
            type_str = "DUMP_TYPE_PAGE"
        elif self.__dump_type == NotionDump.DUMP_TYPE_DB_TABLE:
            type_str = "DUMP_TYPE_DB_TABLE"
        elif self.__dump_type == NotionDump.DUMP_TYPE_BLOCK:
            type_str = "DUMP_TYPE_BLOCK"
        show_log("   type:" + type_str, level=LOG_INFO)
        show_log("  recur:" + str(self.__export_child), level=LOG_INFO)
        show_log("   path:" + self.__dump_path, level=LOG_INFO)
        page_parser_s = "md"
        if self.__page_parser_type == NotionDump.PARSER_TYPE_PLAIN:
            page_parser_s = "plain"
        db_parser_s = "plain"
        if self.__db_parser_type == NotionDump.PARSER_TYPE_MD:
            db_parser_s = "plain"
        show_log("page_parser:" + page_parser_s, level=LOG_INFO)
        show_log("  db_parser:" + db_parser_s, level=LOG_INFO)

    def __start_export(self):
        page_handle = Dump(
            dump_id=self.__page_id,
            query_handle=self.__query_handle,
            export_child_pages=self.__export_child,
            dump_type=self.__dump_type
        )
        # 将解析内容存储到文件中；返回内容存储为json文件
        show_log("start dump to file ..., it may take a long time if you page is too big", level=LOG_INFO)
        page_detail_json = page_handle.dump_to_file()
        json_name = ".tmp/page_parser_result.json"
        common_op.save_json_to_file(handle=page_detail_json, json_name=json_name)
        show_log("page dump success, file info save at " + json_name, level=LOG_INFO)
        # 生成文件目录
        self.__gen_dir()
        main_page_list = [self.__page_id]

        # 利用一下json里的page_recursion变量
        for p_id in page_detail_json:
            page_detail_json[p_id]["page_recursion"] = False
        show_log("start relocate link in file...", level=LOG_INFO)
        self.__relocate_child_page(page_detail_json, main_page_list, is_main=True)
        show_log("file link relocate success, check path :" + self.__dump_path, level=LOG_INFO)

    # 创建文件目录
    def __gen_dir(self):
        if not os.path.exists(self.__dump_path):
            os.mkdir(self.__dump_path)

        CHILD_PATH = self.__dump_path + CHILD_PAGES_PATH
        if not os.path.exists(CHILD_PATH):
            os.mkdir(CHILD_PATH)

        DB_PATH = self.__dump_path + DATABASE_PATH
        if not os.path.exists(DB_PATH):
            os.mkdir(DB_PATH)

    @staticmethod
    def __add_page_file_suffix(page_type, page_name):
        if page_type == "page":
            page_name += ".md"
        elif page_type == "database":
            page_name += ".csv"
        else:
            logging.exception("unknown page type, use none")
        return page_name

    @staticmethod
    def __relocate_link(file_name, src_str, des_str):
        show_log("@ in file:" + file_name + " " + src_str + " -> " + des_str, level=LOG_INFO)
        file = open(file_name, 'r', encoding='utf-8')
        all_lines = file.readlines()
        file.close()

        file = open(file_name, 'w+', encoding='utf-8')
        for line in all_lines:
            line = line.replace(src_str, des_str)
            file.writelines(line)
        file.close()

    def __find_true_id(self, pages_handle, page_id):
        if pages_handle[page_id]["link_id"] != "":
            return self.__find_true_id(pages_handle, pages_handle[page_id]["link_id"])
        else:
            return page_id

    # 获取页面的链接 [页面名称](页面链接)  页面dump路径 页面系统路径
    def __get_child_info(self, pages_handle, child_info, child_id, root_main=False, root_type="page"):
        show_log("> [START] __get_child_info " + child_id)
        show_log("> [START] root_main :" + str(root_main))
        show_log("> [START] root_type :" + root_type)

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
        if common_op.is_link_page(child_id, pages_handle[child_id]):
            show_log("> page id:" + child_id + " is link page, get true page")
            show_log("> link id:" + child_info["link_id"])
            # 向真正的页面传递
            l_name, l_link, l_dump_path, l_os_path = \
                self.__get_child_info(
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
        page_name_suffix = self.__add_page_file_suffix(child_info["type"], page_name_suffix)
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
                show_log("there may be a error")
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
                show_log("there may be a error")

        # 获取系统路径
        if root_main and child_main:  # child_info["main_page"]
            page_os_path = self.__dump_path + page_name_suffix
        else:
            if child_info["type"] == "page":
                page_os_path = self.__dump_path + CHILD_PAGES_PATH + page_name_suffix
            else:
                page_os_path = self.__dump_path + DATABASE_PATH + page_name_suffix
        # 判断系统路径合法性
        if os.path.exists(page_os_path):
            show_log("> page " + page_os_path + " exist in local, dont need copy")
            page_os_path = ""

        show_log("> [END] __get_child_info page id " + child_id)
        show_log("> [END] __get_child_info child_name :" + child_name)
        show_log("> [END] __get_child_info child_link :" + child_link)
        show_log("> [END] __get_child_info local_path :" + child_info["local_path"])
        show_log("> [END] __get_child_info os_path :" + page_os_path)
        return child_name, child_link, child_info["local_path"], page_os_path

    # 获取主页信息（导出的系统路径）
    def __get_root_info(self, page_info, page_id):
        show_log("= [START] __get_root_info " + page_id + " param info:")
        show_log("= [START] root_main :" + str(page_info["main_page"]))
        # 获取页面名称
        page_name = page_info["page_name"]
        if page_name == "":
            if page_info["main_page"]:
                page_name = "main_page"
            else:
                page_name = page_id

        # 给页面加个后缀
        page_name_suffix = copy.deepcopy(page_name)
        page_name_suffix = self.__add_page_file_suffix(page_info["type"], page_name_suffix)

        # 获取系统路径
        if page_info["main_page"]:
            page_os_path = self.__dump_path + page_name_suffix
        else:
            if page_info["type"] == "page":
                page_os_path = self.__dump_path + CHILD_PAGES_PATH + page_name_suffix
            else:
                page_os_path = self.__dump_path + DATABASE_PATH + page_name_suffix
        show_log("= [END] __get_root_info page_id " + page_id)
        show_log("= [END] __get_root_info page_os_path :" + page_os_path)
        return page_os_path

    # 该操作需要递归进行
    # 传入一个下载好的文件相关信息，需要操作的列表，重定位新路径默认是当前路径
    def __relocate_child_page(self, pages_handle, page_list, is_main=False):
        for page_id in page_list:
            # 设置标志位，防止嵌套页面死循环（或者在处理链接死循环）
            if pages_handle[page_id]["page_recursion"]:
                continue
            pages_handle[page_id]["page_recursion"] = True

            # 要不要最后再处理 没有处理到的页面
            # 区分链接页面和非链接页面,link_id是链接页面ID,page_id是实际页面ID
            if common_op.is_link_page(page_id, pages_handle[page_id]):
                true_id = self.__find_true_id(pages_handle, page_id)
                print("% __relocate_child_page page id is:" + page_id)
                print("% __relocate_child_page true_id is:" + true_id)
                self.__relocate_child_page(
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
                show_log("% page:" + page_id + " not export success", level=LOG_INFO)
                return False

            # 链接页面校准
            if page_info["main_page"] != is_main:
                show_log("% page:" + page_id + " page attribute main_page conflict", level=LOG_INFO)
                return False
            # 根路径是不是主页，如果链接到主页面那么程序不会到这里的，前面已经置flag了
            root_page_main = page_info["main_page"]
            show_log("% page id " + page_id + " main page flag " + str(root_page_main))

            # 获取主页的系统路径（根据导出位置计算） # 拷贝dump的文件到导出位置
            root_os_path = self.__get_root_info(page_info=page_info, page_id=page_id)
            if not os.path.exists(root_os_path):
                shutil.copyfile(page_info["local_path"], root_os_path)
            else:
                show_log("file " + root_os_path + " is exist ???")

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
                    self.__get_child_info(
                        pages_handle=pages_handle,
                        child_info=pages_handle[child_id],
                        child_id=child_id,
                        root_main=page_info["main_page"],
                        root_type=page_info["type"]
                    )
                # 文件没有下载
                if child_dump_path == "":
                    show_log("% __relocate_child_page page " + child_id + " not dump success")
                    continue
                if child_os_path != "":
                    shutil.copyfile(child_dump_path, child_os_path)
                    show_log("% __relocate_child_page copy " + child_dump_path + " to " + child_os_path, level=LOG_INFO)

                # 重定位主页中的链接
                src_link = "[" + child_id + "]()"
                des_link = "[" + child_name + "](" + child_link + ")"
                self.__relocate_link(root_os_path, src_link, des_link)

                # 写入数据库辅助定位信息
                if root_md is not None:
                    root_md.write(des_link + "\n\n")

            if root_md is not None:
                root_md.close()

            # 递归处理子页面,链接页面不会递归
            self.__relocate_child_page(pages_handle, page_info["child_pages"])
        return True


class Config:
    def __init__(self):
        self.config = None
        self.__read_config()

    def __read_config(self):
        try:
            with open(CONFIG_FILE_NAME, encoding="utf-8") as conf_file_handle:
                self.config = json.load(conf_file_handle)
        except FileNotFoundError:
            show_log("Configuration file does not exist", level=LOG_INFO)
        except JSONDecodeError:
            show_log("Configuration file is corrupted", level=LOG_INFO)

    def get_key(self, key):
        return self.config.get(key)

    def check_config(self):
        if self.config is None:
            return False
        return True


if __name__ == '__main__':
    config = Config()
    if not config.check_config():
        show_log("Config init failed, file:" + CONFIG_FILE_NAME, level=LOG_INFO)
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
        show_log("unknown type " + _dump_type_str, level=LOG_INFO)
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
    dump_api.start_dump()