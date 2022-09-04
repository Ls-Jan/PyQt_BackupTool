
__version__='1.0.0'
__author__='Ls_Jan'

from abc import ABCMeta,abstractmethod
from enum import Enum
import numpy as np

__all__=['Object']



class Object(metaclass=ABCMeta):#以下所有函数都不允许外界直接调用。
    canvas=None#为XJDrawer_Canvas对象
    
    #【必须重写】
    @abstractmethod
    def Draw(self,painter,isMask=False):#绘制函数，要传入画笔。如果isMask为真则说明该画笔是用来绘制掩模的
        pass
    @abstractmethod
    def Rect(self):#返回对象在画布的范围位置(逻辑位置)，类型为QRect
        pass
    
    #【选择重写】
    def Sense(self,point):#检测点(逻辑位置)是否在范围内。point为坐标(二元元组)。
        return True
    def SetPosition(self,pos):#设置对象在画布的位置(逻辑位置)。默认不提供该功能(目前不想搞，所以没对其声明为“抽象方法”
        pass
    def Interact(self,mouseStatus):#响应鼠标事件。传入的是XJ_MouseStatus对象。如果传入None说明鼠标点击了其他地方
        pass
    def Tooltip_Show(self,mouseStatus):#设置鼠标悬浮显示tooltip。传入的是XJ_MouseStatus对象。
        pass
    def Tooltip_Hide(self):#设置鼠标悬浮隐藏tooltip。
        pass
    def Release(self):#将该对象从画布self.canvas中移除，并置self.canvas为None
        if(self.canvas):
            self.canvas.DelObject(self)
            self.canvas=None

