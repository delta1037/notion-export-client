# notion-export-client

Backup tool base on [notion-export-kernel](https://github.com/delta1037/notion-export-kernel). It use official API and integration token. 

```bash
pip isntall notion-dump-kernel
# NOT notion-export-kernel
```



**Functions：**

-   convert notion page or database to markdown file（you also can choose CSV type for database）
-   relocate link(sub-pages, image, files) in markdown file (relocate to local url)



**Attention:**

-   **You should know the backup file cant restore to notion. Its completely local. **

-   **You should update notion-dump-kernel to the latest version and check for updates regularly**

## Config

<font color=red>**Before you launch the app, you should know the meaning of the config.**</font>

**Fill the config**：config file name is `config.json`,  which content such as:

```json
{
    "backup_type": "multi",
    "auto_close": true,
    "single" : {
        "backup_token": "secret_DVp3bq1mDGUOF75mAxxxxxxxxxxxxxxxxxxx",
        "page_id" : "3b82xxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "page_type" : "page",
        "export_child_page": true,
        "dump_path": "./dumped_pages",
        "page_parser_type": "md",
        "db_parser_type": "md",
        "db_insert_type": "content"
    },
    "multi": {
        "backup_token": "secret_WRLJ9xxxxxxxxxxxxxxxxxxxx",
        "backup_info_token" : "secret_WRLJ9xxxxxxxxxxxxxxxxxxxx",
        "backup_list_id" : "3b82xxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "backup_log_id" : "26edxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        "backup_list_map": {
            "page_id": "页面ID",
            "page_type": "页面类型",
            "dump_path": "备份位置",
            "export_child_page": "递归备份",
            "page_parser_type": "页面备份类型",
            "db_parser_type": "数据库备份类型",
            "db_insert_type": "数据库嵌入类型",
            "dump_status": "备份"
        },
        "backup_log_map": {
            "title": "时间戳",
            "date": "备份时间",
            "status": "备份状态",
            "log": "备注"
        }
    }
}
```

>   single or **multi** ? (usually multi is  better. if you only have a small page, single is more simple to configure)
>
>   1、Official API have a limite on call speed
>
>   2、We usually only update a portion of the page

### Explanation：

-   backup_type：only backup one page(single)，or backup many important child pages(multi)
-   auto_close： auto close when backup finish

single:

-   backup_token：the page that you want to backup must invite this token
-   page_id：the id of the page that you want to backup
-   page_type：support page/database
-   export_child_page：backup sub-page or nested page（true/false）

-   dump_path：the path that you want  to backup
-   page_parser_type：page parser type（md/plain：md is markdown，plain only text without format，default is markdown, it will not warn when you use a wrong value）
-   db_parser_type：database parser type（md/plain：md is markdown table，plain is csv，default is plain, it will not warn when you use a wrong value）

multi:

-   dump_token：the page that you want to backup must invite this token
-   backup_info_token：the page of configuration and backup-log database (the template page that you duplicated) must invite this token
-   backup_list_id：configuration database id
-   backup_log_id：backup-log database id
-   backup_list_map：the key-value map of configuration database （you needn't edit this if you duplicated template directly and not change database properties）
-   backup_log_map：the key-value map of backup-log database（you needn't edit this if you duplicated template directly and not change database properties）

### Multi type NEED Configure database

![database sample](H:\GitHubRepo\notion-dump-local\README\database_args.png)

[configuration template](https://delta1037.notion.site/dump-a0a1fb8c871b4672b5b20437d8a078ec)

**Attention:** If you want to change the property name in database, you **must** change the key-value map of `backup_list_map` and `backup_log_map` in local config file.

## Run

use pyinstaller to pack a exe for window system (or other paltform); use `py notion_backup_terminal.py` run in terminal.



If you find any log in `dump.log` start with `[ISSUE]`, you can issue in github repo or email the `dump.log` to geniusrabbit@qq.com (**you should check the log file not contain your token !!!**)



## Output

the file structure in the path of backup: 

```powershell
- child_pages/  # all child page, include database page
- databases/    # all database file(markdown table or csv file, depend on your configuration), which used to link in page
- files/        # all file (pdf...) and image
main.md         # the main page to backup 
```



## Structure

- api/backup_info.py: operate backup list page (the page is the config of backup what and where to backup). It will check backup status and add backup log automately
- api/notion_dump_api.py: relocate link in the page of *notion-dump-kernel* downloaded, regroup the file downloaded.
- api/notion_dump.py: choose single or multi
- notion_backup_terminal.py: a terminal version of backup tool
- notion_backup_gui.py: a GUI version of backup tool
