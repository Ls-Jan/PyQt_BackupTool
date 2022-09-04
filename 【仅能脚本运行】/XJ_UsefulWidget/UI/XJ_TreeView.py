
__version__='1.0.1'
__author__='Ls_Jan'

import sys
from types import MethodType
from PyQt5.QtCore import Qt,QModelIndex,QItemSelectionModel,pyqtSignal,QMimeData,Qt,QPoint,QVariant
from PyQt5.QtGui import QStandardItemModel, QStandardItem,QFont,QBrush,QColor
from PyQt5.QtWidgets import QTreeView,QAbstractItemView,QApplication

from XJImporter import XJImporter
Import =XJImporter(globals()).Import
Import('./source_TreeView')#使用qrc载入资源文件：https://blog.csdn.net/gongjianbo1992/article/details/105361880

__all__=['XJ_TreeView']


#部分内容仍待完善(修不动了，乏了乏了
class XJ_TreeView(QTreeView):
    doubleClicked=pyqtSignal()#槽信号，当前行双击时发送信号（如果行未发生变化则不发送
    rightClicked=pyqtSignal()#槽信号，右键时触发(多用于右键的自定义菜单)
    dataAltered=pyqtSignal(tuple)#槽信号，单元格内容发生变化时发送信号，返回一个元组，存放三个信息，依次是单元格所在行对应的迭代器、修改前的内容、修改后的内容。(dataChanged被QTreeView占用，只能起个其他名字
    #阻塞/恢复信号的方法：QObject.blockSignals(bool)：https://blog.csdn.net/qq_29787485/article/details/79233764
    
    __dataBeforeAlter=None#双击前的单元格内容
    class Iter:
        def __init__(self,item):
            path=[]#节点路径
            if(type(item)!=QStandardItemModel):
                index=item.index()
                while(index.isValid()):
                    path.append(index.row())
                    index=index.parent()
                path.reverse()
            self.__path=path
            self.__item=item
        def InsertRow(self,i,data):#向子级第i行插入数据(一个列表)，返回新行对应的迭代器。添加的新行是当前行的子级，不是同级关系。【【【单元格默认不可编辑】】】
            if(not self.IsValid()):
                return False
            lst=[]
            for d in data:
                lst.append(QStandardItem(str(d)))
            self.__item.insertRow(i,lst)
            XJ_TreeView.Iter(lst[0]).SetEditable(-1,False)
            return XJ_TreeView.Iter(lst[0])
        def AppendRow(self,data):#向子级最后一行添加数据(一个列表)，返回新行对应的迭代器。添加的新行是当前行的子级，不是同级关系。【【【单元格默认不可编辑】】】
            return self.InsertRow(self.__item.rowCount(),data)
        def DeleteRow(self,i):#删除子级第i行数据(如果该行数据有子级的话会一并被删除
            return self.IsValid() and self.__item.removeRow(i)
        def Copy(self):
            return XJ_TreeView.Iter(self.__item)
        def Back(self):#返回上一级(返回失败则返回false)
            item=self.__item
            if(self.IsRoot() or not self.__item.index().isValid()):
                return False
            if(self.__item.parent()==None):
                self.__item=self.__item.model()
            else:
                self.__item=self.__item.parent()
            self.__path.pop()
            return True
        def Next(self,i):#进入下一级(进入失败则返回false)
            if(self.IsValid()):
                if(0<=i<self.__item.rowCount()):
                    if(type(self.__item)!=QStandardItemModel):
                        self.__item=self.__item.child(i,0)
                    else:
                        self.__item=self.__item.itemFromIndex(self.__item.index(i,0))
                    self.__path.append(i)
                    return True
            return False
        def GetPath(self):#获取节点路径(列表)。如果该迭代器无效的话将返回None。不要对返回的列表进行修改
            return self.__path if self.IsValid() else None
        def GetData(self):#获取数据(一个列表)
            if(type(self.__item)!=QStandardItem):
                return []
            result=[]
            model=self.__item.model()
            index=self.__item.index().siblingAtColumn(0)
            i=1
            while(index.isValid()):
                result.append(model.itemFromIndex(index).text())
                index=index.siblingAtColumn(i)
                i+=1
            return result
        def GetCheckState(self,i):#获取复选框状态，返回结果为：【全选：Qt.Checked(2)、部分选：Qt.PartiallyChecked(1)、不选：Qt.Unchecked(0)、无复选框：None】
            item=self.__item
            if(type(item)==QStandardItemModel):
                return None
            index=item.index().siblingAtColumn(i)
            if(not index.isValid()):
                return None
            item=item.model().itemFromIndex(index)
            return item.checkState() if item.isCheckable() else None
        def GetNextCount(self):#获取子级元素个数
            return self.__item.rowCount()
        def SetData(self,i,data):#设置第i个单元格的内容(单元格不存在则返回false)
            if(type(self.__item)==QStandardItemModel):
                return False
            model=self.__item.model()
            index=self.__item.index().siblingAtColumn(i)
            if(index.isValid()==False):
                return False
            item=model.itemFromIndex(index)
            item.setText(str(data))
            return True
        def SetFont(self,i,font):#设置第i个单元格的字体样式，font类型为QFont。特别的，如果i为负数那么就对该行的所有单元格进行设置
            for item in self.__GetRowItems(i):
                item.setFont(font)
        def SetColor(self,i,fg=None,bg=None):#设置第i个单元格的字体前景背景颜色，fg和bg是形如(128,0,255)的三元/四元元组(传入None将不修改对应颜色)。特别的，如果i为负数那么就对该行的所有单元格进行设置
            #不搜的话鬼才知道怎么设文本颜色：https://www.cnblogs.com/hyq-lst/p/15860775.html
            for item in self.__GetRowItems(i):
                if(fg):
                    item.setForeground(QBrush(QColor(*fg)))
                if(bg):
                    item.setBackground(QBrush(QColor(*bg)))
        def SetCheckable(self,i,flag):#设置是否显示复选框(设置失败则返回false)。如果i为负数那么就对该行的所有单元格进行设置。
            for item in self.__GetRowItems(i):
                item.setCheckable(flag)
                if(not flag):#一个多小时喂狗之后，搜到了别人的解决办法：https://blog.csdn.net/xbnlkdbxl/article/details/53665943
                    item.setData(QVariant(),Qt.CheckStateRole)
        def SetCheckState(self,i,flag):#设置复选框状态(没有复选框则返回false)。复选框可选值：【全选：Qt.Checked(2)、部分选：Qt.PartiallyChecked(1)、不选：Qt.Unchecked(0)】
            index=self.__item.index().siblingAtColumn(i)
            if(not index.isValid()):
                return False
            item=self.__item.model().itemFromIndex(index)
            if(type(item)==QStandardItemModel or item.isCheckable()==False):
                return False
            item.setCheckState(flag)
            return True
        def SetEditable(self,i,flag):#设置第i个单元格可以双击修改，如果i为负数那么就对该行的所有单元格进行设置
            for item in self.__GetRowItems(i):
                item.setEditable(flag)
        def SetFunc_HasChildren(self,hasChildren):#设置是否有展开符号。hasChildren是个函数，参数为XJ_TreeView.Iter
            self.__item.hasChildren=MethodType(hasChildren,self)
        def IsValid(self):#判断迭代器是否有效。如果发生了除行增加之外的结构信息的变动(例如行删除、行移动)那么很可能导致迭代器失效。
            return self.IsRoot() or self.__item.index().isValid()
        def IsRoot(self):#判断是否为根节点
            return type(self.__item)==QStandardItemModel
        def __GetRowItems(self,i):#用于获取该行的对应单元格，如果i为负数则返回所有单元格。
            model=self.__item.model()
            lst=[]
            if(i<0):
                i=0
                while(True):#在Qt的TreeView里，你甚至无法获知一行里到底有多少个单元格
                    index=self.__item.index().siblingAtColumn(i)
                    if(not index.isValid()):
                        break
                    item=model.itemFromIndex(index)
                    lst.append(item)
                    i=i+1
            else:
                index=self.__item.index().siblingAtColumn(i)
                if(index.isValid()):
                    lst.append(model.itemFromIndex(index))
            return lst
        def item(self):#特殊用途，一般用不上
            return self.__item
            
    def __init__(self,parent=None):
        super(XJ_TreeView, self).__init__(parent)

        self.setSelectionMode(QAbstractItemView.ExtendedSelection)#支持Shift、Ctrl多选
#        self.setContextMenuPolicy(Qt.CustomContextMenu)#设置右键菜单策略。【说实话，没用，还不如修改鼠标单击事件】
        self.setModel(QStandardItemModel(self))
        self.__headerLables=[]
        self.__currIndex=None#记录双击选中的行
        # self.SetRowDragable(True)#设置行拖拽
        self.setDragDropMode(QAbstractItemView.InternalMove)#设置拖拽为移动而不是复制。默认模式是DragDrop(复制模式)
        self.__init_extra()#额外的初始化
        self.model().dataChanged.connect(self.__dataChanged)#单元格内容发生修改时发送槽信号
    def __init_extra(self):#额外的初始化
        #属实妖孽，只知道个hasChildren能够控制绘制展开符号：https://blog.csdn.net/fjb2080/article/details/7383429
        #但发现只修改QStandardItem.hasChildren压根不会有效果，鬼知道为啥QTreeView不会主动调用QStandardItem.hasChildren，就离谱
        model=self.model()
        def hasChildren(self,index):#绑定至model.hasChildren
            item=self.itemFromIndex(index)
            if(item):
                return item.hasChildren()
            else:
                return True
        model.hasChildren=MethodType(hasChildren,model)#绑定，将model.hasChildren重写

        #绘制分支：https://www.cnblogs.com/swarmbees/p/11312691.html
        #目的是让绘制的展开收回图标能够往右一些，以便分支线能一路拉到底
        #我搞不动啦！！！界面我懒得搞了
        # def drawBranches(self,painter,rect,index):#绘制分支
            # item=self.model().itemFromIndex(index)
        # self.drawBranches=MethodType(drawBranches,self)#绑定，将self.drawBranches重写

        #设置样式表：https://blog.csdn.net/weixin_33774883/article/details/90525753
        #从qrc中载入资源文件：https://www.cnblogs.com/xiaochuizi/p/10449053.html
        self.setStyleSheet("""
            QTreeView::branch:has-siblings:!adjoins-item {
                border-image: url(:/vline.png) 0;
            }

            QTreeView::branch:has-siblings:adjoins-item {
                border-image: url(:/branch-more.png) 0;
            }

            QTreeView::branch:!has-children:!has-siblings:adjoins-item {
                border-image: url(:/branch-end.png) 0;
            }

            QTreeView::branch:has-children:!has-siblings:closed,
            QTreeView::branch:closed:has-children:has-siblings {
                border-image: none;
                image: url(:/branch-closed.png);
            }

            QTreeView::branch:open:has-children:!has-siblings,
            QTreeView::branch:open:has-children:has-siblings  {
                border-image: none;
                image: url(:/branch-open.png);
            }
        """)

    def SetHeaderLabels(self,labels):#设置列头。labels为列表
        self.__headerLables=labels
        self.model().setHorizontalHeaderLabels(labels)
    def SetRowDragable(self,flag):#设置行可否拖拽(默认启用)
        # self.setDropIndicatorShown(flag)#显示拖拽位置【感觉这东西没用】
        self.setDragEnabled(flag)#开启向外拖拽
        self.setAcceptDrops(flag)#开启接收拖拽
    def SetColMovable(self,flag):#设置列可否拖拽(默认启用)：https://bbs.csdn.net/topics/394499097?list=lz
        self.header().setSectionsMovable(flag)
    def GetIter_Root(self):#返回根部迭代器
        return XJ_TreeView.Iter(self.model())
    def GetIter_ByPath(self,path):#根据传入的路径来返回迭代器，如果路径无效将返回根迭代器。路径格式形如[0,2,1,3,8]
        iter=self.GetIter_Root()
        for i in path:
            if(not iter.Next(i)):
                return self.GetIter_Root()
        return iter
    def GetCurrIter(self):#获取当前行的迭代器(不存在则返回None
        item=self.model().itemFromIndex(self.currentIndex())
        return XJ_TreeView.Iter(item) if item else None
    def GetCurrIters(self):#获取当前选中行的迭代器(列表，只不过没先后顺序)
        model=self.model()
        d={(i.row(),i.internalId()):i for i in self.selectedIndexes()}#同一行的单元格只返回一个迭代器
        return [XJ_TreeView.Iter(model.itemFromIndex(i)) for i in d.values()]
    def GetCursorIter(self,pos:QPoint):#获取坐标(一般传入鼠标坐标)对应行的迭代器
        XJ_TreeView.Iter(self.model().itemFromIndex(self.indexAt(pos)))
    def Clear(self):
        width=[]
        for i in range(self.model().columnCount()):
            width.append(self.columnWidth(i))
        self.model().clear()
        self.model().setHorizontalHeaderLabels(self.__headerLables)
        for i in range(len(width)):
            self.setColumnWidth(i,width[i])

    def mousePressEvent(self,event):
        super().mousePressEvent(event)
        if(event.button() == Qt.LeftButton):#如果是左键
            pass
        elif(event.button() == Qt.RightButton):#如果是右键
            if(self.model().itemFromIndex(self.currentIndex())):
                self.rightClicked.emit()
        else:#其他键
            pass
        event.accept()
    def mouseDoubleClickEvent(self,event):
        if(event.button() == Qt.LeftButton):#如果是左键
            super().mouseDoubleClickEvent(event)
            item=self.model().itemFromIndex(self.currentIndex())
            if(item):
                self.__dataBeforeAlter=item.text()
            self.doubleClicked.emit()
        elif(event.button() == Qt.RightButton):#如果是右键
            if(self.model().itemFromIndex(self.currentIndex())):
                self.rightClicked.emit()
        else:
            pass
        event.accept()
#    def dragEnterEvent(self, event):#【一】【拖拽进入组件内部时调用，判断该拖拽是否可accept，当accept后会进入dragMoveEvent】
#        if(event.source()==self):#仅接收控件内的拖拽，来自外部的拖拽一律禁止
#            event.accept()
    def dragMoveEvent(self, event):#【二】【成功进入到控件内部，在不停的拖拽中被反复调用直到鼠标松开。当event.ignore()时鼠标光标为禁止图标，并且释放拖拽并不会进入到dropEvent中】
        index=self.indexAt(event.pos())
        if(index.column()==0):#王八蛋个狗日东西，垃圾的要死。如果拖到非第一列的地方释放的话会出现数据丢失或者数据错位的情况，蠢得要死真的是绝了这啥破玩意儿
            event.accept()
        else:
            event.ignore()
    def dropEvent(self, event):#【三】【拖拽释放时调用】
        #个凑垃圾QTreeView，简直就是shi，做的啥玩意儿，封装一半不封装一半的，有些巴不得拿到手的功能找几十年结果是不暴露出来的是不是有病？
        super().dropEvent(event)

    def __dataChanged(self,index):#用于连接self.model().dataChange这个信号，以发送信号dataAltered
        before=self.__dataBeforeAlter
        if(type(before)!=None):#因为在QTreeView初始化的时候，QStandardItemModel.dataChanged会疯狂发出信号，就很恶心。当before不为None的时候早就完成初始化不怕翻车
            item=self.model().itemFromIndex(index)
            iter=self.Iter(item)
            after=item.text()
            self.dataAltered.emit((iter,before,after))

if __name__ == '__main__':
    app = QApplication(sys.argv)

    tv=XJ_TreeView()
    tv.resize(1000,600)
    tv.show()

    iter=tv.GetIter_Root()
    iter.AppendRow(['AAA','333']).AppendRow(['AAAAA','00000'])
    iter.AppendRow(['BBB','222'])
    iter.AppendRow(['BBB','222'])
    iter.AppendRow(['CCC','111'])
    iter.AppendRow(['XXX','xxx'])
    iter.AppendRow(['YYY','yyy'])
    iter.AppendRow(['ZZZ','zzz'])
    iter.AppendRow(['零零零'])

    iter=iter.AppendRow(['复选框','双击编辑'])
    # iter.AppendRow(['0']).AppendRow(['1']).AppendRow(['2']).AppendRow(['3'])
    iter.SetFont(-1,QFont('宋体',20))
    iter.SetColor(-1,(128,128,0),(0,255,255))
    iter.SetCheckable(0,True)#复选框(显示
    iter.SetCheckState(0,2)#复选状态(勾选
    # iter.SetCheckable(0,False)#复选框(隐藏
    iter.SetEditable(1,True)#双击可修改
    # print(tv.GetIter_ByPath([4]).GetData())
    iter.SetFunc_HasChildren(lambda iter:True)#添加展开符号，不愧是我
    # print(tv.GetIter_Root().GetNextCount())
    
    tv.dataAltered.connect(lambda data:print(data[0].GetPath()+[data[1:]]))
    # tv.rightClicked.connect(lambda :[print(iter.GetData()) for iter in tv.GetCurrIters()])
    tv.rightClicked.connect(lambda :[print(tv.GetCurrIter().GetNextCount())])
    # tv.rightClicked.connect(lambda :[print(iter.GetPath()) for iter in tv.GetCurrIters()])
    tv.doubleClicked.connect(lambda :print(tv.GetCurrIter().GetData()))
    tv.SetRowDragable(False)
    sys.exit(app.exec())


