
__version__='1.0.0'
__author__='Ls_Jan'

import json
import os
import time

class XJ_Tree:#基于dict和list的树，超懒~~~。这个树的数据能够直接转为json，超赞~~~。该树无论创建还是清空，总会有一个根节点
    '''
        节点之间通过key连接，key类型为str
        节点结构为[pst,data,{key:pst}]，树节点是双向的，即第一个pst是父节点的pst，第二个pst是子节点的pst

        不搞线程安全了，即这个数据结构不允许多线程。请在外部控制好线程问题
    '''
    class __Iter:#这个树的迭代器（支持next(iter)的遍历操作，但并不是深度遍历和广度遍历，遍历结果依赖树节点的添加顺序）
        '''
            新建的节点不会破坏旧迭代器的使用，
            但如果移除节点的话极有可能使旧迭代器失效(因为树信息发生改动
        '''
        def __init__(self,tree,pst=0):#设置迭代器的位置，设置失败将返回根节点迭代器
            self.__tree=tree
            self.__nodes=tree.GetTreeData()
            self.__curr=0
            self.__path=[]
            self.__rootFlag=True#仅用于遍历，为了遍历时能够打印出根节点信息...(无关紧要的变量...
            self.__SetIterPst(pst)
        def __next__(self):#遍历，返回的是迭代器(不要对迭代器进行任何写的操作
            if(self.__curr==0 and self.__rootFlag):
                self.__rootFlag=False
            else:
                self.__rootFlag=True
                if(self.__SetIterPst(self.__curr+1)==False):
                    raise StopIteration
            return self
        def copy(self):#返回当前迭代器的复制
            iter=self.__tree.GetIter_Root()
            iter.__path=self.__path.copy()
            iter.__curr=self.__curr
            return iter
        def parent(self):#返回当前迭代器的父节点迭代器(如果不存在父节点则返回None
            iter=self.copy()
            return iter if iter.MoveBack() else None
        def __SetIterPst(self,pst):
            if(type(pst)!=int or not 0<=pst<len(self.__nodes)):
                return False
            self.__curr=pst

            path=[]
            currNode=self.__nodes[pst]
            while(pst!=0):
                backNode=self.__nodes[currNode[0]]
                for key in backNode[2]:
                    if(backNode[2][key]==pst):
                        path.append(key)
                        break
                pst=currNode[0]
                currNode=backNode
            path.reverse()
            self.__path=path

            return True            
            
        def CreateNext(self,data,key):#创建子节点，创建成功将返回对应迭代器。键key只能为字符串(失败返回None
            nodes=self.__nodes
            curr=self.__curr
            currNode=nodes[curr]
            if(type(key)!=str or key in currNode[2]):
                return None
            next=len(nodes)
            currNode[2][key]=next
            nodes.append([curr,data,{}])

            iter=self.copy()
            iter.__curr=next
            iter.__path.append(key)
            self.__tree.UpdateAlterTime()#更新修改时间
            return iter
        def ChangeKey(self,oldKey,newKey):#更换指向子节点的key。【如果存在多个迭代器的话很可能会导致其他迭代器的self.__path过期，只不过节点的位置依旧有效】
            currNode=self.__nodes[self.__curr]
            if(oldKey in currNode[2] and newKey not in currNode[2]):
                currNode[2][newKey]=currNode[2].pop(oldKey)
                return True
            self.__tree.UpdateAlterTime()#更新修改时间
            return False
        def MoveNext(self,key):#移动到下一节点
            currNode=self.__nodes[self.__curr]
            if(key in currNode[2]):
                self.__curr=currNode[2][key]
                self.__path.append(key)
                return True
            return False
        def MoveBack(self):#移动到上一节点
            if(len(self.__path)>0):
                self.__path.pop(-1)
                self.__curr=self.__nodes[self.__curr][0]
                return True
            return False
        def RemoveCurr(self,removeChildren=False):#移除当前节点(删除代价很大，一般建议不删)。【如果存在多个迭代器的话很可能会导致其他迭代器的使用异常】
            if(len(self.__path)==0):#不删根节点(主要是嫌麻烦+没必要
                return False
            curr=self.__curr
            nodes=self.__nodes

            currNode=nodes[curr]
            backNode=nodes[currNode[0]]

            self.__curr=currNode[0]
            backKey=self.__path.pop(-1)
            backNode[2].pop(backKey)
            
            
            nodesCount=len(nodes)#节点个数
            record=[]#被删的节点的位置
            if(removeChildren):
                stack=[curr]
                while(len(stack)>0):
                    curr=stack.pop(-1)
                    currNode=nodes[curr]
                    stack.extend(currNode[2].values())
                    record.append(curr)
            else:
                backKey=(backKey if len(backKey)>0 else ' ')+'/'
                nextNodes=currNode[2]
                record.append(curr)
                for nextKey in nextNodes:
                    next=nextNodes[nextKey]
                    nextNode=nodes[next]
                    nextNode[0]=currNode[0]
                    backNode[2][backKey+nextKey]=next
            record.sort()
            map=[]
            weight=0
            prePst=0
            for pst in record:
                map.extend([weight for w in range(prePst,pst)])
                weight=weight+1
                prePst=pst
            map.extend([weight for w in range(prePst,len(nodes))])
            record.reverse()
            for curr in record:#删除节点
                nodes.pop(curr)
            for node in nodes:#调整节点的指向
                nexts=node[2]
                for key in nexts:
                    next=nexts[key]
                    nexts[key]=next-map[next]
            self.__tree.UpdateAlterTime()#更新修改时间
            return True
        def SetIterData(self,data):#设置节点内容
            self.__nodes[self.__curr][1]=data
            self.__tree.UpdateAlterTime()#更新修改时间
        def GetIterData(self):#获取当前节点内容(该数据没进行过拷贝)
            return self.__nodes[self.__curr][1]
        def GetIterPst(self):#返回迭代器的当前位置，一般用来debug
            return self.__curr
        def GetIterPath(self):#返回迭代器的路径(列表)。根节点对应的路径列表为空
            return self.__path
        def GetNextKeys(self):#获取指向下一节点的所有key值(集合)
            return set(self.__nodes[self.__curr][2].keys())
        def GetNextPsts(self):#获取下一节点的所有位置(集合)
            return set(self.__nodes[self.__curr][2].values())
        def GetNextIters(self):#获取下一节点的迭代器(字典)
            currNode=self.__nodes[self.__curr]
            iters={}
            nexts=currNode[2]
            for key in nexts:
                iter=self.copy()
                iter.MoveNext(key)
                iters[key]=iter
            return iters
        def GetTree(self):#获取树
            return self.__tree

    def __init__(self):
        self.__list=[[0,None,{}]]
        self.__alterTime=time.time()
    def __iter__(self):
        return self.GetIter_Root()
    def copy(self):
        tree=XJ_Tree()
        tree.__list=self.__list.copy()
        return tree
    def GetTreeData(self):#返回存储的数据信息，极不建议对其内容进行修改
        return self.__list
    def SetTreeData(self,data):#和GetData对应
        self.__list=data
    def ClearTree(self):#清除树
        self.__list=[[0,None,{}]]
    def GetIter_Root(self):#返回根节点迭代器
        return self.__Iter(self)
    def GetIter_ByPst(self,pst):#根据位置返回迭代器
        iter=self.__Iter(self,pst)
        return iter if iter.GetIterPst()==pst else None
    def GetIter_ByPath(self,path:list,cache:dict):#根据路径返回迭代器，path和迭代器的函数GetIterPath对应。cache是缓存，以提高查询速度，每次调用该函数都会自动更新cache
        path=list(path)
        iter=self.__Iter(self)
        stack=[]
        while(len(path)>0):
            path_tuple=tuple(path)
            if(path_tuple in cache):
                iter=cache[path_tuple].copy()
                break
            else:
                stack.append(path.pop())
        stack.reverse()
        for key in stack:
            if(iter.MoveNext(key)):
                path.append(key)
                cache[tuple(path)]=iter.copy()
            else:
                return None
        return iter
    def SaveJSON(self,path):#保存为JSON文件
        with open(path,'w') as f:
            f.write(json.dumps(self.__list, sort_keys=True, ensure_ascii=False, indent=2))
    def LoadJSON(self,path):#读取JSON文件(读取失败返回False
        if(os.path.isfile(path)):
            with open(path,'r') as f:
                self.__list=json.loads(f.read())
                self.__alterTime=time.time()
                return True
        else:
            return False
    def UpdateAlterTime(self):#更新树的修改时间，以便核对
        self.__alterTime=time.time()
    def GetAlterTime(self):#获取树的修改时间。在调用LoadJSON时修改时间为加载时的时间，而不是保存JSON时的时间
        return self.__alterTime

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



















