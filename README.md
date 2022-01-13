# notion-dump

基于notion-dump-kernel的一个实例

## 描述

- [ ] 对递归下载的notion指定页面将其中的链接重定位
- [ ] 

## 使用

- 填写token
- 填写需要下载的页面id和下载的位置（也可以多对，使用CSV文件或者Excel表格传入）

## 输出

下载主目录由用户决定，主目录下结构为
```powershell
- child_pages/  # 所有的子页面
- databases/    # 所有的数据库导出
main.md         # 下载页面id
```

## 记录

- 根据主页id处理主页相关内容（将子页面替换为CSV或者md的本地链接）
- 递归处理子页面（子页面列表，递归处理子页面中的子页面）