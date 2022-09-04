
__version__='1.0.0'
__author__='Ls_Jan'




import os
import sys
import json
from PyQt5.QtWidgets import QApplication,QMainWindow,QPushButton,QWidget,QVBoxLayout,QMenu,QMenuBar,QMessageBox
from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QFont,QPen,QColor

import XJFunc
from XJBackup import BackupSystem
from XJ_UsefulWidget.UI import XJ_SetView
from XJ_PathSelect import XJ_PathSelect
# import XJImporter


class MainSystem(QMainWindow):#总算做主系统了
    __bs=None#BackupSystem。备份系统
    __sv=None#XJ_SetView。用于显示可选的项目名
    __ps=None#XJ_PathSelect。用于选择路径
    
    __data='Data'#项目数据存放目录
    __newProjectName=None#新项目名
    def __init__(self,parent=None):
        super().__init__(parent)
        self.resize(1000,600)
        self.__InitData()
        self.__InitUI()
    def __InitData(self):
        if(not os.path.exists(self.__data)):
            try:
                os.makedirs(self.__data)
            except:
                QMessageBox.information(self,'初始化失败',f'请将程序所在路径下的名为{self.__data}的文件删除')
                exit()
    def __InitUI(self):
        #搞菜单栏(懒得去搜了，反正在自己以前的项目里有代码，直接复制改改多轻松
        menuBar = QMenuBar(self)
        self.setMenuBar(menuBar)
        #【项目】
        menuA=QMenu("项目",self)
        menuA.addAction("打开项目",self.__OpenProjectList)
        menuBar.addMenu(menuA)

        #搞控件
        self.__sv=XJ_SetView('项目')#XJ_SetView，用于项目列表的管理(暂不包括删除行为)
        self.__sv.rightClicked.connect(self.__OpenProject)#右键打开项目
        self.__sv.dataAltered.connect(self.__RenameProject)#项目重命名
        self.__sv.createData.connect(self.__CreateProject_Ready)#准备创建新项目
        self.__ps=XJ_PathSelect()#XJ_PathSelect，在新建项目时弹窗以选择路径
        self.__ps.confirm.connect(self.__CreateProject_Finish)#点击确认后完成项目的创建工作
        self.__ps.cancel.connect(self.__CreateProject_Cancel)#取消创建

        #阻挡其他窗口：https://blog.csdn.net/jxwzh/article/details/83686343
        self.__sv.setWindowModality(Qt.ApplicationModal)
        self.__ps.setWindowModality(Qt.ApplicationModal)

    def __CreateProject_Ready(self,path):#准备新建项目
        self.__ResizeWidget(self.__ps)
        self.__ps.show()
        self.__newProjectName=path
    def __CreateProject_Finish(self,source,backup):#创建项目完毕
        path=os.path.join(self.__data,self.__newProjectName)
        os.makedirs(path)
        path=os.path.join(path,'_paths.json')
        with open(path,'w') as f:
            f.write(json.dumps([source,backup], sort_keys=True, ensure_ascii=False, indent=2))
    def __CreateProject_Cancel(self):#取消项目的创建
        self.__sv.DeleteLastItem()#反悔
    def __RenameProject(self,old,new):#项目重命名
        os.rename(os.path.join(self.__data,old),os.path.join(self.__data,new))
    def __OpenProjectList(self):#打开项目列表用于选择项目
        data=set()
        for name in os.listdir(self.__data):
            path_dir=os.path.join(self.__data,name)
            path_json=os.path.join(path_dir,'_paths.json')
            if(os.path.isdir(path_dir)):
                if(os.path.isfile(path_json)):
                    data.add(name)
                    continue
            XJFunc.DeletePath(path_dir)
        self.__sv.SetData(data)
        self.__ResizeWidget(self.__sv)
        self.__sv.show()
    def __OpenProject(self,path):#打开项目。传入的是路径(目录)
        self.setCentralWidget(BackupSystem(os.path.join(self.__data,path)))
        self.__sv.hide()
    def __ResizeWidget(self,widget):#修改控件大小使其能够在主窗口居中(故技重施
        size=self.size()#窗口大小
        w=size.width()#宽
        h=size.height()#高
        x=w>>2#四分之一宽
        y=h>>2#四分之一高
        w=w>>1#二分之一宽
        h=h>>1#二分之一高
        if(widget.parent()==None):
            pos=self.pos()#窗口位置
            x=x+pos.x()
            y=y+pos.y()
        widget.setGeometry(x,y,w,h)
        widget.raise_()#让控件显示在最上面，避免被其他控件盖住




if __name__=='__main__':
    app = QApplication(sys.argv)
    system=MainSystem()
    system.show()
    sys.exit(app.exec())
    exit()














