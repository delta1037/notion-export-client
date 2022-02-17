# notion-dump-client-multi

notion-dump-client-multi是notion-dump-client的增强版。notion-dump-client是基于notion-dump-kernel的一个实例（在下载页面并解析的基础上对下载页面内的链接进行重定位），用于递归导出notion页面（页面内几乎所有内容详细见测试页面）为Markdown&CSV格式。notion-dump-client-multi在此基础上支持多个页面导出，采用notion数据库页面配置页面导出的参数。

## 一、功能

- [ ] **批量导出**页面到本地指定路径（notion数据库配置导出参数）

## 二、使用

## 2.0 配置参数数据库和日志数据库

![参数数据库样例](https://github.com/delta1037/notion-dump-local/blob/main/img/database_args.png)

[参数数据库模板链接](https://delta1037.notion.site/dump-a0a1fb8c871b4672b5b20437d8a078ec)

**注意：**如果修改数据库中的字段名，配置中的`backup_list_map`或者`backup_log_map`这两个字段映射表需要随之修改

## 2.1 客户端版本使用

<font color=red>**使用前仔细看配置文件和如下配置说明**</font>

**填写配置**：本实例使用配置文件和一个图形客户端（显示dump日志）组成，其中配置文件说明如下：

```json
{
    "dump_token": "secret_WRLJ9xxxxxxxxxxxxxxxxxxxx",
    "backup_info_token" : "secret_WRLJ9xxxxxxxxxxxxxxxxxxxx",
    "backup_list_id" : "b70a415f82384d3cbb3e240ca84fc1cd",
    "backup_log_id" : "26eda87ee96a48dca29f4df5764a5667",
    "backup_list_map": {
        "page_id": "页面ID",
        "page_type": "页面类型",
        "dump_path": "备份位置",
        "export_child_page": "递归备份",
        "page_parser_type": "页面备份类型",
        "db_parser_type": "数据库备份类型",
        "dump_status": "备份"
    },
    "backup_log_map": {
        "title": "时间戳",
        "date": "备份时间",
        "status": "备份状态",
        "log": "备注"
    }
}
```

-   dump_token：导出页面需要invite此token
-   backup_info_token：参数配置和备份日志页面需要invite此token
-   backup_list_id：导出页面参数数据库id
-   backup_log_id：备份日志数据库id
-   backup_list_map：导出页面参数数据库字段映射表（如果是直接dump未修改数据库字段则不需要修改）
-   backup_log_map：备份日志数据库字段映射表（如果是直接dump未修改数据库字段则不需要修改）

**运行客户端**：

![客户端界面](https://github.com/delta1037/notion-dump-local/blob/main/img/client-img.jpg)

在**填好配置之后**，点击开始按钮即可开始备份，如果出现可以在此项目中提交issue，并向Email：geniusrabbit@qq.com发送客户端目录下的`dump.log`，**注意删除其中的token部分**



### 2.2 服务端版本使用

服务端版本是一个python文件（`notion-dump-server.py`），添加到服务端的定时任务中即可

**填写配置**：

服务端版本的配置文件与客户端配置规则一致，不再赘述

**运行服务端**：

在终端运行如下命令即可（定时任务不再赘述）

```shell
python3 notion-dump-server.py
```

## 三、输出

备份位置下的结构为
```powershell
- child_pages/  # 所有的子页面（包括数据库中的子页面）
- databases/    # 所有导出的数据库（包含csv和一个markdown格式的数据库页面辅助定位文件）
- files/        # 所有的图片和文件
main.md         # 下载页面id（作为主页存在）
```

