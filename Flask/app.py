import os
import sys
import json
import threading
import time

from NotionDump import NotionBackupLogger
from api.configuration import CONFIG_FILE_PATH, Configuration
from api.notion_dump import NotionBackup

from flask import Flask, render_template, send_from_directory, request
from flask_bootstrap import Bootstrap

app = Flask(__name__, template_folder='templates', static_folder='static//')
app.config['SECRET_KEY'] = 'delta1037@qq.com'
app.config['BOOTSTRAP_SERVE_LOCAL'] = True
bootstrap = Bootstrap(app)

SEVER_ABS_PATH = os.path.dirname(sys.argv[0])
LOG_FILE = SEVER_ABS_PATH + "/dump.log"


class NotionBackupGUI(NotionBackupLogger):
    def __init__(self):
        super().__init__()
        self.__notion_backup = None
        # 日志文件句柄
        self.__log = open(LOG_FILE, "a+", encoding='utf-8')
        # 输出备份的时间
        self.backup_time = time.strftime('backup_time: %Y-%m-%d %H:%M:%S\n', time.localtime(time.time()))
        self.__log.write("\n###################################################\n")
        self.__log.write(self.backup_time + "\n")
        self.__log.flush()
        # 增量输出内容，给前端用的
        self.__mutex = threading.Lock()
        self.__append_buffer = ""

    def log_debug(self, log_str):
        self.log_info(log_str)

    def log_info(self, message):
        self.log("[EXPORT KERNEL] " + str(message))

    def log(self, msg):
        # 文件输出
        self.__log.write(msg + "\n")
        self.__log.flush()

        # 窗口输出
        self.__mutex.acquire()
        self.__append_buffer += (str(msg) + "\n")
        self.__mutex.release()

    def init_process(self, config_handle):
        # dump api
        self.__notion_backup = NotionBackup(logger=self, config=config_handle)

    def start_process(self):
        # 转入后台执行
        self.log(self.backup_time)
        self.__notion_backup.start_dump(force_auto=True)

    def get_append_log(self):
        self.__mutex.acquire()
        ret_str = self.__append_buffer
        self.__append_buffer = ""
        self.__mutex.release()
        # print("//trans", ret_str, "##trans", len(ret_str))
        return ret_str


# 初始化控制程序
gui = NotionBackupGUI()
config = Configuration(CONFIG_FILE_PATH, gui)
gui.init_process(config)


@app.route('/', methods=['GET', 'POST'])
def index():
    # 默认返回主界面渲染
    return render_main()


# 基本设置界面
@app.route('/setting_base', methods=['GET', 'POST'])
def render_setting_base():
    backup_type = config.get_key("*backup_type")
    return render_template(
        'index.html',
        main_content=render_template(
            'setting_base.html',
            backup_root_path=config.get_key("backup_root_path", default=""),
            display_rowss=["单页面备份", "多页面备份"],
            # 单页面配置
            display_rows_choose=("单页面备份" if backup_type == "single" else "多页面备份"),
            single_readonly_token=config.get_key("*backup_token", prefix="single"),
            single_page_id=config.get_key("*page_id", prefix="single"),
            single_page_types=["Page-ID是页面类型的", "Database-ID是数据库页面类型的"],
            single_page_type_choose=("Page-ID是页面类型的" if config.get_key("-page_type", prefix="single") == "page" else "Database-ID是数据库页面类型的"),
            single_dump_path=config.get_key("-dump_path", prefix="single"),
            database_insert_types=["Content-内容嵌入", "Link-链接嵌入"],
            database_insert_type_choose=("Content-内容嵌入" if config.get_key("db_insert_type", prefix="single") == "content" else "Link-链接嵌入"),
            # 多页面配置
            multi_readonly_token=config.get_key("*backup_token", prefix="multi"),
            multi_rw_token=config.get_key("*backup_info_token", prefix="multi"),
            multi_page_id=config.get_key("*backup_list_id", prefix="multi"),
            multi_log_id=config.get_key("*backup_log_id", prefix="multi"),
        )
    )


# 基本设置 确认请求
@app.route('/setting_base_ack', methods=['GET', 'POST'])
def setting_base_ack():
    setting_base_json = json.loads(request.data)
    # print(setting_base_json)
    config.alt_key("backup_root_path", setting_base_json["backup_root_path"])
    if setting_base_json["display_type"] != "多页面备份":
        config.alt_key("*backup_type", "single")
        config.alt_key("*backup_token", setting_base_json["single_readonly_token"], prefix="single")
        config.alt_key("*page_id", setting_base_json["single_page_id"], prefix="single")
        if "Page-" in setting_base_json["single_page_type"]:
            config.alt_key("-page_type", "page", prefix="single")
        else:
            config.alt_key("-page_type", "database", prefix="single")
        config.alt_key("-dump_path", setting_base_json["single_dump_path"], prefix="single")
        if "Content-" in setting_base_json["database_insert_type"]:
            config.alt_key("db_insert_type", "content", prefix="single")
        else:
            config.alt_key("db_insert_type", "link", prefix="single")
    else:
        config.alt_key("*backup_type", "multi")
        config.alt_key("*backup_token", setting_base_json["multi_readonly_token"], prefix="multi")
        config.alt_key("*backup_info_token", setting_base_json["multi_rw_token"], prefix="multi")
        config.alt_key("*backup_list_id", setting_base_json["multi_page_id"], prefix="multi")
        config.alt_key("*backup_log_id", setting_base_json["multi_log_id"], prefix="multi")
    return ""


# 基本设置 取消请求
@app.route('/setting_base_cancel', methods=['GET', 'POST'])
def setting_base_cancel():
    ret_map = {
        "display_type": ("单页面备份" if config.get_key("*backup_type") == "single" else "多页面备份")
    }
    if ret_map["display_type"] != "多页面备份":
        ret_map["single_readonly_token"] = config.get_key("*backup_token", prefix="single")
        ret_map["single_page_id"] = config.get_key("*page_id", prefix="single")
        ret_map["single_page_type_choose"] = ("Page-ID是页面类型的" if config.get_key("-page_type", prefix="single") == "page" else "Database-ID是数据库页面类型的")
        ret_map["single_dump_path"] = config.get_key("-dump_path", prefix="single")
        ret_map["database_insert_type_choose"] = ("Content-内容嵌入" if config.get_key("db_insert_type", prefix="single") == "content" else "Link-链接嵌入")
    else:
        ret_map["multi_readonly_token"] = config.get_key("*backup_token", prefix="multi")
        ret_map["multi_rw_token"] = config.get_key("*backup_info_token", prefix="multi")
        ret_map["multi_page_id"] = config.get_key("*backup_list_id", prefix="multi")
        ret_map["multi_log_id"] = config.get_key("*backup_log_id", prefix="multi")
    return ret_map


# 开发设置界面
@app.route('/setting_dev', methods=['GET', 'POST'])
def render_setting_dev():
    backup_list_map = config.get_key("backup_list_map", prefix="multi")
    backup_log_map = config.get_key("backup_log_map", prefix="multi")
    # 主题名称转换
    color_theme_type_choose = "自定义"
    if config.get_key("color_theme") == "dark":
        color_theme_type_choose = "暗黑"
    elif config.get_key("color_theme") == "light":
        color_theme_type_choose = "明亮"
    # 主题文字背景属性
    color_map = config.get_key("your_color_theme")
    b_types = []
    f_types = []
    d_types = []
    for color_name in color_map:
        if color_name.startswith("b_"):
            b_types.append({
                "name": color_name[color_name.find("_")+1:],
                "id_name": color_name,
                "color": color_map[color_name]
            })
        elif color_name.startswith("f_"):
            f_types.append({
                "name": color_name[color_name.find("_")+1:],
                "id_name": color_name,
                "color": color_map[color_name]
            })
        elif color_name.startswith("d_"):
            d_types.append({
                "name": color_name[color_name.find("_")+1:],
                "id_name": color_name,
                "color": color_map[color_name]
            })

    return render_template(
        'index.html',
        main_content=render_template(
            'setting_dev.html',
            # checkbox信息
            debug=("true" if config.get_key("debug") else "false"),
            page_properties=("true" if config.get_key("page_properties") else "false"),
            use_buffer=("true" if config.get_key("use_buffer") else "false"),
            file_with_link=("true" if config.get_key("file_with_link") else "false"),
            # 日期信息
            date_formate=config.get_key("date_formate"),
            datetime_formate=config.get_key("datetime_formate"),
            # 主题选择
            color_theme_types=["明亮", "暗黑", "自定义"],
            color_theme_type_choose=color_theme_type_choose,
            b_types=b_types,
            f_types=f_types,
            d_types=d_types,
            # 多页面配置页面列名映射表
            page_id=backup_list_map["page_id"],
            page_type=backup_list_map["page_type"],
            dump_path=backup_list_map["dump_path"],
            db_insert_type=backup_list_map["db_insert_type"],
            dump_status=backup_list_map["dump_status"],
            title=backup_log_map["title"],
            date=backup_log_map["date"],
            status=backup_log_map["status"],
            log=backup_log_map["log"],
        )
    )


# 开发设置 确认请求
@app.route('/setting_dev_ack', methods=['GET', 'POST'])
def setting_dev_ack():
    setting_dev_json = json.loads(request.data)
    # print(setting_dev_json)

    # checkbox信息
    config.alt_key("debug", setting_dev_json["debug"])
    config.alt_key("use_buffer", setting_dev_json["use_buffer"])
    config.alt_key("page_properties", setting_dev_json["page_properties"])
    config.alt_key("file_with_link", setting_dev_json["file_with_link"])
    # 日期格式
    config.alt_key("date_formate", setting_dev_json["date_formate"])
    config.alt_key("datetime_formate", setting_dev_json["datetime_formate"])
    # 主题
    if setting_dev_json["theme_type"] == "明亮":
        config.alt_key("color_theme", "light")
    elif setting_dev_json["theme_type"] == "暗黑":
        config.alt_key("color_theme", "dark")
    else:
        config.alt_key("color_theme", "your_color_theme")
    for key in setting_dev_json:
        if key.startswith("b_") or key.startswith("f_") or key.startswith("d_"):
            config.alt_key(key, setting_dev_json[key], prefix="your_color_theme")

    # 备份映射表
    backup_list_map = {
        "page_id": setting_dev_json["page_id"],
        "page_type": setting_dev_json["page_type"],
        "dump_path": setting_dev_json["dump_path"],
        "dump_status": setting_dev_json["dump_status"],
        "db_insert_type": setting_dev_json["db_insert_type"],
    }
    backup_log_map = {
        "title": setting_dev_json["title"],
        "date": setting_dev_json["date"],
        "status": setting_dev_json["status"],
        "log": setting_dev_json["log"],
    }
    config.alt_key("backup_list_map", backup_list_map, prefix="multi")
    config.alt_key("backup_log_map", backup_log_map, prefix="multi")
    return ""


@app.route('/donate', methods=['GET', 'POST'])
def render_donate():
    return render_template(
        'index.html',
        main_content=render_template(
            'donate.html',
        )
    )


@app.route('/tutorial', methods=['GET', 'POST'])
def render_tutorial():
    return render_template(
        'index.html',
        main_content=render_template(
            'tutorial.html',
        )
    )


# 主界面
@app.route('/main', methods=['GET', 'POST'])
def render_main():
    return render_template(
        'index.html',
        main_content=render_template(
            'backup.html'
        )
    )


@app.route('/start_export', methods=['GET', 'POST'])
def start_export():
    gui.start_process()
    return ""


@app.route('/get_msg', methods=['GET', 'POST'])
def get_msg():
    return gui.get_append_log()
    # return "msg test"


@app.errorhandler(404)
def page_not_found(e):
    return render_template("index.html", main_content=render_template("error_404.html")), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("index.html", main_content=render_template("error_500.html")), 500


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico')


@app.route('/local_static/<path:filename>')
def local_static(filename):
    return send_from_directory(os.path.join(app.root_path, 'static'), filename)
