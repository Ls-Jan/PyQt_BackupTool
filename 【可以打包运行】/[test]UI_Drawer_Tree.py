
__version__='1.0.0'
__author__='Ls_Jan'


import sys
from PyQt5.QtWidgets import QApplication

from XJ_UsefulWidget import XJ_Tree
from XJ_UsefulWidget.UI import Drawer 

if __name__=='__main__':
    app = QApplication(sys.argv)

    cv= Drawer.Canvas()
    data_tree=XJ_Tree()
    cv_tree=Drawer.Tree(data_tree)
    cv.show()
    cv.resize(1500,800)
    cv.AddObject(cv_tree,1)

    iter=data_tree.GetIter_Root()
    iter.SetIterData('!!!')
    iter.CreateNext('A','1')
    iter.CreateNext('B','2')
    iter=iter.CreateNext('C','3')
    iter.CreateNext('CA','1')
    iter.CreateNext('CB','2')
    iter.CreateNext('CC','3')
    iter.CreateNext('CD','4')
    iter.MoveBack()
    iter.CreateNext('D','4')
    iter=iter.CreateNext('E','5')
    iter.CreateNext('EA','1')
    iter.CreateNext('EB','2')
    iter.CreateNext('EC','3')
    iter.MoveNext('2')
    iter.CreateNext('EBA','1')
    iter.CreateNext('EBB','2')
    iter.CreateNext('EBC','3')
    iter.MoveBack()
    iter.MoveBack()
    iter.MoveNext('3')
    iter.MoveNext('4')
    iter.CreateNext('CDA','1')
    iter.CreateNext('CDB','2')
    iter.CreateNext('CDC','3')
    cv_tree.UpdateTree()
    cv_tree.SetCurrentNode(iter)
    cv.SetView_Object(cv_tree)
    
    
    sys.exit(app.exec())














