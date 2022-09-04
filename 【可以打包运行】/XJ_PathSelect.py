
__version__='1.0.0'
__author__='Ls_Jan'



import os
import sys
from PyQt5.QtWidgets import QApplication,QWidget,QGridLayout,QPushButton,QLabel,QLineEdit,QFileDialog,QMessageBox
from PyQt5.QtCore import pyqtSignal,Qt

__all__=['XJ_PathSelect']

class XJ_PathSelect(QWidget):#路径选择器
    confirm=pyqtSignal(str,str)#槽信号，当路径有效并且点击了确认键后触发。两个字符串依次是源路径和备份路径
    cancel=pyqtSignal()#槽信号，当窗口关闭时调用
    __source=None#QLineEdit
    __backup=None#QLineEdit
    __finish=False
    def __init__(self,parent=None):
        super().__init__(parent)

        #一堆控件
        source_hint=QLabel('源路径：',self)#源路径
        source_path=QLineEdit('',self)
        source_btn=QPushButton('选择路径',self)
        backup_hint=QLabel('备份路径：',self)#备份路径
        backup_path=QLineEdit('',self)
        backup_btn=QPushButton('选择路径',self)
        confirm_btn=QPushButton('确认',self)#确认按钮
        
        #部分控件的设置
        source_path.setReadOnly(True)
        backup_path.setReadOnly(True)
        source_btn.clicked.connect(self.__click_source)
        backup_btn.clicked.connect(self.__click_backup)
        confirm_btn.clicked.connect(self.__click_confirm)
        
        #设置布局
        grid=QGridLayout(self)
        grid.addWidget(source_hint,0,0)#第一行
        grid.addWidget(source_path,0,1)
        grid.addWidget(source_btn,0,2)
        grid.addWidget(backup_hint,1,0)#第二行
        grid.addWidget(backup_path,1,1)
        grid.addWidget(backup_btn,1,2)
        grid.addWidget(confirm_btn,2,2)#第三行

        #保存部分控件(便于获取和修改路径
        self.__source=source_path
        self.__backup=backup_path

    def showEvent(self,event):
        self.__finish=False
    def closeEvent(self,event):
        if(not self.__finish):
            self.cancel.emit()
        
    def __click_source(self):
        path=QFileDialog.getExistingDirectory(self,"选择源目录")
        if(path):
            self.__source.setText(path)
    def __click_backup(self):
        path=QFileDialog.getExistingDirectory(self,"选择备份目录")
        if(path):
            self.__backup.setText(path)
    def __click_confirm(self):
        source=self.__source.text()
        backup=self.__backup.text()
        if(os.path.isdir(source) and os.path.isdir(backup) and source!=backup):
            self.confirm.emit(source,backup)
            self.__finish=True
            self.close()#直接关闭窗口(一次性的小玩具
        else:
            QMessageBox.information(self,'失败','路径无效')
            
            
if __name__=='__main__':
    app = QApplication(sys.argv)
    ps=XJ_PathSelect()
    ps.show()
    ps.cancel.connect(lambda:print("取消"))
    ps.confirm.connect(lambda A,B:print(A,B))
    sys.exit(app.exec())
    exit()




# if __name__=='__main__':
    # app = QApplication(sys.argv)
    # system=BackupSystem(r'C:\Users\Administrator\Desktop\XXX\Data')
    # system.show()
    # sys.exit(app.exec())
    # exit()

















