
#废弃的理由：结构复杂，使用困难

class XJ_Tree:#基于dict和list的树，超懒~~~。这个树的数据能够直接转为json，超赞~~~
    '''
        节点之间通过key连接，key类型为str

        这个树具有一定的线程安全，但并不完全的安全，
        只保护了“删”安全，“增改”并不安全，(代码仅是凭感觉瞎敲一通的
    '''
    class __Iter:#针对这个树所设的迭代器。不允许外界直接创建对象，所以怼了个双下划线将其隐藏
        def __init__(self,tree):
            self.__tree=tree
            self.__stack=[]
            self.__path=[]
            self.__curr=tree.GetData()
            self.__valid=True
            self.__protected=False
            self.__tryInvalid=False
        def copy(self):#返回一个克隆对象
            iter=self.__tree.GetHead()#只能绕，绕，绕，py太奇妙辣（说明py对内部类的支持并不友好，内部类实用性奇差
            if(iter):
                iter.__stack=self.__stack
                iter.__curr=self.__curr
                iter.__valid=self.__valid
                iter.__protected=self.__protected
            return iter

        def GetNexts(self):#获取向下一节点移动的所有key值
            return list(self.__curr[1].keys())
        def GetIterPath(self):#返回迭代器的路径，一般用于debug
            return self.__path.copy()
        def GetCurrData(self):#获取当前节点存储的信息
            return self.__curr[0]
        def SetCurrData(self,data):#设置当前节点存储的信息
            self.__curr[0]=data
        def MoveNext(self,key):#向下移动(移动失败返回False
            next=self.__curr[1].get(key)
            if(next==None):
                return False
            self.__stack.append(self.__curr)
            self.__path.append(key)
            self.__curr=next
            return True
        def MoveBack(self):#向上移动(移动失败返回False
            if(len(self.__stack)==0):
                return False
            self.__curr=self.__stack.pop(-1)
            self.__path.pop(-1)
            return True
        def CreateNextNode(self,key,data,moveNext=True):#创建子节点。当节点已存在时将创建失败
            '''
                正常人应该不会设置个非字符串的玩意儿作为键吧不会吧不会吧
            '''
            if(type(key)!=str or key in self.__curr[1]):
                return False
            self.__curr[1][key]=[data,dict()]
            if(moveNext):
                self.MoveNext(key)
            return True
        def DeleteCurrNode(self,flag):#是否删除当前节点。删除行为不立即生效，即“可反悔”
            if(len(self.__curr)==2 and flag):
                self.__curr.append(None)#将长度设置为3，作为删除的标识
            elif(len(self.__curr)==3):
                self.__curr.pop(-1)#将长度恢复为2
        def AlterTheKey(self,key):#更改父节点指向当前节点的key值。更改成功则返回True
            currKey=self.__path[-1]
            if(currKey==key):
                return True
            backNode=self.__stack[-1]
            if(key in backNode):
                return False
            backNode[1][key]=backNode[1].pop(currKey)
            return True
            
        def SetProtected(self,flag):#设置保护状态(当迭代器被保护时SetInvalid将不生效
            self.__protected=flag
            if(not flag and self.__tryInvalid):#如果关闭保护时尝试无效化__tryInvalid为真，那么迭代器立即无效
                self.__valid=False
                self.__tryInvalid=False
        def IsProtected(self):#返回保护状态(虽然没啥必要获取这个信息
            return self.__protected and self.__valid
        def SetInvalid(self):#将该迭代器无效化。该迭代器处于保护状态时无效化将不会立即生效
            if(self.__valid and self.__protected):
                self.__tryInvalid=True
            else:
                self.__valid=False
        def IsValid(self):#判断迭代器是否有效(无效的迭代器极不建议使用
            return self.__valid


    def __init__(self):
        self.__root=[None,dict()]
        self.__iters=[]
        self.__protected=False
        self.__neatenlock=False#保护NeatenTree函数的多线程安全
    def __ForbidIters(self):#禁用当前的迭代器(同时修改self.__iters)，根据调用该函数后self.__iters是否为空来判断当前树是否被访问中
        iters=[]
        for iter in self.__iters:
            iter.SetInvalid()
            if(iter.IsValid()):
                iters.append(iter)
        self.__iters=iters
    def GetData(self):#返回存储的数据(实际上也就是self.__root)。别对返回的数据进行实质性的修改
        return self.__root
    def LoadData(self,data):#加载数据(与GetData对应
        self.__root=data
        self.__ForbidIters()
        self.__iters=[]
    def ClearData(self):#清空数据/清空树
        self.__root=[None,dict()]
        self.__ForbidIters()
        self.__iters=[]
    def GetRootIter(self):#获取根节点的迭代器(如果树处于保护状态则返回None
        return None if self.__protected else self.__Iter(self)
    def TrySettingProtected(self):#尝试保护树
        self.__protected=True
        self.__ForbidIters()
    def NeatenTree(self):#整理树的内容，将那些被设置删除的节点给删除掉，并且处理好被删除节点的上下节点的关系。如果当前树仍在访问中则不整理并且返回False
        self.__iters=[iter for iter in self.__iters if iter.IsValid()]
        if(len(self.__iters)!=0 or self.__neatenlock):
            return False

        self.__neatenlock=True
        record=[]#元素为三元元组(backNode,key,currNode)，代表一个删除操作
        stack=[self.__root]#遍历整棵树，把所有待删节点找出来。遍历方法为深度遍历
        while(len(stack)>0):
            backNode=stack.pop(-1)
            keys=[]
            for key in backNode[1]:
                currNode=backNode[1][key]
                stack.append(currNode)
                if(len(currNode)==3):#该节点将被删除
                    record.append((backNode,key,currNode))
                    keys.append(key)
            for key in keys:
                backNode[1].pop(key)
        record.reverse()
        for msg in record:#删除节点
            backNode=msg[0]
            backKey=msg[1]
            currNode=msg[2]
            nextNodes=currNode[1]
            if(len(nextNodes)==0):#如果currNode是个尾结点
                nextNodes[None]=[None,None]
            keys=set(backNode[1].keys())
            for nextKey in nextNodes:
                nextNode=nextNodes[nextKey]
                theData=self.Relink_Data(backNode[0],currNode[0],nextNode[0])
                backNode[0]=theData[0]

                if(nextKey!=None):
                    theKey=self.Relink_Key(backKey,nextKey,keys)
                    keys.add(theKey)
                    backNode[1][theKey]=nextNode
                    nextNode[0]=theData[1]

        root=self.__root
        if(len(root)==3):
            if(len(root[1])>0):
                currData=root[0]
                for key in root[1]:
                    nextNode=root[1][key]
                    nextData=nextNode[0]
                    theData=self.Relink_Data(None,currData,nextData)
                    nextNode[0]=nextData
            self.__root[0]=None
            self.__root.pop(-1)
        self.__neatenlock=False
        self.__protected=False
        return True

    def Relink_Key(self,backKey,nextKey,keys):#当节点删除时调用，负责连接父子节点
        '''
            【需要的时候要重写函数体】
            【重写仅需要简单的赋值即可，如：tree.Relink_Key=FFF，FFF为自己重写的函数，函数签名(除self的参数、函数返回值)要与Relink_Key一致】
            获取节点删除后父节点指向子节点的key值，keys是当前父节点已经使用的key集合(避免出现key重复)。
            返回单个数据，作为父节点指向子节点的key值
        '''
        return backKey+('/' if len(backKey)>0 else '') +nextKey
    def Relink_Data(self,backData,currData,nextData):#当节点删除时调用，负责设置父子节点的内容
        '''
            【需要的时候要重写函数体】
            【重写仅需要简单的赋值即可，如：tree.Relink_Data=FFF，FFF为自己重写的函数，函数签名(除self的参数、函数返回值)要与Relink_Data一致】
            【如果删除的是尾结点时，nextData的值为None，如果删除的是头结点那么backData为None】
            获取节点删除后父节点和子节点的内部数据。
            返回二元元组，依次是父节点和子节点的内部数据
        '''
        return (backData,nextData)





import json

if __name__=='__main__':
    tree=XJ_Tree()
    iter=tree.GetRootIter()

    iter.SetCurrData('000')
    iter.SetProtected(True)
    iter.CreateNextNode('1',100,False)
    iter.CreateNextNode('2',200,False)
    iter.CreateNextNode('3',300,False)
    iter.CreateNextNode('AAA',"aaa")
    iter.CreateNextNode('1',100,False)
    iter.CreateNextNode('2',200,False)
    iter.CreateNextNode('3',300,False)
    iter.CreateNextNode('BBB',"bbb")
    iter.AlterTheKey('XXX')
    iter.CreateNextNode('1',100,False)
    iter.CreateNextNode('2',200,False)
    iter.CreateNextNode('3',300)

    iter.DeleteCurrNode(True)
    iter.MoveBack()
    iter.DeleteCurrNode(True)
    iter.MoveBack()
    iter.DeleteCurrNode(True)
    iter.MoveBack()

    iter.SetProtected(False)
    iter.SetInvalid()

    tree.NeatenTree()
    print(json.dumps(tree.GetData(), sort_keys=True,ensure_ascii=False, indent=2))





















