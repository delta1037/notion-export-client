# notion-export-client

**功能：**

- 将指定的notion页面和子页面备份为本地的markdown文件
- 对markdown文件中的链接（子页面、图片、文件）进行重新定位

**注意：**

- **备份的内容不能恢复到Notion中**
- 数据库某些高级字段不支持（可以但是没必要）
- 离线目录可以自由编辑（typora打开目录；Obsidian也可以打开，但是表格里的某些富文本无法渲染）
- 数据库备份为csv格式时，使用Excel打开会乱码，百度搜索“Excel utf8乱码”解决
- 备份的内容中图片和文件的命名优先级：Caption > (文件名称：图片没有解析名称) > id

**一些可参考链接：（教程：B站delta1037；源码：Github delta1037）**

- [备份工具测试页面](https://www.notion.so/delta1037/Notion-dump-ed0a3b0f57b34712bc6bafcbdb413d50)
- [单页面备份视频教程](https://www.bilibili.com/video/BV1zr4y1Y7kt/)
- [多页面备份视频教程](https://www.bilibili.com/video/BV1sP4y1P7aK/)
- [Window配置定时备份视频教程](https://www.bilibili.com/video/BV19u411C7cQ/)
- [备份客户端源代码仓库](https://github.com/delta1037/notion-export-client)
- [备份解析模块源代码仓库](https://github.com/delta1037/notion-export-kernel)
- [我的Notion主页](https://delta1037.notion.site/)

------

[TOC]



# 一、版本介绍

目前的备份版本有以下两个类型：

```plain text
1、notion_backup_gui
2、notion_backup_terminal
```

其中`gui`版本是图形界面版本，`terminal`版本是命令窗版本

**这两种的区别是：**

- 图形界面版本打开（运行）是一个图形界面，点击开始就可以备份
- 命令窗版本打开（运行）就可以备份

> 由于命令窗版本启动后就可以开始备份，所以该版本可以配置自动化备份（填写一个Window的定时任务配置即可）

**怎么选择：**

- 图形界面：

    - 有简单的图形界面

- 命令窗界面：

    - 可以配置定时运行，无需干预


**注意：**
1、这两种运行前都需要填写好配置（可以用[vscode](https://code.visualstudio.com/download)打开配置文件进行<u>json语法检查</u>；[在线json语法检查](https://c.runoob.com/front-end/53/)）
<font color="#D44C47">2、运行时关闭全局代理</font>

# 二、使用说明

## 2.1、配置

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

> <span style="background-color:#EDF3EC"><font color="#337EA9">Q：同一个Notion账户为什么需要备份多个页面？</font></span>

### 2.2.1 字段解释

- backup_type：选择备份类型（<font color="#9065B0">单页面或者多页面，接下来只配置多页面或者单页面的部分就可以，</font><font color="#9065B0">**不需要全都填写**</font>）
- auto_close： 备份完成后自动关闭（<font color="#9065B0">在配置定时任务时，如果不需要查看终端的结果，就让它自动关了吧；该配置在图形界面版本无效</font>）
- debug：开启调试（<font color="#9065B0">出现无法复现的错误时可以使用，非专业人士勿开启，产生日志会占用大量磁盘空间</font>）

**单页面备份的配置字段：**

- backup_token：notion官方API token（<font color="#9065B0">该token只需要读权限即可，获取方式参考备份教程视频</font>）
- page_id：需要备份的notion页面（<font color="#9065B0">注意token需要在该页面有读权限</font>）
- page_type：备份的页面类型（<font color="#9065B0">page/database，取决于你的page_id是从page的链接里拷贝出来的，还是从database的链接里拷贝出来的</font>）
- export_child_page：是否导出子页面（<font color="#9065B0">true/false，true的意思是导出所有的子页面，包括链接到的页面（链接到的页面有读权限即可导出）；false表示只有page_id对应的页面导出，另外对于其中的图片或者文件是否导出会有不可控的结果</font>）
- dump_path：备份的位置（<font color="#9065B0">基于当前程序位置，相对路径</font>）
- page_parser_type：页面解析类型（<font color="#9065B0">md/plain：md是markdown格式，plain是纯文本格式，page默认是markdown，填错时会选择默认值并且不提示</font>）
- db_parser_type：数据库解析类型（<font color="#9065B0">md/plain：md是markdown格式，plain是纯文本格式，database默认是plain，填错时会选择默认值并且不提示</font>）

**多页面备份的配置字段：**

- backup_token：导出页面需要invite此token（<font color="#9065B0">该token只需要读权限即可，获取方式参考备份教程视频</font>）
- backup_info_token：参数配置和备份日志页面需要invite此token（<font color="#9065B0">该token需要读写修改权限，</font><font color="#9065B0">**谨慎invite**</font>）
- backup_list_id：导出页面参数数据库的id（<font color="#9065B0">包含了所有需要备份页面的参数，参数解释见</font><font color="#9065B0">`单页面备份的配置字段`</font><font color="#9065B0">，基本一致，可以任意新增字段，但是修改现有的字段名需要和backup_list_map中的映射表同步修改</font>）
- backup_log_id：备份日志数据库的id（<font color="#9065B0">包含了备份的历史记录，不需要人为修改</font>）
- backup_list_map：导出页面参数数据库字段映射表（<font color="#9065B0">如果是直接duplicate的多页面备份模板，未修改数据库字段则不需要修改</font>）
- backup_log_map：备份日志数据库字段映射表（<font color="#9065B0">如果是直接duplicate的多页面备份模板，未修改数据库字段则不需要修改</font>）

**注意：**
1、这两类（多页面和单页面备份）都需要填写好配置 （毕竟除了你谁也不知道你想备份什么）
2、单页面备份和多页面备份在重新运行时，都会覆盖同一个备份目录（即如果需要对备份到本地的文件改动，请异动到别的位置，或者修改备份的位置）
3、单页面备份的页面参数在配置文件中；多页面备份需要备份的页面参数在Notion数据库中，需要备份的页面需要手动勾选

### 2.2.2 多页面**要**配置参数数据库

对于多页面的备份，备份参数的来源是notion中的一个Database，示例和模板如下（选中文版本）：

![多页面备份参数数据库](https://github.com/delta1037/notion-export-client/blob/main/img/database_args.png)

<font color="#D44C47">[多页面备份参数数据库模板](../child_pages/d90024f0d93d4038af703930468c1276.md)</font>

**注意：**

1、可随意新增字段/列（不与现有的字段（列）名冲突即可）
2、修改数据库中的字段（列）名，配置中的`backup_list_map`或者`backup_log_map`这两个字段（列）映射表需要同步修改

### 2.2.3 视频参考

注意上述的配置是将单页面和多页面综合起来的（之前是分离的，视频也是分离时录制的），但是配置过程基本不变（除了token的名称有变化）

[单页面备份操作视频](https://www.bilibili.com/video/BV1zr4y1Y7kt/)

[多页面备份操作视频](https://www.bilibili.com/video/BV1sP4y1P7aK/)

当你的单页面或者多页面运用的熟练之后（手动点击可以正常运行，即配置填写的没有问题），就可以选择是否进行定时自动备份了，下面是一份定时备份配置的教程：

[Window定时备份](https://www.bilibili.com/video/BV19u411C7cQ/)

## 2.3、运行

- 你如果拿到的是一个exe可执行文件（QQ群917606741内的notion-backup文件夹），那么在配置完成之后点击即可开始运行了。
- 你也下载源代码使用pyinstaller打包一个点击即运行的exe（或者其它平台）；或者直接在终端里运行脚本（`py notion_backup_terminal.py`）（见三、自行打包）

**备注：

**1、如果你在`dump.log`中发现以`[ISSUE]`开头的日志，可以在[此项目](https://github.com/delta1037/notion-export-client)中提交issue（或者向QQ群917606741告知），并向Email：geniusrabbit@qq.com发送客户端目录下的`dump.log`，**注意删除其中的token部分

**2、如果你发现备份下来的页面有内容丢失或者错误的问题，可以在[此项目](https://github.com/delta1037/notion-export-kernel)中提交issue（或者向QQ群917606741告知）

## 2.4、输出说明

备份位置下的结构为：

```plain text
 - child_pages/  # 所有的子页面（包括数据库中的子页面）
 - databases/    # 所有导出的数据库（包含csv和一个markdown格式的数据库页面辅助定位文件）
 - files/        # 所有的图片和文件
 main.md         # 下载页面id（作为主页存在）
```

该目录可以直接用`Typora`打开，或者用`Obsidian`打开。

# 三、自行打包

群内的文件夹更新的都是exe（Window系统适用），如果有朋友需要在MacOS上运行，可以自行按照如下的步骤进行打包。

## 3.1 下载源代码

源代码链接如下：

[LINK_PREVIEW](https://github.com/delta1037/notion-export-client)



可以打包的几个文件：（在下载的文件夹的根目录里）

```plain text
1、notion_backup_gui.py
2、notion_backup_terminal.py
```

这两个文件分别对应了上面两个版本（图形界面版本和命令行界面版本）

## 3.2 配置环境

1、检查python环境：（有就行，最好3.7以上）

```powershell
py --version
```

2、环境管理适用`virtualenv`工具，安装环境工具：

```powershell
py -3.7 -m pip install virtualenv
```

3、使用虚拟环境

```powershell
# 创建
py -m venv path_to_env
# 激活（这是powershell里面的激活命令，MacOS和这个估计不一样，自行查一下）
.\path_to_env\Scripts\Activate.ps1
# 退出
deactivate
```

4、安装必要的包（<font color="#D44C47">环境激活的状态下</font>）

```powershell
# 只有这一个依赖
pip install notion-dump-kernel
```

## 3.3 打包

对于上面每一个可以打包的文件，在开头都有类似如下的一段代码：

```plain text
# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller -F -c -i notion-dump.ico notion_backup_terminal.py -p api/notion_dump.py -p api/notion_dump_api.py -p api/backup_info.py
```

其中的打包代码部分，就是打包的指令。对于上述的实例，打包代码就是`pyinstaller -F -c -i notion-dump.ico notion_backup_terminal.py -p api/notion_dump.py -p api/notion_dump_api.py -p api/backup_info.py`，配置好代码运行环境之后，在终端里运行这段代码后即可。



当运行完成之后，dist文件夹里就是点击即可运行的软件了~



# 四、项目结构

- api/backup_info.py: 备份页面清单管理（修改清单备份状态，自动新增备份历史记录）
- api/notion_dump_api.py: 对`notion-dump-kernel`下载的文件重新组合位置并对文件中的链接（子页面、图片、文件）之类的重新定位
- api/notion_dump.py：选择多页面或者单页面备份
- notion_backup_terminal.py：命令行黑窗版本
- notion_backup_gui.py：一个极其简单的图形界面版本（点击开始即可运行）

