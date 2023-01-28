# notion-export-client

**功能：**

- 将指定的notion页面和子页面备份为本地的markdown文件
  - 子页面递归下载
  - 图片下载和本地链接重定位


**注意：**

- **备份的内容不能恢复到Notion中**
- 数据库某些高级字段不支持（可以但是没必要）
- 离线目录可以自由编辑（Typora可以打开目录；Obsidian也可以打开，但是表格里的某些富文本可能无法渲染）
- 数据库备份为csv格式时，使用Excel打开会乱码，百度搜索“Excel utf8乱码”解决
- 备份的内容中图片和文件的命名优先级：Caption > (文件名称：图片没有解析名称) > id

------

**使用说明：**

- [Notion备份工具说明页面](https://www.notion.so/delta1037/Notion-921e6b4ea44046c6935bcb2c69453196)
