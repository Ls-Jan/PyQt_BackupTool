
__version__='1.0.0'
__author__='Ls_Jan'

import numpy as np
from PyQt5.QtGui import QPainter,QColor,QPen
from PyQt5.QtCore import Qt,QRect

from XJImporter import XJImporter
Import=XJImporter(globals()).Import
Import('./Object','*')

__all__=['Rect']

class Rect(Object):
    __matrix=None#为np.array对象，是个Nx3矩阵(N=2+1)。用于点的平移缩放变换
    __color_fill=(0,255,255,128)#颜色
    __color_border=(0,0,0)#边界颜色
    __color_text=(0,0,0)#文本颜色
    __thickness_border=1#边界粗细
    __text=''#文本

    def __init__(self,L=0,T=0,R=0,B=0):#传入矩形的左上右下边界，可以是小数，但不建议
        self.__matrix=np.array([[L,T,1],[R,B,1]])
    def GetLTRB(self):#返回矩形的左上右下
        return (*self.__matrix[0][:2],*self.__matrix[1][:2])
    def SetColor_Fill(self,color):#设置颜色(三元元组或者四元元组)，如果传入空值则说明不需要填充
        self.__color_fill=color
    def SetColor_Border(self,color):#设置边界颜色(三元元组或者四元元组)，如果传入空值则说明不需要描边
        self.__color_border=color
    def SetColor_Text(self,color):#设置文本颜色(三元元组或者四元元组)，如果传入空值则说明不需要显示文本
        self.__color_text=color
    def SetBorderThickness(self,thick):#设置边界厚度(值小于1则不描边)
        self.__thickness_border=thick
    def SetText(self,text):#设置文本
        self.__text=text

    def Rect(self):#【重写】返回对象在画布的范围位置(逻辑位置)，类型为QRect
        mat=self.__matrix
        LT=mat[0][:2]
        RB=mat[1][:2]
        return QRect(*LT.tolist(),*(RB-LT).tolist())
    def Draw(self,painter,isMask=False):#【重写】绘制函数，要传入画笔。如果isMask为真则说明该画笔是用来绘制掩模的
        if(not self.canvas):
            return
        area=self.__GetArea()
        if(isMask):
            painter.eraseRect(*area)#掩模的话就直接把矩形所在区域给擦掉
        else:
            if(self.__color_fill):#填充颜色存在时
                painter.fillRect(*area,QColor(*self.__color_fill))
            if(self.__color_border and self.__thickness_border>=1):#边界颜色存在并且边界厚度有效时
                painter.setPen(QPen(QColor(*self.__color_border),self.__thickness_border))
                painter.drawRect(*area)
            if(self.__color_text and self.__text and len(self.__text)):#绘制文本
                painter.setPen(QPen(QColor(*self.__color_text),self.__thickness_border))
                painter.drawText(*area,Qt.AlignCenter,self.__text)
    # def Tooltip_Show(self,mouseStatus):#【重写】设置鼠标悬浮显示tooltip。传入的是XJ_MouseStatus对象。
        # print("显示Tooltip")
    # def Tooltip_Hide(self):#【重写】设置鼠标悬浮隐藏tooltip。
        # print("隐藏Tooltip")
    # def Interact(self,mouseStatus):#【重写】响应鼠标事件。传入的是XJ_MouseStatus对象
        # if(mouseStatus):#被点击
            # status=mouseStatus.GetStatus()
            # mapping_button={
                # status.ButtonType.Left:"左键",
                # status.ButtonType.Middle:"中键",
                # status.ButtonType.Right:"右键",
            # }
            # mapping_click={
                # status.ClickType.Single:"单击",
                # status.ClickType.Double:"双击",
            # }
            # print("鼠标位置：",status.pos)
            # print("鼠标按键：",mapping_button[status.button])
            # print("鼠标点击：",mapping_click[status.click])
            # if(status.isLongClick):
                # print("【鼠标长按！！！】")
            # print()
        # else:#脱离选中
            # pass

    def __GetArea(self):#获取矩形的屏幕坐标
        canvasMatrix=self.canvas.GetMatrix()
        matrix=self.__matrix.dot(canvasMatrix)
        matrix=matrix/canvasMatrix[2][2]
        matrix=matrix[:,:-1]
        L,T,R,B=*matrix[0],*matrix[1]
        area=(L,T,R-L,B-T)
        return area












if __name__=='__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    Import('./Canvas','*')
    app = QApplication(sys.argv)

    cv= Canvas()
    cv.show()
    rects=[]
    for val in range(10):
        val=val*10
        rect=Rect(20+val,20+val,100+val,100+val)
        rect.SetColor_Fill((255,255,255,192))
        rects.append(rect)
    for rect in rects:
        cv.AddObject(rect,1)
    cv.SetView_Object(rects[5])
    sys.exit(app.exec())

