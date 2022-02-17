# notion-dump-client-single

基于notion-dump-kernel的一个实例（在下载页面并解析的基础上对下载页面内的链接进行重定位），用于递归导出notion页面（页面内几乎所有内容详细见测试页面）为Markdown&CSV格式

## 一、描述

- [ ] 对递归下载的notion指定页面将其中的链接重定位，形成一种内置的文件结构（见输出描述）

## 二、使用

## 2.1 客户端版本使用

<font color=red>**使用前仔细看配置文件和如下配置说明**</font>

**填写配置**：本实例使用配置文件和一个图形客户端（显示dump日志）组成，其中配置文件说明如下：

```json
{
    "token": "xxxxxxxxxxxxxxx",
    "page_id" : "xxxxxxxxxxxxxxxxxxxxxxxx",
    "page_type" : "page",
    "export_child_page": true,
    "dump_path": "./dumped_file",
    "page_parser_type": "md",
    "db_parser_type": "plain"
}
```

-   token：notion官方API token
-   page_id：需要备份的notion页面（注意token需要在该页面有权限）
-   page_type：目前只支持page类型（另一种是database，不过解析出来很诡异，调了三天bug了不想调了）
-   export_child_page：是否导出子页面（true/false）

- dump_path：导出路径位置（基于当前程序位置）
- page_parser_type：页面解析类型（md/plain：md是markdown格式，plain是纯文本格式，page默认是markdown，填错时会选择默认值并且不提示）
- db_parser_type：数据库解析类型（md/plain：md是markdown格式，plain是纯文本格式，database默认是plain，填错时会选择默认值并且不提示）

**运行客户端**：

![客户端界面](https://github.com/delta1037/notion-dump-local/blob/main/img/client-img.jpg)

在**填好配置之后**，点击开始按钮即可开始备份，出现错误时先点击测试按钮看是否成功，如果成功可以在此项目中提交issue，并向Email：geniusrabbit@qq.com发送客户端目录下的`dump.log`，**注意删除其中的token部分**



### 2.2 接口版本使用

接口版本封装了如下三个接口，其中参数自解释（或者看客户端参数配置和[notion-dump-kernel](https://github.com/delta1037/notion-dump-kernel)的参数说明）

```python 
# 1、初始化赋值
def __init__(
            self,
            token=None,
            page_id=None,
            dump_path="./dumped_file",
            dump_type=NotionDump.DUMP_TYPE_PAGE,
            export_child=False,
            page_parser_type=NotionDump.PARSER_TYPE_MD,
            db_parser_type=NotionDump.PARSER_TYPE_PLAIN
    )
   
   
# 2、重新赋值
def reset_param(
            self,
            token=None,
            page_id=None,
            dump_path=None,
            dump_type=None,
            export_child=None,
            page_parser_type=None,
            db_parser_type=None
    )


# 3、开始导出，或者导出前赋值
def start_dump(
            self,
            token=None,
            page_id=None,
            dump_path=None,
            dump_type=None,
            export_child=None,
            page_parser_type=None,
            db_parser_type=None
    )
```

## 三、输出

下载主目录由用户决定，主目录下结构为
```powershell
- child_pages/  # 所有的子页面（包括数据库中的子页面）
- databases/    # 所有导出的数据库（包含csv和一个markdown格式的数据库页面辅助定位文件）
- files/        # 所有的图片和文件
main.md         # 下载页面id（作为主页存在）
```

