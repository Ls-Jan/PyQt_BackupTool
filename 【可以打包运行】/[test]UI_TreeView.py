
__version__='1.0.0'
__author__='Ls_Jan'


import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont

from XJ_UsefulWidget.UI import XJ_TreeView



if __name__ == '__main__':
    app = QApplication(sys.argv)

    tv=XJ_TreeView()
    tv.resize(1000,600)
    tv.show()

    iter=tv.GetIter_Root()
    iter.AppendRow(['AAA','333']).AppendRow(['AAAAA','00000'])
    iter.AppendRow(['BBB','222'])
    iter.AppendRow(['BBB','222'])
    iter.AppendRow(['CCC','111'])
    iter.AppendRow(['XXX','xxx'])
    iter.AppendRow(['YYY','yyy'])
    iter.AppendRow(['ZZZ','zzz'])
    iter.AppendRow(['零零零'])

    iter=iter.AppendRow(['复选框','双击编辑'])
    # iter.AppendRow(['0']).AppendRow(['1']).AppendRow(['2']).AppendRow(['3'])
    iter.SetFont(-1,QFont('宋体',20))
    iter.SetColor(-1,(128,128,0),(0,255,255))
    iter.SetCheckable(0,True)#复选框(显示
    iter.SetCheckState(0,2)#复选状态(勾选
    # iter.SetCheckable(0,False)#复选框(隐藏
    iter.SetEditable(1,True)#双击可修改
    # print(tv.GetIter_ByPath([4]).GetData())
    iter.SetFunc_HasChildren(lambda iter:True)#添加展开符号，不愧是我
    # print(tv.GetIter_Root().GetNextCount())
    
    tv.dataAltered.connect(lambda data:print(data[0].GetPath()+[data[1:]]))
    # tv.rightClicked.connect(lambda :[print(iter.GetData()) for iter in tv.GetCurrIters()])
    tv.rightClicked.connect(lambda :[print(tv.GetCurrIter().GetNextCount())])
    # tv.rightClicked.connect(lambda :[print(iter.GetPath()) for iter in tv.GetCurrIters()])
    tv.doubleClicked.connect(lambda :print(tv.GetCurrIter().GetData()))
    tv.SetRowDragable(False)
    sys.exit(app.exec())





