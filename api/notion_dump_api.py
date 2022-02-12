# author: delta1037
# Date: 2022/01/14
# mail:geniusrabbit@qq.com

import copy
import os
import shutil
import time
import json

import NotionDump
from NotionDump.Dump.dump import Dump
from NotionDump.Notion.Notion import NotionQuery
from NotionDump.utils import common_op

VERSION = "0.3"
# 配置位置
CONFIG_FILE_NAME = "../config.json"
# 子目录的定制
CHILD_PAGES_PATH = "./child_pages/"
DATABASE_PATH = "./databases/"
FILES_PATH = "./files/"

# 日志等级
LOG_DEBUG = 1
LOG_INFO = 2

# 利用本地下载好的文件测试 ./tmp文件夹
LOCAL_FILE_TEST = False


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

        # 记录数据库插入到嵌入改数据库md文件的位置
        # db_relocate_item = {
        #     "parent_os_path": "path",    # 父文件位置
        #     "parent_key_id": "key_id",   # 父文件需要插入的位置
        #     "database_os_path": "path"   # 子文件位置
        # }
        self.__db_relocate_dic = {}  # db_relocate_item 组成的list

    @staticmethod
    def show_log(debug_str, level=LOG_DEBUG):
        current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        log_msg_in = str(current_time) + " " + str(debug_str)
        # if level == LOG_INFO:
        print(log_msg_in)

    def __init_query_handle(self):
        if self.__token is None:
            return None
        query_handle = NotionQuery(token=self.__token)
        if query_handle is None:
            self.show_log("query handle init error, check your token", level=LOG_INFO)
            return None
        self.show_log("notion query handle init success", level=LOG_INFO)
        return query_handle

    # 开始之前校验变量
    def __check_variable(self):
        if self.__query_handle is None:
            return False
        if self.__page_id is None or self.__page_id == "":
            self.show_log("page_id is null", level=LOG_INFO)
            return False
        if self.__dump_path is None or self.__dump_path == "":
            self.show_log("dump_path is null", level=LOG_INFO)
            return False
        if self.__dump_type != NotionDump.DUMP_TYPE_PAGE and self.__dump_type != NotionDump.DUMP_TYPE_DB_TABLE:
            self.show_log("dump only support page&database now", level=LOG_INFO)
            return False
        if self.__export_child is not True and self.__export_child is not False:
            self.show_log("export_child type error", level=LOG_INFO)
            self.show_log(self.__export_child, level=LOG_INFO)
            return False
        if self.__page_parser_type != NotionDump.PARSER_TYPE_MD and self.__page_parser_type != NotionDump.PARSER_TYPE_PLAIN:
            self.show_log("page_parser_type error", level=LOG_INFO)
            return False
        if self.__db_parser_type != NotionDump.PARSER_TYPE_MD and self.__db_parser_type != NotionDump.PARSER_TYPE_PLAIN:
            self.show_log("db_parser_type error", level=LOG_INFO)
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
            if self.__token is None or self.__token != token:
                self.show_log("init or reinit query handle", level=LOG_INFO)
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
        if page_parser_type is not None:
            self.__page_parser_type = page_parser_type
        if db_parser_type is not None:
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
            self.show_log("param check fail, return", level=LOG_INFO)
            return False

        # 文件名安全测试
        test_file_name = "\\ / : * ? \" < > | ”"
        self.show_log(
            "filename replace reg: from " + test_file_name + " to " + self.__get_safe_file_name(test_file_name),
            level=LOG_INFO)
        # 开始导出
        return self.__start_export()

    def show_param(self):
        self.show_log("version:" + VERSION, level=LOG_INFO)
        self.show_log("  token:" + self.__token)
        self.show_log("page_id:" + self.__page_id, level=LOG_INFO)
        type_str = "unknown"
        if self.__dump_type == NotionDump.DUMP_TYPE_PAGE:
            type_str = "DUMP_TYPE_PAGE"
        elif self.__dump_type == NotionDump.DUMP_TYPE_DB_TABLE:
            type_str = "DUMP_TYPE_DB_TABLE"
        elif self.__dump_type == NotionDump.DUMP_TYPE_BLOCK:
            type_str = "DUMP_TYPE_BLOCK"
        self.show_log("   type:" + type_str, level=LOG_INFO)
        self.show_log("  recur:" + str(self.__export_child), level=LOG_INFO)
        self.show_log("   path:" + self.__dump_path, level=LOG_INFO)
        page_parser_s = "md"
        if self.__page_parser_type == NotionDump.PARSER_TYPE_PLAIN:
            page_parser_s = "plain"
        db_parser_s = "plain"
        if self.__db_parser_type == NotionDump.PARSER_TYPE_MD:
            db_parser_s = "md"
        self.show_log("page_parser:" + page_parser_s, level=LOG_INFO)
        self.show_log("  db_parser:" + db_parser_s, level=LOG_INFO)

    def __start_export(self):
        if not LOCAL_FILE_TEST:
            page_handle = Dump(
                dump_id=self.__page_id,
                query_handle=self.__query_handle,
                export_child_pages=self.__export_child,
                dump_type=self.__dump_type,
                db_parser_type=self.__db_parser_type,
                page_parser_type=self.__page_parser_type
            )
            # 将解析内容存储到文件中；返回内容存储为json文件
            self.show_log("start dump to file ..., it may take a long time if you page is too many", level=LOG_INFO)
            page_detail_json = page_handle.dump_to_file()
            json_name = ".tmp/page_parser_result.json"
            common_op.save_json_to_file(handle=page_detail_json, json_name=json_name)
            self.show_log("page dump success, file info save at " + json_name, level=LOG_INFO)
        else:
            # 从本地加载文件
            json_name = ".tmp/page_parser_result.json"
            with open(json_name, "r", encoding="utf-8") as f:
                page_detail_json = json.load(f)

        # 主页不存在，可能是导出失败
        if self.__page_id not in page_detail_json.keys():
            self.show_log("page dump fail, can't find main page ", level=LOG_INFO)
            return False

        # 生成文件目录
        self.__gen_dir()
        main_page_list = [self.__page_id]
        dump_path_last_no_path = self.__dump_path[0:self.__dump_path.rfind('/')]
        dump_path_last = dump_path_last_no_path[dump_path_last_no_path.rfind('/')+1:]
        self.show_log("page dump main page name: " + dump_path_last, level=LOG_INFO)
        if dump_path_last == "":
            page_detail_json[self.__page_id]["page_name"] = "main_page"
        else:
            page_detail_json[self.__page_id]["page_name"] = dump_path_last

        # 利用一下json里的page_recursion变量
        for p_id in page_detail_json:
            page_detail_json[p_id]["page_recursion"] = False
        self.show_log("start relocate link in file...", level=LOG_INFO)
        self.__relocate_child_page(page_detail_json, main_page_list, is_main=True)
        self.show_log("file link relocate success, check path :" + self.__dump_path, level=LOG_INFO)
        if self.__db_parser_type == NotionDump.PARSER_TYPE_MD:
            self.__relocate_db()
        return True

    # 创建文件目录
    def __gen_dir(self):
        if not os.path.exists(self.__dump_path):
            os.makedirs(self.__dump_path)

        CHILD_PATH = self.__dump_path + CHILD_PAGES_PATH
        if not os.path.exists(CHILD_PATH):
            os.mkdir(CHILD_PATH)

        DB_PATH = self.__dump_path + DATABASE_PATH
        if not os.path.exists(DB_PATH):
            os.mkdir(DB_PATH)

        FILE_PATH = self.__dump_path + FILES_PATH
        if not os.path.exists(FILE_PATH):
            os.mkdir(FILE_PATH)

    def __add_page_file_suffix(self, child_info, page_name):
        if (child_info["type"] == "image" or child_info["type"] == "file") and page_name.find('.') != -1:
            return page_name
        local_path = child_info["local_path"]
        local_filename = local_path[local_path.rfind('/'):]
        page_name = page_name + local_filename[local_filename.find('.'):]
        self.show_log("get page name: " + page_name, level=LOG_INFO)
        return page_name

    def __relocate_link(self, file_name, src_str, des_str, show_log=True):
        if show_log:
            self.show_log("@ in file:" + file_name + " " + src_str + " -> " + des_str, level=LOG_INFO)
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

    @staticmethod
    def __get_safe_file_name(file_name):
        # 文件名不能包含的特殊字符： \ / : * ? " < > |
        file_name = file_name.replace("\\", "-")
        file_name = file_name.replace("/", "-")
        file_name = file_name.replace(":", "-")
        file_name = file_name.replace("*", "-")
        file_name = file_name.replace("?", "-")
        file_name = file_name.replace("|", "-")
        file_name = file_name.replace("\"", "-")
        file_name = file_name.replace("”", "-")
        file_name = file_name.replace("<", "-")
        file_name = file_name.replace(">", "-")
        # 去掉公式特性
        file_name = file_name.replace("$", "-")
        # 去掉换行
        file_name = file_name.replace("\n", "-")
        # 去掉空格
        file_name = file_name.replace(" ", "")
        return file_name

    # 获取页面的链接 [页面名称](页面链接)  页面dump路径 页面系统路径
    def __get_child_info(self, pages_handle, child_info, child_id, root_main=False, root_type="page"):
        self.show_log("> [START] __get_child_info " + child_id)
        self.show_log("> [START] root_main :" + str(root_main))
        self.show_log("> [START] child_main :" + str(child_info["main_page"]))
        self.show_log("> [START] root_type :" + root_type)

        child_main = child_info["main_page"]

        # 获取页面名称
        child_name = child_info["page_name"]

        # 如果子页面是一个链接类型
        # 页面名称 用链接的名称
        # 页面位置 用实际的
        # dump路径 用实际的
        if common_op.is_link_page(child_id, pages_handle[child_id]):
            self.show_log("> page id:" + child_id + " is link page, get true page")
            self.show_log("> link id:" + child_info["link_id"])
            # 向真正的页面传递
            l_name, l_link, l_dump_path, l_os_path = \
                self.__get_child_info(
                    pages_handle=pages_handle,
                    child_info=pages_handle[child_info["link_id"]],
                    child_id=child_info["link_id"],
                    root_main=root_main,
                    root_type=root_type
                )
            if child_name == "":
                child_name = l_name
            return child_name, l_link, l_dump_path, l_os_path

        if child_name == "":
            # 如果没名字，用ID做名字
            child_name = child_id

        # 到了这之后可以认为都是子页面（非链接）
        # 获取页面后缀,
        page_name_suffix = self.__get_safe_file_name(copy.deepcopy(child_name))
        page_name_suffix = self.__add_page_file_suffix(child_info, page_name_suffix)
        # 获取页面链接
        child_link = ""
        if root_main and child_main:
            # 主页里面包含了自己（这里是主页里面有链接是自己）
            child_link = "./" + page_name_suffix
        elif root_main and not child_main:
            # 子页面，重定位链接
            if child_info["type"] == "page":
                child_link = "./" + CHILD_PAGES_PATH + page_name_suffix
            elif child_info["type"] == "database":
                # 主页面嵌套数据库
                child_link = "./" + DATABASE_PATH + page_name_suffix
            elif child_info["type"] == "image" or child_info["type"] == "file":
                # 主页面嵌套图片或者文件
                child_link = "./" + FILES_PATH + page_name_suffix
            else:
                # 无法识别的子页面类型
                self.show_log("> child type error : " + child_info["type"], level=LOG_INFO)
        elif not root_main and child_main:
            # 子页面中调用了主页面
            child_link = "../" + page_name_suffix
        else:
            if child_info["type"] == "page":
                # 子页面
                child_link = "../" + CHILD_PAGES_PATH + page_name_suffix
            elif child_info["type"] == "database":
                # 子数据库
                child_link = "../" + DATABASE_PATH + page_name_suffix
            elif child_info["type"] == "image" or child_info["type"] == "file":
                # 子页面嵌套图片或者文件
                child_link = "../" + FILES_PATH + page_name_suffix
            else:
                # 无法识别的子页面类型
                self.show_log("> child type error : " + child_info["type"], level=LOG_INFO)

        # 获取系统路径
        page_os_path = ""
        if root_main and child_main:  # child_info["main_page"]
            page_os_path = self.__dump_path + page_name_suffix
        elif not root_main and child_main:
            page_os_path = self.__dump_path + "../" + page_name_suffix
        else:
            if child_info["type"] == "page":
                page_os_path = self.__dump_path + CHILD_PAGES_PATH + page_name_suffix
            elif child_info["type"] == "database":
                page_os_path = self.__dump_path + DATABASE_PATH + page_name_suffix
            elif child_info["type"] == "image" or child_info["type"] == "file":
                page_os_path = self.__dump_path + FILES_PATH + page_name_suffix
            else:
                self.show_log("> there may be a error type" + child_info["type"], level=LOG_INFO)
        # 判断系统路径合法性
        if page_os_path != "" and os.path.exists(page_os_path):
            self.show_log("> page " + page_os_path + " exist in local, dont need copy", level=LOG_INFO)
            page_os_path = ""

        self.show_log("> [END] __get_child_info page id " + child_id)
        self.show_log("> [END] __get_child_info child_name :" + child_name)
        self.show_log("> [END] __get_child_info child_link :" + child_link)
        self.show_log("> [END] __get_child_info local_path :" + child_info["local_path"])
        self.show_log("> [END] __get_child_info os_path :" + page_os_path)
        return child_name, child_link, child_info["local_path"], page_os_path

    # 获取主页信息（导出的系统路径）
    def __get_root_info(self, page_info, page_id):
        self.show_log("= [START] __get_root_info " + page_id + " param info:")
        self.show_log("= [START] root_main :" + str(page_info["main_page"]))
        # 获取页面名称
        page_name = page_info["page_name"]
        if page_name == "":
            if page_info["main_page"]:
                page_name = "main_page"
            else:
                page_name = page_id

        # 给页面加个后缀;获取安全路径
        page_name_suffix = self.__get_safe_file_name(copy.deepcopy(page_name))
        page_name_suffix = self.__add_page_file_suffix(page_info, page_name_suffix)

        # 获取系统路径
        if page_info["main_page"]:
            page_os_path = self.__dump_path + page_name_suffix
        else:
            if page_info["type"] == "page":
                page_os_path = self.__dump_path + CHILD_PAGES_PATH + page_name_suffix
            else:
                page_os_path = self.__dump_path + DATABASE_PATH + page_name_suffix

        self.show_log("= [END] __get_root_info page_id " + page_id)
        self.show_log("= [END] __get_root_info page_os_path :" + page_os_path)
        return page_os_path

    # 该操作需要递归进行
    # 传入一个下载好的文件相关信息，需要操作的列表，重定位新路径默认是当前路径
    def __relocate_child_page(self, pages_handle, page_list, is_main=False):
        for page_id in page_list:
            # 设置标志位，防止嵌套页面死循环（或者在处理链接死循环）
            if pages_handle[page_id]["page_recursion"]:
                continue
            pages_handle[page_id]["page_recursion"] = True

            # 下载的文件不需要进一步处理
            if pages_handle[page_id]["type"] == "file" or pages_handle[page_id]["type"] == "image":
                continue

            # 区分链接页面和非链接页面,link_id是链接页面ID,page_id是实际页面ID
            if common_op.is_link_page(page_id, pages_handle[page_id]):
                true_id = self.__find_true_id(pages_handle, page_id)
                self.show_log("% __relocate_child_page page id is:" + page_id)
                self.show_log("% __relocate_child_page true_id is:" + true_id)
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

            # 主页面的数据库，与主页面同等看待
            if "_main_page_db" in pages_handle[page_id].keys():
                page_info["main_page"] = True

            # 判断实际页面是否成功导出
            if not page_info["dumped"]:
                self.show_log("% page:" + page_id + " not export success", level=LOG_INFO)
                continue

            # 如果文件不存在(成功导出但是内容为空则不会有本地文件)
            if page_info["local_path"] == "":
                self.show_log("% page:" + page_id + " local_path is null", level=LOG_INFO)
                continue

            # 根路径是不是主页，如果链接到主页面那么程序不会到这里的，前面已经置flag了
            # root_page_main = page_info["main_page"]
            self.show_log("% page id " + page_id + " main page flag " + str(page_info["main_page"]))

            # 获取主页的系统路径（根据导出位置计算） # 拷贝dump的文件到导出位置
            root_os_path = self.__get_root_info(page_info=page_info, page_id=page_id)
            if not os.path.exists(root_os_path):
                shutil.copyfile(page_info["local_path"], root_os_path)
                self.show_log("% __relocate_child_page <root> copy " + page_info["local_path"] + " to " + root_os_path,
                              level=LOG_INFO)
            else:
                self.show_log("file " + root_os_path + " is exist ???")

            # 对数据库类型生成同路径md辅助文件
            root_md = None
            if self.__db_parser_type != NotionDump.PARSER_TYPE_MD and page_info["type"] == "database":
                # 数据库类型，生成同路径md文件，辅助做数据库中的链接定位
                root_md_name = root_os_path[0:root_os_path.rfind(".")] + ".md"
                root_md = open(root_md_name, "w+", encoding="utf-8")

            # 开始处理该页面下的所有链接，并将主页中的内容重定位
            # 获取到所有的子页面id 将主页中的子页面进行重定位，获取实际链接
            for child_id in page_info["child_pages"]:
                # 如果是子id是主页面包含的数据库，给子页面添加 额外的标志位
                if self.__db_parser_type == NotionDump.PARSER_TYPE_MD \
                        and is_main and pages_handle[child_id]["type"] == "database":
                    pages_handle[child_id]["_main_page_db"] = "true"
                    pages_handle[child_id]["main_page"] = True

                # 计算子页面名称和链接
                child_name, child_link, child_dump_path, child_os_path = \
                    self.__get_child_info(
                        pages_handle=pages_handle,
                        child_info=pages_handle[child_id],
                        child_id=child_id,
                        root_main=page_info["main_page"],
                        root_type=page_info["type"]
                    )

                if child_os_path != "" and child_dump_path != "":
                    shutil.copyfile(child_dump_path, child_os_path)
                    self.show_log("% __relocate_child_page copy " + child_dump_path + " to " + child_os_path, level=LOG_INFO)

                # 重定位主页中的链接
                src_link = "[" + child_id + "]()"
                if child_dump_path != "":
                    des_link = "[" + child_name + "](" + child_link + ")"
                    if pages_handle[child_id]["type"] == "image":
                        # 图片类型链接
                        des_link = "!" + des_link
                    elif pages_handle[child_id]["type"] == "database" and self.__db_parser_type != NotionDump.PARSER_TYPE_MD:
                        # 新增一个辅助路径文件
                        des_link += "\n" + "[" + child_name + "](" + child_link[0:child_link.rfind(".")] + ".md" + ")"
                else:
                    des_link = child_name
                self.__relocate_link(root_os_path, src_link, des_link)
                self.show_log("% __relocate_link file " + root_os_path + ", from " + src_link + " to " + des_link,
                              level=LOG_INFO)

                # 记录需要重定位的数据库(要求：md格式，数据库，已下载，非链接类型，)
                if self.__db_parser_type == NotionDump.PARSER_TYPE_MD \
                        and pages_handle[child_id]["type"] == "database" \
                        and child_os_path != "" \
                        and not common_op.is_link_page(child_id, pages_handle[child_id]):
                    if child_os_path not in self.__db_relocate_dic.keys():
                        self.__db_relocate_dic[child_os_path] = {}
                    if "parent_os_path" not in self.__db_relocate_dic[child_os_path].keys():
                        self.__db_relocate_dic[child_os_path]["parent_os_path"] = []
                    self.__db_relocate_dic[child_os_path]["parent_os_path"].append(root_os_path)
                    self.__db_relocate_dic[child_os_path]["parent_key_id"] = des_link
                    self.__db_relocate_dic[child_os_path]["database_name"] = child_name
                    self.show_log(self.__db_relocate_dic)

                # 写入数据库辅助定位信息
                if root_md is not None and child_dump_path != "":
                    root_md.write(des_link + "\n\n")

            if root_md is not None:
                root_md.close()

            # 递归处理子页面,链接页面不会递归
            self.__relocate_child_page(pages_handle, page_info["child_pages"])
        return True

    def __relocate_db(self):
        # 根据 __db_relocate_list 记录的内容，对相关的文件重新定位即可
        for db_os_path in self.__db_relocate_dic.keys():
            file = open(db_os_path, 'r', encoding='utf-8')
            db_all_line = "##### " + self.__db_relocate_dic[db_os_path]["database_name"] + "\n" + file.read()
            file.close()
            for p_os_path in self.__db_relocate_dic[db_os_path]["parent_os_path"]:
                md_file = p_os_path
                md_key = self.__db_relocate_dic[db_os_path]["parent_key_id"]

                # 将数据库内容插入到原来的位置,替换成标题加表格的形式
                self.__relocate_link(md_file, md_key, db_all_line, show_log=False)

            # 删除新增的数据库表格
            # if "db_be_rel" not in self.__db_relocate_dic[db_os_path].keys():
            #     os.remove(db_os_path)
