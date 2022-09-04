
from abc import ABCMeta,abstractmethod
from enum import Enum
import numpy as np

class XJDrawer_Object_Base(metaclass=ABCMeta):#以下所有函数都不允许外界直接调用。
    __canvas=None#为XJDrawer_Canvas对象
    
    
    
    #【必须重写】
    @abstractmethod
    def Draw(self):#绘制函数。
        pass
    @abstractmethod
    def Interact(self,mouseStatus):#响应鼠标事件。传入的是XJ_MouseStatus对象。如果传入None说明鼠标点击了其他地方
        pass
    @abstractmethod
    def Rect(self):#返回对象在画布的位置(逻辑位置)，类型为QRect
        pass
    
    #【选择重写】
    def Sense(self,point):#检测点(逻辑位置)是否在范围内。point为坐标(二元元组)。
        return True
    def SetPosition(self,pos):#设置对象在画布的位置(逻辑位置)。默认不提供该功能(目前不想搞，所以没对其声明为“抽象方法”
        pass
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
            point=np.array([*point,1])#转换为二维矩阵
            return point.dot(canvas.GetMatrix_Inv())#使用逆矩阵获取逻辑坐标
        else:
            return None



__all__=['XJDrawer_Object_Base']



