
from abc import ABCMeta,abstractmethod
from enum import Enum
import numpy as np

class XJDrawer_Object_Base(metaclass=ABCMeta):#以下所有函数都不允许外界直接调用。
    __canvas=None

    #【必须重写】
    @abstractmethod
    def Draw(self):#绘制函数。
        pass
    @abstractmethod
    def Sense(self,point):#检测点是否在范围内。point为坐标(二元元组)。
        pass
    @abstractmethod
    def Interact(self,event):#响应鼠标事件。传入的是QtGui.QMouseEvent对象
        pass

    #【选择重写】
    def Tooltip_Show(self):#设置鼠标悬浮显示tooltip。
        pass
    def Tooltip_Hide(self):#设置鼠标悬浮隐藏tooltip。
        pass

    #【不需重写】
    def SetCanvas(self,canvas):#设置画布(canvas必须为XJDrawer_Canvas对象)
        self.__canvas=canvas
    def GetCanvas(self):#返回画布
        return self.__canvas
    def TransformPoint(self,point):#把屏幕坐标点(二元元组)转换为逻辑坐标点(二维numpy数组)。没设置canvas的话返回None
        canvas =self.__canvas
        if(canvas and type(point) is tuple):
            point=np.array([point])#转换为二维矩阵
            return point.dot(np.linalg.inv(canvas.GetMatrix()))#使用逆矩阵获取逻辑坐标
        else:
            return None



__all__=['XJDrawer_Object_Base']



