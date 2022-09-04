
__version__='1.0.0'
__author__='Ls_Jan'


import sys
from PyQt5.QtWidgets import QApplication

from XJ_UsefulWidget.UI import XJ_SetView


if __name__=='__main__':
    app = QApplication(sys.argv)
    sv=XJ_SetView('列名')
    sv.show()
    sv.SetData([1,2,3,4,5])
    sv.DeleteLastItem()
    sv.createData.connect(lambda key:print(key))
    sys.exit(app.exec())
    exit()




