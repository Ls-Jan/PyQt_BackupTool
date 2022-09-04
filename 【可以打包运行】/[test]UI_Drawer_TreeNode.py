
__version__='1.0.0'
__author__='Ls_Jan'


import sys
from PyQt5.QtWidgets import QApplication

from XJ_UsefulWidget.UI import Drawer


if __name__=='__main__':
    app = QApplication(sys.argv)
    
    cv=Drawer.Canvas()
    cv.show()

    tn=Drawer.TreeNode(0,0,150,30,None,None)
    tn.SetCurrent(True)
    cv.AddObject(tn,1)
    cv.SetView_Object(tn)
    
    sys.exit(app.exec())








