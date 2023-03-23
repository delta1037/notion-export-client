# author: delta1037
# Date: 2022/05/01
# mail:geniusrabbit@qq.com
# 打包代码 pyinstaller notion_backup_gui.spec
import webview
from Flask.app import app, bootstrap

if __name__ == "__main__":
    window = webview.create_window(
        title='Notion备份程序',
        url=app,
        # confirm_close=True,  # 退出时提示
        width=1200,
        height=850
    )
    # 自定义退出提示的中文内容
    cn = {
        'global.quitConfirmation': u'确定关闭?'
    }
    webview.start(localization=cn, gui='gtk')

    # 网页测试
    # app.run(debug=True)
