
__version__='1.0.0'
__author__='Ls_Jan'



import sys
from PyQt5.QtWidgets import QApplication,QPushButton,QWidget,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont,QPen,QColor

from XJImporter import XJImporter
Import=XJImporter(globals()).Import
Import('../XJFunc')
Import('../XJ_UsefulWidget.UI','XJ_TreeView')

__all__=['FileSelect']


class FileSelect(QWidget):#文件树显示+文件选择。一个树状图附上一个点击按钮。树状图显示四列数据，分别是：['文件名','修改时间','文件大小','备份时间']。
    __tv=None#XJ_TreeView
    __btn=None#QPushButton
    __fileNameOrder=lambda self,iter:(len(iter.GetIterData()),iter.GetIterPath()[-1])#对同级文件/目录的排序
    __hideFunc=lambda self:None#窗口隐藏时调用的函数
    __style={#风格样式：字体、前景色、背景色
        'normal':(QFont(),(0,0,0),(0,0,0,0)),
        'create':(QFont(),(0,255,0),(0,0,0,0)),#新增【绿色】
        'alter':(QFont(),(0,0,255),(0,0,0,0)),#修改【蓝色】
        'delete':(QFont(),(255,0,0),(0,0,0,0)),#删除【红色】
    }
    __cache=None#字典。XJ_TreeView迭代器路径→XJ_Tree迭代器的位置

    def __init__(self,parent=None):
        super().__init__(parent)
        tv=XJ_TreeView(self)
        btn=QPushButton(self)
        vbox=QVBoxLayout(self)
        tv.SetRowDragable(False)
        tv.SetColMovable(False)
        tv.rightClicked.connect(self.__InvertSelection)#右键反选
        tv.SetHeaderLabels(['文件名','修改时间','文件大小(kB)','备份时间'])
        tv.setColumnWidth(0,300)
        tv.setColumnWidth(1,200)
        tv.setColumnWidth(2,100)
        tv.setColumnWidth(3,200)
        btn.clicked.connect(lambda :None)
        vbox.addWidget(tv)
        vbox.addWidget(btn)
        self.__tv=tv
        self.__btn=btn
        self.__style=self.__style.copy()
        self.setWindowModality(Qt.ApplicationModal)#阻塞主窗口
        self.setWindowFlags(Qt.Drawer)#窗体无边界+去除任务栏图标
        # self.setStyleSheet("background-color:rgb(16,16,16)")#暂时别用，用了的话展开符号看不见
        # tv.header().setStyleSheet("QHeaderView::section{color:rgb(255,255,255);background-color:rgba(0,0,0,0)}")#把表头变黑
        self.resize(1000,600)

    def GetSelected(self):#返回选中节点的对应位置(集合)
        selected=set()
        iter=self.__tv.GetIter_Root()
        cache=self.__cache
        stack=[0]
        while(len(stack)):
            if(iter.Next(stack[-1])):
                stack[-1]=stack[-1]+1
                stack.append(0)
                if(iter.GetCheckState(0)):#被选中
                    selected.add(cache[tuple(iter.GetPath())])
            else:
                stack.pop()
                iter.Back()
        return selected
    def SetStyle(self,style):#style的格式和FileSelect.__style一致
        self.__style=style
    def SetFileNameOrder(self,func):#设置对同级文件/目录的排序关键词，func传入一个列表参数，列表对应着树状图显示的一行数据
        self.__fileNameOrder=func
    def SetFileTree(self,tree,set_selected=set(),dict_change=dict(),restoreBackup=False):#tree为XJ_Tree，sets_alter为BaseSystem.GetSelected返回的字典，restoreBackup为真时如果该文件没有备份记录则不提供复选框
        self.__tv.Clear()
        self.__cache={}
        iter_tv=self.__tv.GetIter_Root()
        iter_tr=tree.GetIter_Root()
        stack=[sorted(iter_tr.GetNextIters().values(),key=self.__fileNameOrder)]
        cache=self.__cache
        while(len(stack)):
            if(len(stack[-1])>0):
                iter_tr=stack[-1].pop()
                data=iter_tr.GetIterData().copy()
                isFolder=len(data)==1#目录的话就只有“修改时间”这一份数据，列表长度为1
                noBackup=len(data)==2#如果没有备份记录的话就只有“修改时间”和“文件大小”这两份数据，列表长度为2
                while(len(data)<3):
                    data.append('')
                row=iter_tr.GetIterPath()[-1:]
                row.append(XJFunc.GetFormatTime(data[0]))
                row.extend(data[1:])
                iter_tv=iter_tv.AppendRow(row)
                # for iter in iter_tr.GetNextIters().values():
                    # print(iter.GetIterPath(),iter.GetIterData())
                stack.append(sorted(iter_tr.GetNextIters().values(),key=self.__fileNameOrder))

                pst=iter_tr.GetIterPst()
                cache[tuple(iter_tv.GetPath())]=pst
                iter_tv.SetCheckable(0,True)
                iter_tv.SetCheckState(0,2 if pst in set_selected else 0)
                if(isFolder):
                    iter_tv.SetFunc_HasChildren(lambda iter:True)
                if(restoreBackup and (noBackup or isFolder)):
                    iter_tv.SetCheckable(0,False)
                if(pst in dict_change.setdefault('create',set())):
                    style=self.__style['create']
                elif(pst in dict_change.setdefault('delete',set())):
                    style=self.__style['delete']
                    if(not restoreBackup):#如果不是恢复存档的话就禁用复选框
                        iter_tv.SetCheckable(0,False)#禁用复选框
                elif(pst in dict_change.setdefault('alter',set())):
                    style=self.__style['alter']
                else:
                    style=self.__style['normal']
                iter_tv.SetFont(-1,style[0])
                iter_tv.SetColor(-1,*style[1:])
            else:
                iter_tr.MoveBack()
                iter_tv.Back()
                stack.pop()
    def SetClickFunc(self,text,func):#设置按钮的文本和回调函数(无参)
        self.__btn.setText(text)
        self.__btn.clicked.disconnect()
        self.__btn.clicked.connect(func)
    def SetHideFunc(self,func):#设置窗口隐藏时调用的函数(无参)
        self.__hideFunc=func

    def showEvent(self,event):#人为实现窗口居中(既然QWidget不提供类似于QMainWindow.setCentralWidget的函数那我也只能这么做了
        parent=self.parent()
        if(parent):
            while(parent.parent()):
                parent=parent.parent()#找到真正的父窗口为止
            pos=parent.pos()#窗口位置
            size=parent.size()#窗口大小
            w=size.width()#宽
            h=size.height()#高
            w=w>>2#四分之一宽
            h=h>>2#四分之一高

            x=pos.x()+w
            y=pos.y()+h
            w=w<<1
            h=h<<1
            self.setGeometry(x,y,w,h)
    def hideEvent(self,event):
        self.__hideFunc()
    
    def __InvertSelection(self):#将选中的行进行反选
        for iter in self.__tv.GetCurrIters():
            iter.SetCheckState(0,0 if iter.GetCheckState(0) else 2)
        
        
        
        
        
        
        
        
        




        

if __name__=='__main__':
    app = QApplication(sys.argv)
    Import('../XJ_UsefulWidget','XJ_Tree')
    fs=FileSelect()
    fs.show()
    fs.SetHideFunc(lambda:exit())
    sys.exit(app.exec())

















