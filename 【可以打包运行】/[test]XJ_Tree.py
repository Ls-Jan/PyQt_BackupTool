
__version__='1.0.0'
__author__='Ls_Jan'

import time
from XJ_UsefulWidget import XJ_Tree

if __name__=='__main__':
    tree=XJ_Tree()
    iter=tree.GetIter_Root()
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
    iter.CreateNext('E','5')
    iter.MoveNext('3')
    iter.MoveNext('4')
    iter.CreateNext('CDA','1')
    iter.CreateNext('CDB','2')
    iter.CreateNext('CDC','3')

    for item in tree.GetTreeData():
        print(item)
    print()
    print("节点位置：",iter.GetIterPst())
    print("节点路径：",'/'.join(iter.GetIterPath()))
    print("节点信息：",tree.GetTreeData()[iter.GetIterPst()])
    print("【移除当前节点】")
    print()
    print()
    print()
    iter.RemoveCurr(True)
    for item in tree.GetTreeData():
        print(item)
    print()
    print("节点信息：",tree.GetTreeData()[iter.GetIterPst()])
    print("【向键'4/3'移动】")
    iter.MoveNext('4/3')
    print("节点信息：",tree.GetTreeData()[iter.GetIterPst()])
    
    print()
    path=['3','3']
    iter=tree.GetIter_ByPath(path,{})
    print("【获取路径",path,"的节点】")
    print("节点为：",iter)


    time.sleep(0.5)






