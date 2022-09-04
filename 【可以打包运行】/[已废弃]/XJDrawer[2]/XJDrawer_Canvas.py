

import sys
from PyQt5.QtGui import QPainter,QPen,QColor
from PyQt5.QtCore import Qt,QRect,QPoint,pyqtSignal,QEvent
from PyQt5.QtWidgets import QApplication,QWidget

from threading import Thread
import numpy as np
from time import time,sleep

from XJ_MouseStatus import XJ_MouseStatus

class XJDrawer_Canvas(QWidget):#画布
#    clipChanged=pyqtSignal()#当选区发生变化时触发
    class __PosRange:#用于快速筛选可能点击到的对象。当绘制对象的位置发生变化时，必须将其移除然后再重新添加以更新数据
        class __Mapping:
            __list=[]#便于快速查找。元素升序
            __map={}#位置→对象集合
            def __init__(self):
                self.__list=self.__list.copy()
                self.__map=self.__map.copy()
            def AddObject(self,pos,obj):#记录绘制对象
                if(pos in self.__map):
                    if(obj not in self.__map[pos]):
                        self.__map[pos].add(obj)
                else:
                    if(len(self.__list)):
                        self.__list.insert(self.__binarySearch(pos),pos)
                    else:
                        self.__list.append(pos)
                    self.__map[pos]={obj}
            def DelObject(self,pos,obj):#移除相应记录
                set_obj=self.__map[pos]
                if(obj in set_obj):
                    set_obj.remove(obj)
                    if(len(set_obj)==0):
                        self.__list.pop(self.__binarySearch(pos))
            def SearchObject(self,pos,less):#搜寻符合条件的对象集合。LeftSide为真代表返回小于等于pos的对象集合，反之则返回大于等于pos的
                index=self.__binarySearch(pos)
                lst=self.__list
                rst=set()
                for i in range(*((0,index) if less else (max(0,index),len(lst)))):
                    rst.update(self.__map[lst[i]])
                if(less and 0<=index<len(lst) and lst[index]==pos):
                    rst.update(self.__map[lst[index]])
                return rst
            def __binarySearch(self,pos):#二分查找。特别的，pos小于最小值会返回-1，大于最大值会返回len(self.__list)。不处理self.__list为空的情况
                lst=self.__list
                L=0
                R=len(lst)-1
                M=(L+R)>>1
                if(pos<lst[L]):
                    return L-1
                elif(pos>lst[R]):
                    return R+1
                
                while(L+1<R):
                    M=(L+R)>>1
                    if(lst[M]>pos):
                        R=M
                    elif(lst[M]<pos):
                        L=M
                    else:
                        break
                if(len(lst)>0):
                    absR=abs(lst[R]-pos)
                    absM=abs(lst[M]-pos)
                    absL=abs(lst[L]-pos)
                    tmp=(L,absL) if absL<absR else (R,absR)
                    if(tmp[1]<absM):
                        absM=tmp[0]
                
                return M
        __L=None#__Mapping类型，下面三个数据也一样
        __R=None
        __T=None
        __B=None
        def __init__(self):
            self.__L=self.__Mapping()
            self.__R=self.__Mapping()
            self.__T=self.__Mapping()
            self.__B=self.__Mapping()
        def AddObject(self,obj):#加入对象
            rect=obj.Rect()
            self.__L.AddObject(rect.left(),obj)
            self.__R.AddObject(rect.right(),obj)
            self.__T.AddObject(rect.top(),obj)
            self.__B.AddObject(rect.bottom(),obj)
        def DelObject(self,obj):#移除对象
            rect=obj.Rect()
            self.__L.DelObject(rect.left(),obj)
            self.__R.DelObject(rect.right(),obj)
            self.__T.DelObject(rect.top(),obj)
            self.__B.DelObject(rect.bottom(),obj)
        def SearchObject(self,pos):#根据二维坐标(二元元组)搜寻对象，返回的是对象集合
            posX,posY=pos
            L=self.__L.SearchObject(posX,True)
            R=self.__R.SearchObject(posX,False)
            T=self.__T.SearchObject(posY,True)
            B=self.__B.SearchObject(posY,False)
            # print(L)
            # print(R)
            # print(T)
            # print(B)
            return L.intersection(R).intersection(T).intersection(B)


    __matrix=None#转换矩阵，逻辑坐标→显示坐标
    __matrix_inv=None#逆转换矩阵，显示坐标→逻辑坐标
    __map_weight=None#绘制对象→权重
    __map_objects=None#权重→集合(绘制对象)
    __selected=None#被单击选中的对象
    __weights=None#权重列表。省的一次次地对__map_objects的键进行排序然后遍历
    __posRange=None#用于快速筛选可能点击到的绘制对象(__PosRange)
    __last_clickPos=None#最近一次按下的位置(2-tuple)。虽然可以通过__mouseStatus来获取，但挺麻烦的，而且mouseMoveEvent调用频率挺高，应该尽可能减少耗时
    __tooltipVisible=False#tooltip是否处于显示中
    __mouseStatus=None#鼠标状态记录器(XJ_MouseStatus)
    def __init__(self,parent=None):
        super().__init__(parent)
        self.__mouseStatus=XJ_MouseStatus()
        self.__map_objects=dict()
        self.__map_weight=dict()
        self.__selected=None
        self.__matrix=np.array([[1,0,0],[0,2,0],[0,0,1]])
        self.__matrix_inv=np.linalg.inv(self.__matrix)
        self.__posRange=self.__PosRange()
        self.__mouseStatus.longClick.connect(self.__longClick)
        self.setMouseTracking(True)#时刻捕捉鼠标移动。得在mouseMoveEvent里对__mouseStatus进行更新
        self.installEventFilter(self)#安装事件过滤器，以便函数eventFilter生效：https://www.jianshu.com/p/3ab51ed54622
        
    def AddObject(self,obj,weight):#添加绘制对象(必须继承XJDrawer_Object)，weight为权重(不小于0的整数)。权重越小越先被绘制(也就是垫底)
        if(type(weight)==int and weight>=0):
            self.DelObject(obj)#先移除一下再添加
            self.__posRange.AddObject(obj)
            self.__map_weight[obj]=weight
            self.__map_objects.setdefault(weight,set()).add(obj)
            self.__setWeights()
            obj.SetCanvas(self)
    def DelObject(self,obj):#移除绘制对象
        weig=self.__map_weight.get(obj)
        if(weig !=None):
            obj.SetCanvas(None)
            self.__posRange.DelObject(obj)
            self.__map_weight.pop(obj)
            self.__map_objects[weig].remove(obj)
            self.__setWeights()
            if(self.__selected==obj):
                self.__selected=None
    def GetObjectWeight(self,obj):#获取绘制对象的权重。为负值说明绘制对象没添加进画布中
        return self.__map_objects.get(obj,-1)
    def GetMatrix(self):#获取画布的转换矩阵
        return self.__matrix
    def GetMatrix_Inv(self):#获取画布的逆转换矩阵
        return self.__matrix_inv

    def mousePressEvent(self,event):
        mouseStatus=self.__mouseStatus
        mouseStatus.UpdateStatus(event)#更新鼠标状态
        status=self.__mouseStatus.GetStatus()#获取鼠标信息
        obj=self.__Sense()#获取感应到的控件

        if(self.__selected!=obj):#点到了别的地方
            if(status.click==status.ClickType.Double):#双击
                mouseStatus.ClearStatus()#清空记录
                mouseStatus.UpdateStatus(event)#重新更新鼠标状态(目的是设置为单击状态
            if(self.__selected):
                self.__selected.Interact(None)#传入空值，旨在通知其失去了选中状态
            self.__selected=obj
        if(obj):
            obj.Interact(mouseStatus)#对其作出响应
        self.__last_clickPos=status.pos
    def mouseReleaseEvent(self,event):
        self.__mouseStatus.UpdateStatus(event)#更新鼠标状态
    def mouseMoveEvent(self,event):
        self.__mouseStatus.UpdateStatus(event)#更新鼠标状态
        
        
    def paintEvent(self,event):
        objects=self.__map_objects
        for weig in self.__weights:#按权重依次绘制
            for obj in objects[weig]:
                obj.Draw()
    def eventFilter(self, obj, e):#主要为了tooltip的自定义：https://www.cnblogs.com/zhiyiYo/p/16303940.html
        if(self.__selected !=None):#如果有对象被选中
            if(self.__selected==self.__Sense()):#如果鼠标当前位置在被选中的对象上
                if(e.type()==QEvent.ToolTip):#如果是tooltip事件
                    if(self.__tooltipVisible==False):#如果tooltip没显示(为了避免多次调用Tooltip_Show函数
                        self.__selected.Tooltip_Show()#显示tooltip
                        self.__tooltipVisible=True
                        return True
            else:#鼠标不在被选中的对象上
                if(self.__tooltipVisible):#如果tooltip显示中(为了避免多次调用Tooltip_Hide函数
                    self.__selected.Tooltip_Hide()
                    self.__tooltipVisible=False
                    return True
        return super().eventFilter(obj, e)
    def __logicalClickPos(self,pos):#根据屏幕点击坐标返回逻辑点击坐标
        pos=np.array([*pos,1])
        mat=pos.dot(self.__matrix_inv)
        return tuple(mat[:2])
    def __setWeights(self):#设置self.__weights
        self.__weights=sorted(self.__map_objects.keys())
    def __longClick(self):#长按的回调函数
        if(self.__selected):
            self.__selected.Interact(self.__mouseStatus)
    def __Sense(self):#获取鼠标所指的对象(没有则返回None
        status=self.__mouseStatus.GetStatus()#获取鼠标信息
        pos=self.__logicalClickPos(status.pos)#获取逻辑坐标
        lst=self.__posRange.SearchObject(pos)#一般来说，重合在一起的对象少之又少
        lst=[(obj,self.__map_weight[obj]) for obj in lst]
        lst.sort(key=lambda item:item[1],reverse=True)#以权重进行从大到小排序
        lst=[obj for obj in map(lambda item:item[0],lst) if obj.Sense(pos)]+[None]#调用obj.Sense来获取实际感应到的对象
        return lst[0]







from XJDrawer_Object_Rect import XJDrawer_Object_Rect

if __name__=='__main__':
    app = QApplication(sys.argv)

    cv= XJDrawer_Canvas()
    cv.show()
    r1=XJDrawer_Object_Rect(20,20,100,100)
    cv.AddObject(r1,1)
    # cv.setToolTip("ABC")

    sys.exit(app.exec())











