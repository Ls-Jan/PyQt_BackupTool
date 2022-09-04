
__version__='1.0.0'
__author__='Ls_Jan'


import os
from XJImporter import XJImporter
Import=XJImporter(globals()).Import
Import('../XJ_FileManager','*')
Import('../XJFunc')
Import('./Path','*')
Import('./StructTree','*')
Import('./ArchiveTree','*')
Import('./StructTree','*')
__all__=['BaseSystem']


class BaseSystem:#丐版备份系统
    __archiveTree=None#存档树
    __structTree=None#文件树(聚焦节点)
    fileManager=XJ_FileManager()#文件管理器，用于完成文件的复制、删除操作

    def __init__(self,path):#path为库目录路径。库目录下有三类json文件，分别存放存档树、文件树、路径列表。【如果路径文件_paths.json缺失的话会抛出异常；如果备份源路径不存在则抛出异常】
        Path.Init(path)

        archiveTree=ArchiveTree()#这是存档树
        structTree=StructTree()#这是文件树
        if(not archiveTree.LoadArchive() or not structTree.LoadStruct(archiveTree.iter_curr.GetIterData()['backupTime'])):#如果读取失败说明路径无效
            if(not os.path.exists(Path.source)):#如果连源文件路径都不存在的话那就直接报错吧，不能乱创建文件夹
                raise Exception(f'【路径{Path.source}不存在！】')
            structTree.GetSourceStruct()
            structTree.SaveStruct()

            archiveTree.iter_curr=archiveTree.tree.GetIter_Root()
            archiveTree.iter_curr.SetIterData({'backupTime':structTree.backupTime,'selectedPath':[]})
            archiveTree.iter_focus=archiveTree.iter_curr.copy()
            archiveTree.SaveArchive()
        self.__archiveTree=archiveTree
        self.__structTree=structTree

    def GetArchiveTree(self):#获取存档树的内容XJ_Tree。【这里返回的数据只是给人看的】
        return self.__archiveTree.tree
    def GetNodeIter_Focus(self):#获取存档树聚焦节点的迭代器iter_focus。【这里返回的数据只是给人看的】
        return self.__archiveTree.iter_focus
    def GetNodeIter_Curr(self):#获取存档树当前节点的迭代器iter_curr【这里返回的数据只是给人看的】
        return self.__archiveTree.iter_curr
    def GetStructInfo_Focus(self):#获取聚焦节点的文件结构树树内容XJ_Tree和被选中的路径set。【这里返回的数据只是给人看的】
        return self.__structTree.tree,set(self.__archiveTree.iter_focus.GetIterData()['selectedPath'])
    def GetStructInfo_Path(self,create=False,recover=False):#获取源路径下的一堆信息(详看注释)。【如果源路径不存在则抛出异常】
        '''
            返回的信息(与聚焦节点关联)有：
                文件结构树树内容XJTree
                被选中的路径set()、
                相较之下发生变动的路径{'create':set(),'delete':set(),'alter':set()}
                    [集合中记录的均是文件结构树的节点位置]
                    [combineFocusStruct为假时，'delete'对应的集合信息将为空，因为没法记录]

            注：
                ①、源路径不存在则会报错
                ②、如果create为真，那么返回的文件结构会以 当前路径文件结构树 合并 聚焦节点文件结构树
                ③、如果recover为真，那么返回的文件结构会以 聚焦节点文件结构树 合并 当前路径文件结构树
                ④、如果create和recover同时为假，那么仅仅返回 当前文件结构树树内容XJTree 和 被选中的路径set
                ⑤、不支持create和recover同时为真的情况，如果同时为真那么将直接报错(因为恶意传参)
        '''
        if(not os.path.exists(Path.source)):#源路径不存在将会抛出异常，注意接收
            raise Exception(f'【路径{Path.source}不存在！】')
        if(create and recover):
            raise Exception(f'【参数错误！】')
        struct_path=StructTree()
        struct_path.GetSourceStruct()
        struct_focus=self.__structTree
        struct_focus.tree=struct_focus.tree.copy()
        select_focus=set(self.__archiveTree.iter_focus.GetIterData()['selectedPath'])#聚焦节点记录的 被选中的路径
        select_path={i for i in range(len(struct_path.tree.GetTreeData()))}#全选 被选中的路径
        if(create):
            return self.__CombineStructTree(struct_path,struct_focus,select_path,True)
        elif(recover):
            return self.__CombineStructTree(struct_focus,struct_path,select_focus,False)
        else:
            return struct_path,select_path

    def SwitchNode_Focus(self,pst):#切换聚焦节点
        iter_focus=self.__archiveTree.tree.GetIter_ByPst(pst)
        if(iter_focus):#防止pst无效
            self.__archiveTree.iter_focus=iter_focus
            self.__structTree=StructTree()
            self.__structTree.LoadStruct(iter_focus.GetIterData()['backupTime'])
    def SwitchNode_Curr(self,tree,selectedPath,strictMode=False):#切换当前存档节点。【【【该行为意味着存档的恢复】】】
        '''
            传入的tree和selectedPath由GetStructInfo_Path获得
            tree为XJ_Tree
            selectedPath是列表/集合，元素对应于聚焦节点的文件树的节点位置
            strictMode为真时，将对那些没被选中但存在于源路径中的文件予以删除

            文件的复制删除行为丢给fileManager执行(子线程)，可以获取其运行状态来判断当前的回档情况
        '''
        if(self.fileManager.IsRunning()):#如果正在运行中就不进行存档的恢复
            return False

        operationList=[]
        for iter in tree:#遍历。
            if(iter.GetIterPst()==0):#根节点请无视
                continue
            iterData=iter.GetIterData()
            path_relative=os.path.join('.',*iter.GetIterPath()[1:])#相对路径
            path_source=os.path.join(Path.source,path_relative)#源路径
            if(len(iterData)==1):#说明是目录
                if(os.path.isfile(path_source)):#如果同名文件挡道就将其删除
                    operationList.append((path_source,))
                elif(os.path.isdir(path_source)):#如果是目录就设置访问时间和修改时间(暂未能找到“创建时间”的修改方法
                    os.utime(path_source,(iterData[0],iterData[0]))#设置修改和访问时间：https://www.runoob.com/python/os-utime.html
                operationList.append((path_source,True))#创建文件夹
            elif(len(iterData)==3):#说明是文件并且有备份
                if(iter.GetIterPst() in selectedPath):
                    operationList.append((path_source,))#删路径防阻碍
                    path_backup=os.path.join(Path.backup,iterData[2],path_relative)#备份路径
                    operationList.append((path_backup,path_source))#添加进列表中，之后再恢复备份
            else:#说明没有备份
                pass
        if(strictMode):#如果是严格模式，就对当前路径进行遍历，删除不被选中的路径
            iter_path=self.GetStructInfo_Path()[0].GetIter_Root()
            iter_comp=tree.GetIter_Root()
            stack=[iter_path.GetNextKeys()]
            while(len(stack)):
                if(len(stack[-1])):
                    key=stack[-1].pop()
                    iter_path.MoveNext(key)
                    path_relative=os.path.join('.',*iter_path.GetIterPath()[1:])#相对路径
                    if(iter_comp.MoveNext(key)):#成功向下移动
                        if(iter_comp.GetIterPst() in selectedPath or len(iter_comp.GetIterData())==1):#并且该路径被选中，或者该路径仅仅是个目录
                            stack.append(iter_path.GetNextKeys())
                            continue
                    operationList.append((os.path.join(Path.source,path_relative),))#删除路径
                    iter_path.MoveBack()#既然路径无效，那就没必要对其向下遍历
                else:
                    stack.pop()
                    iter_path.MoveBack()
                    iter_comp.MoveBack()
        archiveTree=self.__archiveTree
        archiveTree.iter_curr=archiveTree.iter_focus.copy()
        archiveTree.SaveArchive()#保存存档树信息
        self.fileManager.Start(operationList)
    def CreateNode(self,tree,selectedPath):#创建下一节点，位于当前节点下。【【【该行为意味着创建存档】】】
        '''
            传入的tree和selectedPath由GetStructInfo_Path获得
            tree为XJ_Tree
            selectedPath为列表/集合，其中的元素对应于tree的位置

            文件的复制行为丢给fileManager执行(子线程)，可以获取其运行状态来判断当前的备份情况
        '''
        if(self.fileManager.IsRunning()):#如果正在复制文件的话就不进行存档的创建
            return False

        struct_next=StructTree()#获取源路径下的当前文件树，是待创建的下一节点所对应的文件树
        struct_next.GetSourceStruct()
        backupTime=struct_next.backupTime

        selected=[]#记录被选中的节点
        operationList=[]#丢给XJ_FileManager执行
        cache_next={}#缓存，用于XJ_Tree.GetIter_ByPath函数
        for pst in selectedPath:
            iter_path=tree.GetIter_ByPst(pst)
            if(iter_path):#防止pst无效导致iter_path无效
                path=iter_path.GetIterPath()
                iter_next=struct_next.tree.GetIter_ByPath(path,cache_next)
                if(iter_next):#如果迭代器有效，说明路径有效
                    selected.append(iter_next.GetIterPst())
                    iterData_next=iter_next.GetIterData()
                    iterData_path=iter_path.GetIterData()
                    path_relative=os.path.join('.',*iter_next.GetIterPath()[1:])#相对路径
                    path_source=os.path.join(Path.source,path_relative)#源路径
                    path_backup=os.path.join(Path.backup,backupTime,path_relative)#备份路径
                    if(len(iterData_path)==3):#说明存在备份，先判断备份是否失效
                        if(not os.path.exists(os.path.join(Path.backup,iterData_path[2],path_relative))):#备份失效，将其删除
                            iterData_path.pop()
                    if(len(iterData_path)==1):#说明是目录
                        operationList.append((path_backup,True))#创建文件夹(虽然没啥用，聊胜于无
                    elif(len(iterData_path)==2):#说明是文件并且没被备份
                        iterData_next.append(backupTime)#更新文件节点信息(加入新备份时间
                        operationList.append((path_source,path_backup))#添加进列表中，之后再备份
                    else:#说明是文件并且有备份
                        iterData_next.append(iterData_path[2])#更新文件节点信息(加入旧备份时间
        archiveTree=self.__archiveTree
        archiveTree.iter_curr=archiveTree.iter_curr.CreateNext({'backupTime':backupTime,'selectedPath':selected},backupTime)#存档树创建新节点
        archiveTree.iter_focus=archiveTree.iter_curr.copy()
        archiveTree.SaveArchive()#存起来存起来
        struct_next.SaveStruct()#存起来存起来
        self.__archiveTree.SaveArchive()#保存存档树信息
        self.fileManager.Start(operationList)#开始文件备份
        return True

    def __CombineStructTree(self,struct_A,struct_B,select_A,update):#以A为主，B结合进A当中。select_A为被选中的路径；update为真则当两文件信息一致时将B的文件信息赋值给A(主要是覆盖backupTime这个数据)。【该函数供GetStructInfo_Path调用】
        tree_A=struct_A.tree
        tree_B=struct_B.tree

        select=set()#被选中
        create=set()#B比A多的
        delete=set()#B比A少的
        alter=set()#A与B不同的

        iter_A=tree_A.GetIter_Root()
        iter_B=tree_B.GetIter_Root()
        stack=[iter_A.GetNextKeys().union(iter_B.GetNextKeys())]
        count=0

        while(len(stack)>0):
            if(len(stack[-1])):#如果有子节点(说明是目录)
                key=stack[-1].pop()
                if(iter_A.MoveNext(key)):#如果目录中存在文件/目录key
                    selectFlag=False#决定当前路径是否加入到选中路径中(即files和folders)
                    iterPst_A=iter_A.GetIterPst()
                    iterData_A=iter_A.GetIterData()
                    if(count==0 and iter_B.MoveNext(key)):#如果记录中存在文件/路径key。当count不为0时说明当前路径在记录中不存在
                        iterPst_B=iter_B.GetIterPst()
                        iterData_B=iter_B.GetIterData()
                        selectFlag=iterPst_A in select_A
                        if((len(iterData_A)>1 ^ len(iterData_B)>1)==False):#如果当前路径和记录的路径都同是文件或同是目录
                            pst=2 if len(iterData_A)>1 else 1#舍去backupTime这信息，只保留time和size
                            if(iterData_A[:pst]!=iterData_B[:pst]):#如果当前路径和记录的路径的基础信息不一致，说明发生了变化
                                alter.add(iterPst_A)
                            elif(update):#未发生变化，则直接更新值
                                iter_A.SetIterData(iterData_B)
                        else:#出现同名但类型不一致的情况，说明原文件/目录被删除并且还创建了一个同名的新目录/文件。
                            alter.add(iterPst_A)
                    else:#记录不存在该文件/目录key
                        count=count+1
                        create.add(iterPst_A)
                        selectFlag=iter_A.parent().GetIterPst() in select
                    if(selectFlag):
                        select.add(iterPst_A)
                else:#当前路径不存在该文件/目录key，(但记录是存在这个文件/目录key的)，于是创建新节点，并将新节点位置加入delete中
                    if(count==0):
                        iter_B.MoveNext(key)
                        iter_A=iter_A.CreateNext(iter_B.GetIterData(),key)
                        delete.add(iter_A.GetIterPst())
                    else:
                        continue
                stack.append(iter_A.GetNextKeys().union(iter_B.GetNextKeys()))
            else:#不存在子节点，就向上移动
                stack.pop()
                iter_A.MoveBack()
                if(count>0):
                    count=count-1
                else:#仅count为0时iter_B跟着iter_A向上移动
                    iter_B.MoveBack()
        return struct_A.tree,select,{'create':create,'delete':delete,'alter':alter}


if __name__=='__main__':
    bs=BaseSystem(r'..\Data\1号')

    bs.SwitchNode_Focus(2)
    rst=bs.GetStructInfo_Focus()
    for data in rst[0]:
        print(data.GetIterData())











