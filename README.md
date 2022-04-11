# notion-export-client

[中文版](https://github.com/delta1037/notion-dump-local/blob/main/README_zh.md)

Backup tool base on [notion-export-kernel](https://github.com/delta1037/notion-export-kernel). It use official API and integration token. 

```bash
pip isntall notion-dump-kernel
# NOT notion-export-kernel
```

-   **You should know the backup file cant restore to notion. Its completely local. **

-   **You should update notion-dump-kernel to the latest version and check for updates regularly**



Functions：

-   convert notion page or database to markdown file（you can choose CSV type for database）
-   relocate link(sub-pages, image, files) in markdown file (relocate to local url)

## Version

Single page convert GUI / Multi page convert GUI

-   Single page convert GUI（[README](https://github.com/delta1037/notion-dump-local/blob/main/README_single.md)）
-   Multi page convert GUI（[README](https://github.com/delta1037/notion-dump-local/blob/main/README_multi.md)）



*If you want put this tool on you server (for regular backup), you could choose \*\_server\_\*.py version.*

## Files

backup == convert

- api/backup_info.py: operate backup list page (the page is the config of backup what and where to backup). It will check backup status and add backup  log automately
- api/notion_dump_api.py: relocate link in the page of *notion-dump-kernel* downloaded, regroup the file downloaded.
- notion_dump_server_single.py: the server script to backup single page（use cron command to do regular backup ）
- notion_dump_client_single.py: a GUI client to backup single page (it is very simple, all settings are configured in config file)
- notion_dump_server_multi.py: the server script to backup multi page（use cron command to do regular backup ）
- notion_dump_client_multi.py: a GUI client to backup multi page (it is very simple, all settings are configured in config file)

