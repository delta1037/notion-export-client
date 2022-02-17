# notion-dump-client-single

**notion-dump-client-single** is a tool base on [notion-dump-kernel](https://github.com/delta1037/notion-dump-kernel) (regroup the file downloaded and relocate link in pages or database), it can recursionly convert all subpages (about convert block you can see test page) to markdown/CSV format (database parser type can be choosed convert to CSV).

## 1. Function

- [ ] Backup **single-page** to path configured in file named `config.json`

## 2、Usage

## 2.1 GUI usage

<font color=red>**Before you launch the app, you should know the meaning of the config.**</font>

**Fill the config**：config file name is `config.json`,  which content such as:

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

-   token：the page that you want to backup must invite this token
-   page_id：the id of the page that you want to backup
-   page_type：support page/database
-   export_child_page：backup sub-page or nested page（true/false）

- dump_path：the path that you want  to backup
- page_parser_type：page parser type（md/plain：md is markdown，plain only text without format，default is markdown, it will not warn when you use a wrong value）
- db_parser_type：database parser type（md/plain：md is markdown table，plain is csv，default is plain, it will not warn when you use a wrong value）

**运行客户端**：

![GUI](https://github.com/delta1037/notion-dump-local/blob/main/img/client-img.jpg)

After you fill the `config.json`, you can click start button to statup backup. If you find any log in `dump.log` start with `[ISSUE]`, you can issue in github repo or email the `dump.log` to geniusrabbit@qq.com (**you should check the log file not contain your token !!!**)

### 2.2 API usage

Here are three way to call the api and the args explain itself (or you can reference [notion-dump-kernel](https://github.com/delta1037/notion-dump-kernel)) 

```python 
# 1. init pass args
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
   
   
# 2. re-pass args
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


# 3. p
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

## 3. Output

the file structure in the path of backup: 

```powershell
- child_pages/  # all child page, include database page
- databases/    # all database file(markdown table or csv file, depend on your configuration), which used to link in page
- files/        # all file (pdf...) and image
main.md         # the main page to backup 
```

