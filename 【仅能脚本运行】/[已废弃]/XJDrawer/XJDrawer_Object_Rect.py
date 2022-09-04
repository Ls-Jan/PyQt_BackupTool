
import numpy as np
from PyQt5.QtGui import QPainter,QColor,QPen

from XJDrawer_Object_Base import XJDrawer_Object_Base

__all__=['XJDrawer_Object_Rect']        

class XJDrawer_Object_Rect(XJDrawer_Object_Base):
    __matrix=None#为np.array对象，是个3xN矩阵(N=2)。用于点的平移缩放变换
    __color=(0,0,0)#颜色，默认黑
    __thick=1#线条粗细。如果是小于1的值就视为填充
    def __init__(self,L=0,T=0,R=0,B=0):#传入画布以及矩形的左上右下边界
        self.__matrix=np.array([[L,T,1],[R,B,1]],dtype=np.float)#不用整数是因为，若是使用了整数，在放大时设置位置会明显感到力不从心
    def SetLT(self,L,T):#只设置左上点的坐标
        self.__matrix[0]=[L,T,0]
    def SetRB(self,R,B):#只设置右下点的坐标
        self.__matrix[1]=[R,B,0]
    def GetLTRB(self):#返回矩形的左上右下
        return (*self.__matrix[0][:2],*self.__matrix[1][:2])
    def SetColor(self,color):#设置颜色(三元元组或者四元元组
        self.__color=color
    def SetThick(self,thick):#设置厚度(厚度小于1视为填充
        self.__thick=thick
    
    

    def Draw(self):#【重写】绘制矩形，这个供XJDrawer_Canvas调用
        canvas=self.GetCanvas()
        painter=QPainter(canvas)
        matrix=self.__matrix.dot(canvas.GetMatrix())
        matrix=matrix/matrix[-1][-1]
        matrix=matrix[:,:-1]
        L,T,R,B=*matrix[0],*matrix[1]
        area=(L,T,R-L,B-T)
        color=QColor(*self.__color)
        
        if(self.__thick>1):
            painter.setPen(QPen(color,self.__thick))
            painter.drawRect(*area)
        else:
            painter.fillRect(*area,color)
        
    def Sense(self,point):#【重写】检测点是否在范围内。point为坐标(二元元组)。
        point=self.TransformPoint(point)
        matrix=self.__matrix
        matrix=matrix[:,:-1]
        L,T,R,B=*matrix[0],*matrix[1]
        area=(L,T,R-L,B-T)
    def Interact(self,event):#【重写】响应鼠标事件。point为坐标(二元元组)，button和event分别对应MouseButton和MouseEvent。
        point=self.TransformPoint(point)
        matrix=self.__matrix
        matrix=matrix[:,:-1]
        L,T,R,B=*matrix[0],*matrix[1]
        area=(L,T,R-L,B-T)
        
        
        return True
        
        
    
        
        







