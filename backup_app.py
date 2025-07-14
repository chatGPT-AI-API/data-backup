import wx
import shutil
import os
from datetime import datetime
import zipfile

class BackupFrame(wx.Frame):
    """主程序窗口，用于备份应用数据"""
    
    def __init__(self):
        super().__init__(None, title='应用数据备份工具', size=wx.Size(400, 300))
        self.panel = wx.Panel(self)
        self.init_ui()
        self.Centre()
        self.Show()

    def init_ui(self):
        """初始化界面组件"""
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        # 源目录选择
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        label_src = wx.StaticText(self.panel, label="源目录：")
        hbox1.Add(label_src, flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=5)
        self.src_dir = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        btn_choose_src = wx.Button(self.panel, label='选择源目录')
        btn_choose_src.Bind(wx.EVT_BUTTON, self.on_choose_src)
        hbox1.Add(self.src_dir, proportion=1, flag=wx.EXPAND)
        hbox1.Add(btn_choose_src, flag=wx.LEFT, border=5)

        # 目标目录选择
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        label_dest = wx.StaticText(self.panel, label="目标目录：")
        hbox2.Add(label_dest, flag=wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, border=5)
        self.dest_dir = wx.TextCtrl(self.panel, style=wx.TE_READONLY)
        btn_choose_dest = wx.Button(self.panel, label='选择目标目录')
        btn_choose_dest.Bind(wx.EVT_BUTTON, self.on_choose_dest)
        hbox2.Add(self.dest_dir, proportion=1, flag=wx.EXPAND)
        hbox2.Add(btn_choose_dest, flag=wx.LEFT, border=5)

        # 加密选项
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        self.encrypt_cb = wx.CheckBox(self.panel, label='加密备份')
        hbox3.Add(self.encrypt_cb, flag=wx.ALL, border=5)
        
        # 备份按钮
        btn_backup = wx.Button(self.panel, label='开始备份')
        btn_backup.Bind(wx.EVT_BUTTON, self.on_backup)

        vbox.Add(hbox1, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox2, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(hbox3, flag=wx.EXPAND|wx.ALL, border=10)
        vbox.Add(btn_backup, flag=wx.ALIGN_CENTER|wx.TOP, border=20)

        self.panel.SetSizer(vbox)

    def on_choose_src(self, event):
        """处理源目录选择事件"""
        dlg = wx.DirDialog(self, "选择需要备份的源目录")
        if dlg.ShowModal() == wx.ID_OK:
            self.src_dir.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_choose_dest(self, event):
        """处理目标目录选择事件"""
        dlg = wx.DirDialog(self, "选择备份保存目录")
        if dlg.ShowModal() == wx.ID_OK:
            self.dest_dir.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_backup(self, event):
        """执行备份操作"""
        src = self.src_dir.GetValue()
        dest = self.dest_dir.GetValue()
        encrypt = self.encrypt_cb.GetValue()
        password = None

        if not src or not dest:
            wx.MessageBox('请先选择源目录和目标目录', '错误', wx.OK|wx.ICON_ERROR)
            return
            
        if encrypt:
            dlg = wx.TextEntryDialog(self, '请输入加密密码', '密码输入')
            if dlg.ShowModal() == wx.ID_OK:
                password = dlg.GetValue().encode('utf-8')
            dlg.Destroy()
            if not password:
                return

        try:
            # 创建带时间戳的备份目录
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"backup_{timestamp}"
            backup_path = os.path.join(dest, backup_name)
            os.makedirs(backup_path, exist_ok=True)

            # 复制文件
            for item in os.listdir(src):
                s = os.path.join(src, item)
                d = os.path.join(backup_path, item)
                if os.path.isdir(s):
                    shutil.copytree(s, d)
                else:
                    shutil.copy2(s, d)

            # 创建压缩包
            zip_path = os.path.join(dest, f"{backup_name}.zip")
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if encrypt and password:
                    zipf.setpassword(password)
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        zipf.write(file_path, os.path.relpath(file_path, dest))

            wx.MessageBox(f'备份成功！\n保存路径: {zip_path}' +
                         ('\n已启用加密保护' if encrypt else ''),
                         '完成', wx.OK|wx.ICON_INFORMATION)

        except Exception as e:
            wx.MessageBox(f'备份失败: {str(e)}', '错误', wx.OK|wx.ICON_ERROR)

if __name__ == '__main__':
    app = wx.App()
    BackupFrame()
    app.MainLoop()