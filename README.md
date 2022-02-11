# notion-dump-local

基于[notion-dump-kernel](https://github.com/delta1037/notion-dump-kernel)的实例

## 版本

两个版本

-   单个页面导出（[README](https://github.com/delta1037/notion-dump-local/blob/main/README_single.md)）
-   多个页面导出（更强悍）（[README](https://github.com/delta1037/notion-dump-local/blob/main/README_multi.md)）

## 文件说明

- api/backup_info.py: 备份清单管理（修改清单备份状态，新增备份历史记录）
- api/notion_dump_api.py: 对notion-dump-kernel下载的文件重新组合位置并对文件中的链接之类的重定向
- dump_api_test.py: 单个页面备份脚本
- notion_dump_client.py:单个页面备份客户端
- notion_dump_server.py:多个页面备份脚本
- notion_dump_client_multi.py:多个页面备份客户端

