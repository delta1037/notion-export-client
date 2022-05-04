# notion--export--client

[English](https://github.com/delta1037/notion-dump-local/blob/main/README_en.md)

## 一、概要

基于[notion-export-kernel](https://github.com/delta1037/notion-dump-kernel)的一个备份工具

```bash
pip isntall notion-dump-kernel
# 不是 notion-export-kernel
```



**功能：**

-   将指定的notion页面和子页面备份为本地的markdown文件
-   对markdown文件中的链接（子页面、图片、文件）进行重新定位



**注意：**

-   **备份的内容不能恢复到Notion中**
-   **使用时需要保证notion-dump-kernel是最新版本的并且定时检查更新**

## 二、配置

<font color=red>**使用前仔细看配置文件和如下配置说明**</font>

**填写配置**：配置文件名称是`config.json`，配置文件样例和字段含义说明如下：

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

>   Q：同一个Notion账户为什么需要备份多个页面？ 
>
>   A： 
>
>   1、该备份工具使用Notion官方API获取页面数据，官方API对调用速率有要求，所以一次备份的页面量最好不要太多（太多的话目前也没遇到问题），可以对页面拆分备份，一次只备份其中有更新的一部分 
>
>   2、大部分时候主页里的一些页面不会继续更新也就不需要重新备份，所以可以对主页里面的页面进行拆分，单独进行备份

### 2.1 解释

-   backup_type：选择备份类型（**单页面或者多页面，接下来只配置多页面或者单页面的部分就可以，不需要全都填写**）
-   auto_close： 备份完成后自动关闭（在配置定时任务时，如果不需要查看终端的结果，就让它自动关了吧；该配置在图形界面无效）

单页面备份的配置字段：

-   backup_token：notion官方API token（该token只需要读权限即可）
-   page_id：需要备份的notion页面（注意token需要在该页面有读权限）
-   page_type：备份的页面类型（page/database，取决于你的page_id是从page的链接里拷贝出来的，还是从database的链接里拷贝出来的）
-   export_child_page：是否导出子页面（true/false，true的意思是导出所有的子页面，包括链接到的页面（链接到的页面有读权限即可导出）；false表示只有page_id对应的页面导出，另外对于其中的图片或者文件是否导出会有不可控的结果）
-   dump_path：备份的位置（基于当前程序位置，相对路径）
-   page_parser_type：页面解析类型（md/plain：md是markdown格式，plain是纯文本格式，page默认是markdown，填错时会选择默认值并且不提示）
-   db_parser_type：数据库解析类型（md/plain：md是markdown格式，plain是纯文本格式，database默认是plain，填错时会选择默认值并且不提示）

多页面备份的配置字段：

-   backup_token：导出页面需要invite此token（该token只需要读权限即可）
-   backup_info_token：参数配置和备份日志页面需要invite此token（该token需要读写修改权限，谨慎invite）
-   backup_list_id：导出页面参数数据库的id（包含了所有需要备份页面的参数，参数解释见`单页面备份的配置字段`，基本一致，可以任意新增字段，但是修改现有的字段名需要和backup_list_map中的映射表同步修改）
-   backup_log_id：备份日志数据库的id（包含了备份的历史记录，不需要人为修改）
-   backup_list_map：导出页面参数数据库字段映射表（如果是直接duplicate的多页面备份模板，未修改数据库字段则不需要修改）
-   backup_log_map：备份日志数据库字段映射表（如果是直接duplicate的多页面备份模板，未修改数据库字段则不需要修改）

### 2.2 多页面**需要**配置参数数据库

对于多页面的备份，备份参数的来源是notion中的一个Database，示例和模板如下（选中文版本）：

![database sample](https://github.com/delta1037/notion-export-client/tree/main/img/database_args.png)

[数据库模板](https://delta1037.notion.site/dump-a0a1fb8c871b4672b5b20437d8a078ec)

**注意：**

-   修改数据库中的字段（列）名，配置中的`backup_list_map`或者`backup_log_map`这两个字段（列）映射表需要同步修改
-   可随意新增字段/列（不与现有的字段（列）名冲突即可）

### 2.3 注意事项

1、这两类（多页面和单页面备份）都需要填写好配置 （毕竟除了你谁也不知道你想备份什么）

2、单页面需要备份的page_id在配置文件中；多页面备份需要备份的page_id在Notion数据库中，需要备份的页面需要手动勾选 

3、单页面备份和多页面备份在重新运行时，都会覆盖同一个备份目录（即如果需要对备份到本地的文件改动，请异动到别的位置，或者修改备份的位置）

### 2.4 视频参考

注意上述的配置是将单页面和多页面综合起来的（之前是分离的），但是配置过程基本不变（除了token的名称有变化而言）

[单页面备份操作视频](https://www.bilibili.com/video/BV1zr4y1Y7kt/)

[多页面备份操作视频](https://www.bilibili.com/video/BV1sP4y1P7aK/)

当你的单页面或者多页面运用的熟练之后（手动点击可以正常运行，即配置填写的没有问题），就可以选择是否进行定时自动备份了，下面是一份定时备份的教程：

[Window定时备份](https://www.bilibili.com/video/BV19u411C7cQ/)

## 三、运行

使用pyinstaller打包一个点击即运行的exe（或者其它平台）；或者直接在终端里运行脚本（`py notion_backup_terminal.py`）

如果你在`dump.log`中发现以`[ISSUE]`开头的日志，可以在[此项目](https://github.com/delta1037/notion-export-client)中提交issue，并向Email：geniusrabbit@qq.com发送客户端目录下的`dump.log`，**注意删除其中的token部分**

## 四、输出说明

备份位置下的结构为：

```powershell
- child_pages/  # 所有的子页面（包括数据库中的子页面）
- databases/    # 所有导出的数据库（包含csv和一个markdown格式的数据库页面辅助定位文件）
- files/        # 所有的图片和文件
main.md         # 下载页面id（作为主页存在）
```

该目录可以直接用`Typora`打开，或者用`Obsidian`打开。

## 五、项目结构

- api/backup_info.py: 备份页面清单管理（修改清单备份状态，自动新增备份历史记录）
- api/notion_dump_api.py: 对`notion-dump-kernel`下载的文件重新组合位置并对文件中的链接（子页面、图片、文件）之类的重新定位
- api/notion_dump.py：选择多页面或者单页面备份
- notion_backup_terminal.py：命令行黑窗版本
- notion_backup_gui.py：一个极其简单的图形界面版本（点击开始即可运行）

## 六、可参考的链接

-   [备份工具版本说明](https://www.notion.so/delta1037/Notion-921e6b4ea44046c6935bcb2c69453196)
-   [备份工具测试页面](https://www.notion.so/delta1037/Notion-dump-ed0a3b0f57b34712bc6bafcbdb413d50)
-   [单页面备份视频教程](https://www.bilibili.com/video/BV1zr4y1Y7kt/)
-   [多页面备份视频教程](https://www.bilibili.com/video/BV1sP4y1P7aK/)
-   [Window配置定时备份视频教程](https://www.bilibili.com/video/BV19u411C7cQ/)
-   [备份客户端源代码仓库](https://github.com/delta1037/notion-export-client)
-   [备份解析模块源代码仓库](https://github.com/delta1037/notion-export-kernel)
-   [我的Notion主页](https://delta1037.notion.site/)

