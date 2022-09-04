
__version__='1.0.0'
__author__='Ls_Jan'



import sys
from PyQt5.QtWidgets import QApplication,QPushButton,QWidget,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont,QPen,QColor

import XJFunc
from .BaseSystem import BaseSystem
from .FileSelect import FileSelect
from XJ_UsefulWidget import XJ_Tree
from XJ_UsefulWidget.UI import Drawer
from XJ_UsefulWidget.UI import XJ_TreeView

__all__=['BackupSystem']


class BackupSystem(QWidget):
    __bk=None#BaseSystem。丐版备份系统
    __fs=None#FileSelect。用来展示文件树的
    __cvtr=None#Drawer.Tree。用来展示备份节点的
    __cv=None#Drawer.Canvas。在这里不过是__cvtr的载具罢了

    strictRestore=False#严格恢复模式，恢复存档时如果该值为真那么会将与备份记录不一致的新增文件全部删去
    def __init__(self,path,parent=None):
        super().__init__(parent)
        self.__initWidget(path)
        self.resize(1400,800)
        self.__cv.SetView_Object(self.__cvtr)
    def __initWidget(self,path):
        backup=BaseSystem(path)
        cv=Drawer.Canvas(self)
        cvtr=Drawer.Tree(backup.GetArchiveTree())
        fs=FileSelect(self)

        cvtr.SetCurrentNode(backup.GetNodeIter_Curr())
        cv.AddObject(cvtr,1)
        fs.SetHideFunc(self.__func_fsHide)

        self.__bk=backup
        self.__cv=cv
        self.__cvtr=cvtr
        self.__fs=fs

        cvtr.func_switch=self.__func_recover
        cvtr.func_create=self.__func_create
        cvtr.func_delete=self.__func_delete
        cvtr.func_rename=self.__func_rename

    def resize(self,width,height):#重写一下
        self.__cv.setGeometry(0,0,width,height)
        self.__fs.setGeometry(width>>2,height>>2,width>>1,height>>1)
    def resizeEvent(self,event):#重写一下
        size=self.size()
        width=size.width()
        height=size.height()
        self.__cv.setGeometry(0,0,width,height)
        self.__fs.setGeometry(width>>2,height>>2,width>>1,height>>1)
        
    def __func_create(self,iter):#点击了创建按钮
        self.__cv.CreateMasking(color=(0,0,0,128))#创建蒙版，屏蔽点击
        self.__bk.SwitchNode_Focus(iter.GetIterPst())#存档树切换聚焦节点
        tree,selected,change=self.__bk.GetStructInfo_Path(create=True)#获取文件树、选中的节点、发生变动的节点集合
        self.__fs.SetFileTree(tree,selected,change)#设置树状图
        def func():
            self.__bk.CreateNode(tree,self.__fs.GetSelected())#存档树创建新节点(也就是创建备份)
            self.__cvtr.UpdateTree()
            self.__cvtr.SetCurrentNode(self.__bk.GetNodeIter_Curr())#切换画布存档树的当前节点
            #【此处需加上备份进度条窗口】
            self.__fs.hide()
        self.__fs.SetClickFunc('创建存档',func)
        self.__fs.show()
    def __func_recover(self,iter):#点击了恢复按钮(切换节点即为恢复存档)
        self.__cv.CreateMasking(color=(0,0,0,128))#创建蒙版，屏蔽点击
        self.__bk.SwitchNode_Focus(iter.GetIterPst())#存档树切换聚焦节点
        tree,selected,change=self.__bk.GetStructInfo_Path(recover=True)#获取文件树、选中的节点、发生变动的节点集合
        self.__fs.SetFileTree(tree,selected,change,restoreBackup=True)#设置FileSelect的树状图
        def func():#FileSelect的按钮回调函数
            self.__bk.SwitchNode_Curr(tree,self.__fs.GetSelected(),self.strictRestore)#存档树切换当前节点(也就是恢复备份)
            self.__cvtr.SetCurrentNode(self.__bk.GetNodeIter_Curr())#切换画布存档树的当前节点
            #【此处需加上备份进度条窗口】
            self.__fs.hide()
        self.__fs.SetClickFunc('恢复存档',func)
        self.__fs.show()
    def __func_rename(self,iter):#节点重命名
        pass
    def __func_delete(self,iter):#节点删除
        pass
    def __func_fsHide(self):#隐藏FileSelect窗口时调用的函数
        self.__fs.hide()
        self.__cv.CancelMasking()#撤销蒙版
        
        
        








        














