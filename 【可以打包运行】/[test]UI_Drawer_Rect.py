
__version__='1.0.0'
__author__='Ls_Jan'


import sys
from PyQt5.QtWidgets import QApplication

from XJ_UsefulWidget.UI import Drawer

if __name__=='__main__':
    app = QApplication(sys.argv)
    
    cv= Drawer.Canvas()
    cv.show()
    rects=[]
    for val in range(10):
        val=val*10
        rect=Drawer.Rect(20+val,20+val,100+val,100+val)
        rect.SetColor_Fill((255,255,255,192))
        rects.append(rect)
    for rect in rects:
        cv.AddObject(rect,1)
    cv.SetView_Object(rects[5])
    
    sys.exit(app.exec())






