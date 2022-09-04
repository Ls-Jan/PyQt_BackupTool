
import numpy as np
from PyQt5.QtGui import QPainter,QColor,QPen
from PyQt5.QtCore import QRect

from XJDrawer_Object_Base import XJDrawer_Object_Base

__all__=['XJDrawer_Object_Rect']        

class XJDrawer_Object_Rect(XJDrawer_Object_Base):
    __matrix=None#为np.array对象，是个3xN矩阵(N=2)。用于点的平移缩放变换
    __color_fill=(0,255,255,128)#颜色
    __color_border=(0,0,0)#边界颜色
    __thick=1#边界粗细
    def __init__(self,L=0,T=0,R=0,B=0):#传入画布以及矩形的左上右下边界
        # self.__matrix=np.array([[L,T,1],[R,B,1]],dtype=np.float)#不用整数是因为，若是使用了整数，在放大时设置位置会明显感到力不从心
        self.__matrix=np.array([[L,T,1],[R,B,1]])
    # def SetLT(self,L,T):#只设置左上点的坐标
        # self.__matrix[0]=[L,T,0]
    # def SetRB(self,R,B):#只设置右下点的坐标
        # self.__matrix[1]=[R,B,0]
    def GetLTRB(self):#返回矩形的左上右下
        return (*self.__matrix[0][:2],*self.__matrix[1][:2])
    def SetColor_Fill(self,color):#设置颜色(三元元组或者四元元组)，如果传入空值则说明不需要填充
        self.__color_fill=color
    def SetColor_Border(self,color):#设置边界颜色(三元元组或者四元元组)，如果传入空值则说明不需要描边
        self.__color_border=color
    def SetThick(self,thick):#设置厚度(厚度小于1视为填充
        self.__thick=thick


    def Tooltip_Show(self):#【重写】设置鼠标悬浮显示tooltip。
        print("显示Tooltip")
    def Tooltip_Hide(self):#【重写】设置鼠标悬浮隐藏tooltip。
        print("隐藏Tooltip")
    def Rect(self):#【重写】返回对象的大概位置，类型为QRect
        mat=self.__matrix
        LT=mat[0][:2]
        RB=mat[1][:2]
        return QRect(*LT.tolist(),*(RB-LT).tolist())
    def SetCanvas(self,canvas):#【重写】设置画布
        super().SetCanvas(canvas)
    def Draw(self):#【重写】绘制矩形，这个供XJDrawer_Canvas调用
        canvas=self.GetCanvas()
        painter=QPainter(canvas)
        matrix=self.__matrix.dot(canvas.GetMatrix())
        matrix=matrix/matrix[-1][-1]
        matrix=matrix[:,:-1]
        L,T,R,B=*matrix[0],*matrix[1]
        area=(L,T,R-L,B-T)
        if(self.__color_fill):#填充颜色存在时
            painter.fillRect(*area,QColor(*self.__color_fill))
        if(self.__color_border):#边界颜色存在时
            painter.setPen(QPen(QColor(*self.__color_border),self.__thick))
            painter.drawRect(*area)
    def Interact(self,mouseStatus):#【重写】响应鼠标事件。传入的是XJ_MouseStatus对象
        if(mouseStatus):#被点击
            status=mouseStatus.GetStatus()
            mapping_button={
                status.ButtonType.Left:"左键",
                status.ButtonType.Middle:"中键",
                status.ButtonType.Right:"右键",
            }
            mapping_click={
                status.ClickType.Single:"单击",
                status.ClickType.Double:"双击",
            }
            print("鼠标位置：",status.pos)
            print("鼠标按键：",mapping_button[status.button])
            print("鼠标点击：",mapping_click[status.click])        
            print()
        else:#脱离选中
            print("【脱离选中状态】")
            print()
        
        







