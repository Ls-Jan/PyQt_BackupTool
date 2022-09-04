

#尝试使用蒙版

import sys
from PyQt5.QtWidgets import QApplication,QWidget
from PyQt5.QtGui import QPainter,QColor,QPen,QPixmap,QBrush,QBitmap
from PyQt5.QtCore import Qt

class Canvas(QWidget):
    def paintEvent(self,event):
        painter_self=QPainter(self)
        pix=QPixmap(500,500)
        pix.fill(QColor(0,0,0,128))

        bit=QBitmap(500,500)
        bit.fill(Qt.black)
        painter_bit=QPainter(bit)
        # painter_bit.fillRect(50,50,2000,200,QColor(255,253,253,128))
        painter_bit.eraseRect(50,50,2000,200)
        painter_bit.end()
        pix.setMask(bit)
        painter_self.drawPixmap(0,0,pix)
        
        bit=QBitmap(500,500)
        bit.fill(Qt.black)
        painter_bit=QPainter(bit)
        painter_bit.fillRect(50,50,200,2000,Qt.white)
        painter_bit.end()
        pix.setMask(bit)
        painter_self.drawPixmap(0,0,pix)

        # painter_self.end()



if __name__=='__main__':
    app = QApplication(sys.argv)

    cv=Canvas()
    cv.show()
    
    sys.exit(app.exec())











