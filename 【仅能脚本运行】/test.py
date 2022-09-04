
__version__='1.0.0'
__author__='Ls_Jan'




import os
import sys
import json
from PyQt5.QtWidgets import QApplication,QMainWindow,QPushButton,QWidget,QVBoxLayout,QMenu,QMenuBar,QMessageBox
from PyQt5.QtCore import Qt

from XJ_UsefulWidget.UI import Drawer


if __name__=='__main__':
    app = QApplication(sys.argv)

    cv= Drawer.Canvas()
    cv.show()
    r1=Drawer.Rect(20,20,100,100)
    r2=Drawer.Rect(50,50,120,120)
    r3=Drawer.Rect(40,40,60,60)
    r1.SetColor_Fill((255,255,255,192))
    r2.SetColor_Fill((255,255,255,192))
    r3.SetColor_Fill((255,255,255,192))
    r2.SetText("TQLLLLLLL")
    cv.AddObject(r1,1)
    cv.AddObject(r2,1)
    cv.AddObject(r3,1)
    cv.CreateMasking(r1,(255,0,0,128))
    cv.CreateMasking(r2,(0,255,0,128))
    cv.CreateMasking(r3,(0,0,255,128))
    # cv.CancelMasking()
    # cv.SetView_Center(50,50)
    # cv.SetView_Rate(7)
    cv.SetView_Object(r3)
    sys.exit(app.exec())


















