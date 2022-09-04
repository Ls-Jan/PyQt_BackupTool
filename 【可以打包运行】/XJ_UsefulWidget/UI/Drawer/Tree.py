
__version__='1.0.0'
__author__='Ls_Jan'


from XJImporter import XJImporter
from PyQt5.QtCore import pyqtSignal,QRect

from .Rect import Rect
from .Object import Object
from .TreeNode import TreeNode

__all__=['Tree']

class Tree(Object):#依赖XJ_Tree
    func_create=lambda self,iter:None#节点创建时调用。iter为XJ_Tree的迭代器
    func_delete=lambda self,iter:None#节点删除时调用
    func_switch=lambda self,iter:None#节点切换时调用
    func_rename=lambda self,iter:None#节点重命名时调用
    # func_compare=lambda self,iter:None#节点比较时调用
    __nodeText=lambda self,iter:str(iter.GetIterPath()[-1] if iter.GetIterPst()!=0 else '>>根节点<<')#节点显示的文本内容

    __tree=None#XJ_Tree对象
    __line_thickness=1#节点间的连线的粗细
    __line_color=(0,0,0)#节点间的连线的颜色
    __node_size=(150,30)#绘制节点大小
    __node_distance=20#绘制节点之间的距离
    __node_color={#节点颜色。节点有三种：普通节点、当前节点、被选中的节点
        'normal':(255,255,255),
        'current':(0,255,255),
        'selected':(255,255,255),
    }
    __cache={
        'nodes':{},#字典。节点路径→TreeNode对象
        'lines':[],#列表。存放Rect对象
        'rect':QRect,#QRect。记录树的边界
        'alterTime':None,#float。树修改时间
        'canvas':None,#Canvas。记录最近一次绘制时的canvas。该值由self.UpdateTree和self.Draw更新
        'currNodePath':(),#当前节点所在路径。默认根路径。当绘制时该路径不存在的话会自动设为根路径
    }
    def __init__(self,tree):#tree为XJ_Tree对象，nodeText为节点显示的文本内容
        self.__tree=tree
        self.__node_color=self.__node_color.copy()
        self.UpdateTree()
    def Draw(self,painter,isMask=False):#【重写】绘制对象
        if(self.__tree.GetAlterTime()!=self.__cache['alterTime']):#如果树信息已经落后，那就对缓存进行更新
            self.UpdateTree()
        if(self.canvas and self.canvas != self.__cache['canvas']):#画布不一致
            self.__cache['canvas']=self.canvas
            lines=self.__cache['lines']
            nodes=self.__cache['nodes']
            canvas=self.__cache['canvas']
            weight=canvas.GetObjectWeight(self)
            for line in self.__cache['lines']:
                line.SetColor_Fill(self.__line_color)
                line.SetColor_Border(self.__line_color)
                canvas.AddObject(line,weight,False)
            for node in self.__cache['nodes'].values():
                canvas.AddObject(node,weight,True)
            if(canvas):
                canvas.update()
    def Rect(self):#【重写】返回对象在画布的范围位置(逻辑位置)，类型为QRect
        return self.__cache['rect']
    def Sense(self,point):#【重写】重写它的目的是不能让树被点击选中
        return False
    def Release(self):#【重写】释放对象
        super().Release()
        for line in self.__cache['lines']:
            line.Release()
        for node in self.__cache['nodes'].values():
            node.Release()
    def SetFunc_NodeText(self,nodeText):#设置节点显示的文本内容
        self.__nodeText=nodeText
        self.UpdateTree()
    def SetCurrentNode(self,iter):#设置当前节点。iter为XJ_Tree的迭代器
        path=tuple(iter.GetIterPath())
        oldPath=self.__cache['currNodePath']
        nodes=self.__cache['nodes']
        if(path in nodes):
            nodes[oldPath].SetCurrent(False)
            nodes[path].SetCurrent(True)
            self.__cache['currNodePath']=path
            if(self.canvas):
                self.canvas.update()
    def GetNodeColor(self):#获取节点颜色
        return self.__node_color
    def UpdateTree(self):#更新数据。(一般不需要主动调用
        for line in self.__cache['lines']:
            line.Release()
        for node in self.__cache['nodes'].values():
            node.Release()

        nodes={}
        lines=[]
        rect=QRect()
        oldPath=self.__cache['currNodePath']#记录老路径。当该路径仍然有效时就重新对self.__cache['currNodePath']赋值
        self.__cache={
            'nodes':nodes,#字典。节点路径→TreeNode对象
            'lines':lines,#列表。存放Rect对象
            'rect':rect,#QRect。记录树的边界
            'alterTime':self.__tree.GetAlterTime(),#float。树修改时间
            'canvas':None,#Canvas。记录最近一次绘制时的canvas。该值由self.UpdateTree和self.Draw更新
            'currNodePath':(),#当前节点所在路径。默认根路径。当绘制时该路径不存在的话会自动设为根路径
        }
        #每一主枝的所有节点(不包括侧枝)的横向位置都是相同的
        #侧枝等同于新主枝
        iter=self.__tree.GetIter_Root()#获取迭代器，开始遍历之旅
        stack=[sorted(iter.GetNextKeys(),reverse=True)]#栈，深度遍历
        sideBranch=False#用于分辨是否为侧枝(侧枝向右展开)
        id_pos=[0]#主枝编号→主枝横向位置
        depth_id=[0]#行数→最右侧节点主枝编号
        path_id={():0}#节点路径→主枝编号
        path_pst={():0}#节点路径→节点位置
        path_parentBranchID={}#根节点path→根节点所附属的主枝id（设置这变量便于后面节点之间的连线
        while(len(stack)):
            if(len(stack[-1])==0):#返回上一节点
                stack.pop()
                iter.MoveBack()
                sideBranch=True
            else:
                id=path_id[tuple(iter.GetIterPath())]#当前节点主枝编号
                iter.MoveNext(stack[-1].pop())#向下节点移动
                stack.append(sorted(iter.GetNextKeys(),reverse=True))
                path=tuple(iter.GetIterPath())#新节点路径
                depth=len(path)#新节点深度
                path_pst[path]=iter.GetIterPst()
                if(sideBranch):#新节点为侧枝
                    sideBranch=False
                    path_parentBranchID[path]=id#记录该节点依附的主枝
                    id_pos.append(id_pos[depth_id[depth]]+1)#增加新主枝(新主枝横向右移一格
                    id=len(id_pos)-1#新主枝的编号
                    depth_id[depth]=id#更新编号
                    path_id[path]=id#记录该节点的主枝编号
                else:#主枝
                    if(depth==len(depth_id)):#只有主枝才会出现这种情况
                        depth_id.append(id)
                        path_id[path]=id#记录该节点的主枝编号(与上一节点主枝编号一致)
                    else:
                        path_id[path]=id#记录该节点的主枝编号(与上一节点主枝编号一致)
                        if(id_pos[id]<=id_pos[depth_id[depth]]):#延展的主枝侵占到其他的主枝位置，修改该主枝的横向位置
                            # print("【NB】",path,depth,depth_id[depth],id_pos[depth_id[depth]])
                            id_pos[id]=id_pos[depth_id[depth]]+1
                        depth_id[depth]=id#更新编号


        size=self.__node_size
        size_half=(size[0]>>1,size[1]>>1)
        thickness_half=self.__line_thickness>>1
        if(thickness_half==0):
            thickness_half=1
        dist=tuple(d+self.__node_distance for d in size)#节点中心之间的距离
        color=self.__node_color['normal']
        iterCache={}
        for path in path_id:
            id=path_id[path]
            depth=len(path)
            pos=id_pos[id]
            center=(pos*dist[0],depth*dist[1])
            L=center[0]-size_half[0]
            T=center[1]-size_half[1]
            R=center[0]+size_half[0]
            B=center[1]+size_half[1]
            node=TreeNode(L,T,R,B,self,self.__tree.GetIter_ByPath(path,iterCache))
            node.SetText(self.__nodeText(self.__tree.GetIter_ByPst(path_pst[path])))
            if(rect.left()>L):
                rect.setLeft(L)
            if(rect.right()<R):
                rect.setRight(R)
            if(rect.top()>T):
                rect.setTop(T)
            if(rect.bottom()<B):
                rect.setBottom(B)
            nodes[path]=node

            #折线-竖
            VL=center[0]-thickness_half
            VR=center[0]+thickness_half
            VB=T
            if(path not in path_parentBranchID):#直直的连线，省心
                #折线-竖
                VT=B-dist[1]
                lineV=Rect(VL,VT,VR,VB)
                #添加进lines中
                lines.append(lineV)
            else:#如果该节点是主枝的根节点，那么节点之间的连线还得拐一个弯
                #折线-竖
                VT=center[1]-(dist[1]>>1)
                lineV=Rect(VL,VT,VR,VB)
                #折线-横
                id=path_parentBranchID[path]
                pos=id_pos[id]
                HL=pos*dist[0]+thickness_half
                HR=VR
                HT=VT
                HB=HT-(thickness_half<<1)
                lineH=Rect(HL,HT,HR,HB)
                #添加进lines中
                lines.append(lineV)
                lines.append(lineH)
        if(oldPath in nodes):#老路径仍然生效
            nodes[oldPath].SetCurrent(True)
            self.__cache['currNodePath']=oldPath
    
    
    
    
        
    
    









