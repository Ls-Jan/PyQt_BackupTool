

import sys
from PyQt5.QtWidgets import QApplication,QWidget
from XJ_MouseStatus import XJ_MouseStatus
class XJ_Test(QWidget):
    __mouseStatus=None
    def __init__(self,parent=None):
        super().__init__(parent)
        self.__mouseStatus=XJ_MouseStatus()
        self.__mouseStatus.longClick.connect(self.__func_longClick)
    def mousePressEvent(self,event):
        self.__mouseStatus.UpdateStatus(event)
        print("【鼠标按下！！！】")
        self.__func_printMsg()
    def mouseReleaseEvent(self,event):
        self.__mouseStatus.UpdateStatus(event)
        print("【鼠标抬起！！！】\n")
    def __func_longClick(self):#鼠标长按的回调
        print("【鼠标长按！！！】")
        self.__func_printMsg()
    def __func_printMsg(self):#打印鼠标信息
        status=self.__mouseStatus.GetStatus()
        mapping_button={
            status.ButtonType.Left:"左键",
            status.ButtonType.Middle:"中键",
            status.ButtonType.Right:"右键"
        }
        mapping_click={
            status.ClickType.Single:"单击",
            status.ClickType.Double:"双击",
        }
        print("鼠标位置：",status.pos)
        print("鼠标按键：",mapping_button[status.button])
        print("鼠标点击：",mapping_click[status.click])
        
if __name__=='__main__':
    app = QApplication(sys.argv)
    
    test=XJ_Test()
    test.show()
    
    sys.exit(app.exec())








