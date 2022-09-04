
__version__='1.0.0'
__author__='Ls_Jan'


import os
import sys
from PyQt5.QtWidgets import QApplication,QWidget,QVBoxLayout
from PyQt5.QtCore import pyqtSignal,Qt


from XJImporter import XJImporter
Import =XJImporter(globals()).Import
Import('./XJ_TreeView','*')#使用qrc载入资源文件：https://blog.csdn.net/gongjianbo1992/article/details/105361880

__all__=['XJ_SetView']

class XJ_SetView(QWidget):#显示集合，并允许对元素重命名(出现重名则重命名失败)。不允许出现空白名称
    rightClicked=pyqtSignal(str)#槽信号，右键触发，返回选中元素的名称
    dataAltered=pyqtSignal(str,str)#槽信号，重命名时触发，返回重命名前和重命名后的字串
    createData=pyqtSignal(str)#槽信号，创建新元素时触发
    __tv=None#XJ_TreeView
    __set=None#集合
    def __init__(self,rowName='',parent=None):
        super().__init__(parent)
        tv=XJ_TreeView(parent)        
        tv.SetHeaderLabels([rowName])
        tv.header().setDefaultAlignment(Qt.AlignCenter)#列标题文本居中
        tv.dataAltered.connect(self.__dataAltered)#重命名
        tv.rightClicked.connect(self.__rightClick)#右键触发信号
        tv.setRootIsDecorated(False)#删除左侧空白使其成为列表：https://mlog.club/article/1161025
        tv.SetRowDragable(False)#禁用拖拽
        vbox=QVBoxLayout(self)
        vbox.addWidget(tv)
        vbox.setContentsMargins(0,0,0,0)#把四周的空白填满。关键词spacing和margins：https://blog.csdn.net/groundhappy/article/details/52020779(博客仅标题有含金量，内容多半又是从哪复制来的
        self.__tv=tv
        self.__AddItem('')
        
    def Clear(self):#清空集合
        self.__tv.Clear()
        self.__AddItem('')
    def GetData(self):#获取集合(不要对返回内容进行修改
        return self.__set
    def SetData(self,data):#设置集合，data为可迭代对象(可以传入列表、字典、集合
        self.__tv.Clear()
        data=[str(d) for d in data]
        data=sorted(filter(lambda key:len(key.strip())>0,data))#删除掉空字串，并且排序一下(虽然不排序也没啥
        self.__set=set(data)
        
        data.append('')#最后一行为空白行，另做他用
        for d in data:
            self.__AddItem(d)
    def DeleteLastItem(self):#移除最后一个元素。该函数主要用于创建元素后进行反悔操作
        iter=self.__tv.GetIter_Root()
        pst=iter.GetNextCount()-2
        if(pst>=0):
            iter.Next(pst)
            self.__set.remove(iter.GetData()[0])
            iter.Back()
            iter.DeleteRow(pst)

    def __rightClick(self):#右键鼠标时调用
        data=self.__tv.GetCurrIter().GetData()[0].strip()
        if(data):
            self.rightClicked.emit(data)
    def __dataAltered(self,data):#信息发生变化时调用
        iter,before,after=data
        after=after.strip()
        if(not after or after in self.__set):#如果重名，或者命名为空串，就将其取消
            iter.SetData(0,before)
        else:
            iter.SetData(0,after)
            self.__set.add(after)
            if(before):#如果before不为空，说明是重命名
                self.dataAltered.emit(before,after)#发送修改信号
            else:#为空说明是对最后一个元素进行修改的，意为增添新元素
                iter=self.__tv.GetIter_Root()
                iter.Next(iter.GetNextCount()-1)
                self.__tv.blockSignals(True)#暂时关闭信号(谁又能知道，设置单元格颜色一样会触发dataChanged信号
                iter.SetColor(0,bg=(255,255,255))#重新染白
                self.__tv.blockSignals(False)#重新打开信号
                self.__AddItem('')
                self.createData.emit(after)
    def __AddItem(self,item):
        self.__tv.blockSignals(True)#暂时关闭信号
        iter=self.__tv.GetIter_Root().AppendRow([item])
        iter.SetEditable(0,True)
        if(not item):#如果为空，说明是表尾元素，稍微染下色
            iter.SetColor(0,bg=(192,255,255))
        iter.item().setTextAlignment(Qt.AlignCenter)#单元格居中
        self.__tv.blockSignals(False)#重新打开信号
            
if __name__=='__main__':
    app = QApplication(sys.argv)
    sv=XJ_SetView('列名')
    sv.show()
    sv.SetData([1,2,3,4,5])
    sv.DeleteLastItem()
    sv.createData.connect(lambda key:print(key))
    sys.exit(app.exec())
    exit()

















