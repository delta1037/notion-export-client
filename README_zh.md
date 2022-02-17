# notion-dump-local

基于[notion-dump-kernel](https://github.com/delta1037/notion-dump-kernel)的实例

功能：

-   将notion页面转换为本地的markdown文件
-   对markdown文件中的链接（子页面、图片、文件）进行重新定位

## 版本

分为单个页面导出和多个页面导出两个版本

-   单个页面转换（[README](https://github.com/delta1037/notion-dump-local/blob/main/README_single_zh.md)）
-   多个页面转换（更强悍）（[README](https://github.com/delta1037/notion-dump-local/blob/main/README_multi_zh.md)）

## 文件说明

备份 == 转换

- api/backup_info.py: 备份页面清单管理（修改清单备份状态，新增备份历史记录）
- api/notion_dump_api.py: 对notion-dump-kernel下载的文件重新组合位置并对文件中的链接（子页面、图片、文件）之类的重新定位
- notion_dump_server_single.py: 单个页面备份脚本（命令行配置定时任务）
- notion_dump_client_single.py:单个页面备份客户端（图形界面，挺简陋的）
- notion_dump_server_multi.py:多个页面备份脚本（命令行配置定时任务）
- notion_dump_client_multi.py:多个页面备份客户端（图形界面，挺简陋的）

