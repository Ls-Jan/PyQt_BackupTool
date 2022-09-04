

import sys
from PyQt5.QtGui import QPainter,QPen,QColor
from PyQt5.QtCore import Qt,QRect,QPoint,pyqtSignal,QEvent
from PyQt5.QtWidgets import QApplication,QWidget

from threading import Thread
import numpy as np
from time import time,sleep


class XJDrawer_Canvas(QWidget):#画布
#    clipChanged=pyqtSignal()#当选区发生变化时触发
    
    __matrix=None#转换矩阵
    __map_weight=None#绘制对象→权重
    __map_objects=None#下标(权重)→集合(绘制对象)
    __selected=None#被选中的对象
    __weights=None#省的一次次地对__map_objects的键进行排序然后遍历
    __tooltipVisible=False#tooltip是否处于显示中
    __Interval_doubleClick=None#两次点击小于此时间就视为双击。在创建对象时该值被固定
    __Interval_LongClick=0.5#长按的界定标准，松开鼠标时如果时间超过这个标准则视为长按。自然地，长按可以有“单击长按”和“双击长按”
    __Flag_doubleClick=False#专用于判断是否双击
    __time_click=None#单击时的时间，用于获取鼠标抬起时按下的时长
    def __init__(self,parent=None):
        super().__init__(parent)
        self.__map_objects=dict()
        self.__map_weight=dict()
        self.__selected=None
        self.__matrix=np.array([[1,0,0],[0,1,0],[0,0,1]])
        self.__Interval_doubleClick=QApplication.doubleClickInterval()/1000
        self.setMouseTracking(True)#时刻捕捉鼠标移动
        self.installEventFilter(self)#安装事件过滤器，以便函数eventFilter生效：https://www.jianshu.com/p/3ab51ed54622
        
    def AddObject(self,obj,weight):#添加绘制对象(必须继承XJDrawer_Object)，weight为权重(不小于0的整数)。权重越小越先被绘制
        if(type(weight)==int and weight>=0):
            self.DelObject(obj)#先移除一下再添加
            self.__map_weight[obj]=weight
            self.__map_objects.setdefault(weight,set()).add(obj)
            self.__SetWeights()
            obj.SetCanvas(self)
    def DelObject(self,obj):#移除绘制对象
        weig=self.__map_weight.get(obj)
        if(weig !=None):
            obj.SetCanvas(None)
            self.__map_weight.pop(obj)
            self.__map_objects[weig].remove(obj)
            self.__SetWeights()
            if(self.__selected==obj):
                self.__selected=None
    def GetObjectWeight(self,obj):#获取绘制对象的权重。为负值说明绘制对象没添加进画布中
        return self.__map_objects.get(obj,-1)
    def GetMatrix(self):#获取画布的转换矩阵
        return self.__matrix


    def paintEvent(self,event):
        objects=self.__map_objects
        for weig in self.__weights:#按权重依次绘制
            for obj in objects[weig]:
                obj.Draw()
        
    def mousePressEvent(self,event):
        self.__Flag_doubleClick=False
        self.__time_click=time()
        # Thread(target=self.__Click_Single,args=(event,)).start()
    def mouseDoubleClickEvent(self,event):
        self.__Flag_doubleClick=True
        self.__time_click=time()
        # Thread(target=self.__Click_Double,args=(event,)).start()
    def mouseReleaseEvent(self,event):
        if(self.__Estimate_LongClick()):#视为长按
            if(self.__Flag_doubleClick):
                self.__LongClick_Single(event)
            else:
                self.__Click_Double(event)
        else:#视为点击
            if(self.__Flag_doubleClick==False):
                self.__Click_Single(event)
            else:
                self.__LongClick_Double(event)
        print("松鼠",int(event.button()),"\n")
    def mouseMoveEvent(self,event):
        # print(event.pos())
        # print(int(event.buttons()))
        pass
    def eventFilter(self, obj, e):
        if(e.type()==QEvent.ToolTip and self.__selected):#tooltip可以自定义：https://www.cnblogs.com/zhiyiYo/p/16303940.html
            self.__selected.Tooltip_Show()
        else:
            return super().eventFilter(obj, e)



    def __SetWeights(self):#设置self.__weights
        self.__weights=sorted(self.__map_objects.keys())
    def __Estimate_LongClick(self):#判断——是否为长按
        return time()-self.__time_click>self.__Interval_LongClick
    def __Click_Single(self,event):
        sleep(self.__Interval_doubleClick)
        if(self.__Flag_doubleClick==False):
            # pos=event.pos()
            # print(int(event.button()))
            print("单击！！！")
    def __Click_Double(self,event):
        print("双击！！！")
        # print(int(event.button()))
    def __LongClick_Single(self,event):
        print("单击长按！！！")
    def __LongClick_Double(self,event):
        print("双击长按！！！")








from XJDrawer_Object_Rect import XJDrawer_Object_Rect

if __name__=='__main__':
    app = QApplication(sys.argv)

    cv= XJDrawer_Canvas()
    cv.show()
    r1=XJDrawer_Object_Rect(20,20,100,100)
    cv.AddObject(r1,1)

    sys.exit(app.exec())











