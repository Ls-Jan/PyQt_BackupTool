
__version__='1.0.0'
__author__='Ls_Jan'


from PyQt5.QtGui import QPainter,QColor,QPen
from PyQt5.QtCore import Qt
from threading import Thread
from time import sleep

from .Rect import Rect

__all__=['TreeNode']

class MenuButton(Rect):#这个类不对外使用，因为功能太少了，仅给TreeNode作为菜单按钮使用
    callback_click=lambda:None#左键点击时的回调函数
    callback_unselect=lambda:None#脱离选中时的回调函数
    size=(50,50)#按钮大小(该属性仅在对象创建时生效)
    
    def __init__(self,x,y):
        L=x-self.size[0]/2
        R=x+self.size[0]/2
        T=y-self.size[1]/2
        B=y+self.size[1]/2
        super().__init__(L,T,R,B)
    def Interact(self,mouseStatus):
        if(mouseStatus):
            status=mouseStatus.GetStatus()
            if(status and status.button==status.ButtonType.Left):#左键点击，立马调用回调函数
                self.callback_click()
        else:#脱离选中状态
            self.callback_unselect()


class TreeNode(Rect):
    __selected=False#判断是否被选中
    __current=False#判断是否为当前节点
    __tree=None#Tree对象
    __iter=None#XJ_Tree的迭代器
    __extend=None#节点展开时所添加的MenuButton对象列表

    __trigger=None#用于判断菜单是否撤走
    color={#颜色。节点有三种：普通节点、当前节点、被选中的节点
        'normal':(240,240,240),
        'current':(255,255,0),
        'selected':(0,255,0),
        'masking':(0,0,0,128),#蒙版颜色
    }
    buttonStyle={#菜单按钮相关样式
        'create':[(0,255,255),'创建'],#依次是：颜色、文本
        'delete':[(0,255,255),'删除'],
        'switch':[(0,255,255),'恢复'],
        'rename':[(0,255,255),'重命名'],
        # 'compare':[(0,255,255),'比较'],
    }
    def __init__(self,L,T,R,B,tree,iter):#传入节点位置、Tree对象、XJ_Tree的迭代器
        super().__init__(L,T,R,B)
        self.__tree=tree
        self.__iter=iter
        self.__extend=[]
        self.SetColor_Fill(self.color['normal'])
    def SetCurrent(self,isCurrent):#设置该节点是否为当前节点，这决定了该节点的菜单有无“创建”选项
        self.__current=isCurrent
        if(not self.__selected):
            self.SetColor_Fill(self.color['current' if isCurrent else 'normal'])
    def Interact(self,mouseStatus):#【重写】响应鼠标事件。传入的是XJ_MouseStatus对象
        if(mouseStatus):#被点击
            self.__trigger=self
            if(not self.__selected):#不处于选中状态的话就改一下
                self.__selected=True
                self.SetColor_Fill(self.color['selected'])
            status=mouseStatus.GetStatus()
            if(status.button==status.ButtonType.Left and len(self.__extend)==0):#如果菜单未展开那就展开菜单
                area=self.Rect()#返回当前节点所在位置(QRect)
                Sx=area.width()/3#菜单按钮的长度
                Sy=area.height()/2#菜单按钮的宽度
                Lx=area.left()#水平位置(左)
                Rx=area.right()#水平位置(右)
                Cx=area.center().x()#水平位置(中)
                Ty=area.top()-Sy/2-Sy/4#竖直位置(上)
                By=area.bottom()+Sy/2+Sy/4#竖直位置(下)
                MenuButton.size=(Sx,Sy)#对菜单按钮设置好大小
                
                self.__CreateMenuButton((Lx,By),'switch')
                self.__CreateMenuButton((Cx,Ty),'rename')
                if(self.__current):#如果是当前节点
                    self.__CreateMenuButton((Cx,By),'create')
                else:
                    self.__CreateMenuButton((Rx,By),'delete')
                self.canvas.CreateMasking({self}.union(set(self.__extend)),self.color['masking'])#创建蒙版
            self.canvas.update()
        else:#点到别的地方
            self.__HideMenu(self)
    def Release(self):#【重写】释放对象
        if(self.__extend):
            for btn in self.__extend:
                btn.Release()
            if(self.canvas):
                self.canvas.CancelMasking()
            self.__extend.clear()
        super().Release()
        
    def __CreateMenuButton(self,center,type):#type取值与buttonStyle的键有关
        btn=MenuButton(*center)
        style=self.buttonStyle[type]
        def callback_click():
            self.__trigger=btn
            if(self.__tree):
                exec(f'tree.func_{type}(iter)',{'tree':self.__tree,'iter':self.__iter})
        def callback_unselect():
            self.__HideMenu(btn)
        btn.SetColor_Fill(style[0])
        btn.SetText(style[1])
        btn.callback_click=callback_click
        btn.callback_unselect=callback_unselect
        self.canvas.AddObject(btn,self.canvas.GetObjectWeight(self))
        self.__extend.append(btn)
        return btn
    def __HideMenu(self,trigger):#根据触发对象来判断是否将菜单隐藏
        def hideMenu():#先睡一会儿再判断是否隐藏按钮
            sleep(0.05)#不多，就睡一小会儿
            if(trigger==self.__trigger):
                self.__selected=False
                self.SetColor_Fill(self.color['current' if self.__current else 'normal'])
                for btn in self.__extend:#撤走菜单按钮
                    btn.Release()
                canvas=self.canvas
                if(canvas):
                    canvas.CancelMasking()#撤走蒙版
                    canvas.update()
                self.__extend.clear()
        Thread(target=hideMenu).start()
    
    
