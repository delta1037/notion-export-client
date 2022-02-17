# notion-dump-client-multi

**notion-dump-client-multi** is a multi-page convert version of *notion-dump-client-single*. *notion-dump-client-single* is a tool base on [notion-dump-kernel](https://github.com/delta1037/notion-dump-kernel) (regroup the file downloaded and relocate link in pages or database), it can recursionly convert all sub-pages (about convert block you can see test page) to markdown/CSV format (database parser type can be choosed convert to CSV). notion-dump-client-multi basing on this support multi-page export by iterator, which backup config will be configured in notion database. [config page example](https://www.notion.so/delta1037/2426ed9408494244a7ffaf81a6561afb) 

## 1. Function

- [ ] Backup **multi-page** to path configured in notion database (use notion database to configure backup)

## 2、Usage

## 2.0 configuration and backup-log database

![database sample](https://github.com/delta1037/notion-dump-local/blob/main/img/database_args.png)

[configuration template](https://delta1037.notion.site/dump-a0a1fb8c871b4672b5b20437d8a078ec)

**Attention:** If you want to change the property name in database, you **must** change the key-value map of `backup_list_map` and `backup_log_map` in local config file.

## 2.1 GUI usage

<font color=red>**Before you launch the app, you should know the meaning of the config.**</font>

**Fill the config**：config file name is `config_multi.json`,  which content such as:

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

-   dump_token：the page that you want to backup must invite this token
-   backup_info_token：the page of configuration and backup-log database (the template page that you duplicated) must invite this token
-   backup_list_id：configuration database id
-   backup_log_id：backup-log database id
-   backup_list_map：the key-value map of configuration database （you needn't edit this if you duplicated template directly and not change database properties）
-   backup_log_map：the key-value map of backup-log database（you needn't edit this if you duplicated template directly and not change database properties）

**Attention:** For English language user it is need to replace Chinese in `config_multi.json` **and database properties**.



**Run GUI client**：

![GUI](https://github.com/delta1037/notion-dump-local/blob/main/img/client-img.jpg)

After you fill the `config_multi.json`, you can click start button to statup backup. If you find any log in `dump.log` start with `[ISSUE]`, you can issue in github repo or email the `dump.log` to geniusrabbit@qq.com (**you should check the log file not contain your token !!!**)

### 2.2 Server usage

The server verion is a python script(`notion-dump-server.py`), you can use cron command to run regularly.

**Fill the config**：

The config file as same as GUI config.

**Run at server**：

run command in terminal（you can also use cron）

```shell
python3 notion-dump-server.py
```

## 3. Output

the file structure in the path of backup: 
```powershell
- child_pages/  # all child page, include database page
- databases/    # all database file(markdown table or csv file, depend on your configuration), which used to link in page
- files/        # all file (pdf...) and image
main.md         # the main page to backup 
```

