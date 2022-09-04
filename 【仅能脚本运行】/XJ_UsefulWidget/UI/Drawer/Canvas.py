
__version__='1.0.0'
__author__='Ls_Jan'


import numpy as np
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter,QColor,QPen,QBitmap,QPixmap#QBitmap和QPixmap专门搞掩模
from PyQt5.QtCore import Qt

from XJImporter import XJImporter
Import=XJImporter(globals()).Import
Import('../XJ_MouseStatus','*')
Import('../../XJ_Clocker','*')
Import('../../../XJFunc')


__all__=['Canvas']

class Canvas(QWidget):#画布
    class __PosRange:#用于快速筛选可能点击到的对象。当绘制对象的位置发生变化时，必须将其移除然后再重新添加以更新数据
        class __Mapping:
            __list=[]#便于快速查找。元素升序
            __map={}#位置→对象集合
            def __init__(self):
                self.__list=self.__list.copy()
                self.__map=self.__map.copy()
            def AddObject(self,pos,obj):#记录绘制对象
                if(pos in self.__map):
                    if(obj not in self.__map[pos]):
                        self.__map[pos].add(obj)
                else:
                    if(len(self.__list)):
                        self.__list.insert(XJFunc.BinarySearch(self.__list,pos),pos)
                    else:
                        self.__list.append(pos)
                    self.__map[pos]={obj}
            def DelObject(self,pos,obj):#移除相应记录
                set_obj=self.__map[pos]
                if(obj in set_obj):
                    set_obj.remove(obj)
                    if(len(set_obj)==0):
                        self.__map.pop(pos)
                        self.__list.pop(XJFunc.BinarySearch(self.__list,pos))
            def SearchObject(self,pos,less):#搜寻符合条件的对象集合。LeftSide为真代表返回小于等于pos的对象集合，反之则返回大于等于pos的
                lst=self.__list
                index=XJFunc.BinarySearch(lst,pos)
                rst=set()
                for i in range(*((0,index) if less else (max(0,index),len(lst)))):
                    rst.update(self.__map[lst[i]])
                if(less and 0<=index<len(lst) and lst[index]==pos):
                    rst.update(self.__map[lst[index]])
                return rst

        __L=None#__Mapping类型，下面三个数据也一样
        __R=None
        __T=None
        __B=None
        def __init__(self):
            self.__L=self.__Mapping()
            self.__R=self.__Mapping()
            self.__T=self.__Mapping()
            self.__B=self.__Mapping()
        def AddObject(self,obj):#加入对象
            rect=obj.Rect()
            self.__L.AddObject(rect.left(),obj)
            self.__R.AddObject(rect.right(),obj)
            self.__T.AddObject(rect.top(),obj)
            self.__B.AddObject(rect.bottom(),obj)
        def DelObject(self,obj):#移除对象
            rect=obj.Rect()
            self.__L.DelObject(rect.left(),obj)
            self.__R.DelObject(rect.right(),obj)
            self.__T.DelObject(rect.top(),obj)
            self.__B.DelObject(rect.bottom(),obj)
        def SearchObject(self,pos):#根据二维坐标(二元元组)搜寻对象，返回的是对象集合
            posX,posY=pos
            L=self.__L.SearchObject(posX,True)
            R=self.__R.SearchObject(posX,False)
            T=self.__T.SearchObject(posY,True)
            B=self.__B.SearchObject(posY,False)
            # print(len(L),len(R),len(T),len(B),'\n')
            return L.intersection(R).intersection(T).intersection(B)

    __matrix=None#转换矩阵(np.array，二维)，逻辑坐标→显示坐标
    __iMatrix=None#逆转换矩阵，显示坐标→逻辑坐标
    __map_weight=None#绘制对象→权重
    __map_objects=None#权重→列表(绘制对象)。不用集合，因为集合无法控制同优先级对象的绘制顺序(后加入的对象优先级高，会盖在上面
    __map_id=None#绘制对象→id。给对象进行唯一编号，防止出现同级对象的绘制优先级和点击响应优先级出现不一致的问题
    __list_masking=None#蒙版列表。专用于突出选中的对象。元素为[color,exclude]
    __list_drawingOrder=None#渲染顺序列表。作为缓存提高重绘时的效率。元素为Object对象或者QColor
    __set_noninteractive=None#不参与交互的对象
    __selected=None#被单击选中的对象
    __id=None#当前编号。用于给新加入的对象赋予唯一编号
    __posRange=None#用于快速筛选可能点击到的绘制对象(__PosRange)
    __dragButton=XJ_MouseStatus.Status.ButtonType.Left#鼠标拖拽键(默认左键)
    __dragable=True#允许拖拽
    __tooltipVisible=False#tooltip是否处于显示中
    __tooltipTime=500#鼠标悬停触发tooltip所需的时长(ms)
    __mouseStatus=None#鼠标状态记录器(XJ_MouseStatus)
    __clocker=None#计时器(XJ_Clocker)，用于实现tooltip功能。我这里没重写eventFilter，因为Qt自带的tooltip不能满足我当前需求
    #重写tooltip有异曲同工但不完全相同的例子：https://www.cnblogs.com/zhiyiYo/p/16303940.html
    #使用eventFilter前要先调用函数self.installEventFilter(self)安装事件过滤器：https://www.jianshu.com/p/3ab51ed54622

    def __init__(self,parent=None):
        super().__init__(parent)
        self.__map_objects=dict()
        self.__map_weight=dict()
        self.__map_id=dict()
        self.__id=0
        self.__list_weight=[]
        self.__list_masking=[]
        self.__list_drawingOrder=[]
        self.__set_noninteractive=set()
        self.__selected=None
        self.__matrix=np.array([[3,0,0],[0,3,0],[0,0,1]])
        self.__posRange=self.__PosRange()
        self.__clocker=XJ_Clocker()
        self.__mouseStatus=XJ_MouseStatus()

        self.__mouseStatus.longClick.connect(self.__longClick)
        self.__clocker.SetCallback(self.__tooltip,self.__tooltipTime)
        self.__UpdateIMatrix()
        self.setMouseTracking(True)#时刻捕捉鼠标移动。得在mouseMoveEvent里对__mouseStatus进行更新
    def AddObject(self,obj,weight,interact=True):#添加绘制对象(必须继承XJDrawer_Object)，weight为权重(不小于0的整数)。权重越小越先被绘制(也就是垫底)。如果interact为假，那么该对象就“融入到背景中”，无法被点击选中
        if(type(weight)==int and weight>=0):
            if(obj.canvas):#如果该对象已经加入过其他画布，那就先将它移除
                obj.canvas.DelObject(obj)
            if(interact):
                self.__posRange.AddObject(obj)
            else:
                self.__set_noninteractive.add(obj)
            self.__map_weight[obj]=weight
            self.__map_id[obj]=self.__id
            self.__map_objects.setdefault(weight,[]).append(obj)
            self.__id=self.__id+1
            self.__UpdateDrawingOrder()#更新渲染顺序
            obj.canvas=self
            self.update()
    def DelObject(self,obj):#移除绘制对象
        weight=self.__map_weight.get(obj)
        if(weight !=None and obj.canvas==self):
            if(self.__selected==obj):
                self.__selected.Interact(None)#传入空值，旨在通知其失去了选中状态
                self.__selected=None
            if(obj not in self.__set_noninteractive):
                self.__posRange.DelObject(obj)
            obj.canvas=None
            self.__map_weight.pop(obj)
            self.__map_id.pop(obj)
            self.__map_objects[weight].remove(obj)
            self.__UpdateDrawingOrder()#更新渲染顺序
            self.update()
    def UpdateObject(self,obj,weight=-1):#更新绘制对象的位置(同步显示和点击响应位置)、权重(显示顺序)。当weight为-1时不对权重进行修改。
        #虽然可以依次调用DelObject、AddObject来实现该功能，但效率不高而且还不体面不是吗
        if(obj in self.__map_id):
            self.__posRange.DelObject(obj)
            self.__posRange.AddObject(obj)
            if(weight>=0):
                oldWeight=self.__map_weight[obj]
                if(weight!=oldWeight):
                    self.__map_objects[oldWeight].remove(obj)
                    self.__map_objects.setdefault(weight,[]).append(obj)
                    self.__map_weight[ob]=weight
                    self.__UpdateDrawingOrder()#更新渲染顺序
            self.update()
    def GetObjectWeight(self,obj):#获取绘制对象的权重。为负值说明绘制对象没添加进画布中
        return self.__map_weight.get(obj,-1)
    def GetMatrix(self):#获取画布的转换矩阵。【供绘制对象调用】
        return self.__matrix
    def SetDragButton(self,btn):#设置拖拽键，btn为XJ_MouseStatus.Status.ButtonType的其中一个枚举值
        self.__dragButton=btn
    def SetDragable(self,flag):#设置是否允许拖拽
        self.__dragable=flag
    def SetView_Center(self,x,y):#设置视图中心逻辑坐标(用于快速移动画面)。center类型为2-tuple
        center_orig=np.array([self.size().width()>>1,self.size().height()>>1,1])#当前位置
        center_targ=np.array([x,y,1]).dot(self.__matrix)#目标位置
        self.__matrix[2]=self.__matrix[2]-(center_targ-center_orig)
        self.__UpdateIMatrix()
        self.update()
    def SetView_Rate(self,rate):#设置视图缩放比例
        if(rate<0.05):#防止过度缩小
            rate=0.05
        pos=(self.size().width()>>1,self.size().height()>>1)
        rate=rate/self.__matrix[0][0]

        self.__matrix=self.__matrix.dot(np.array([[rate,0,0],[0,rate,0],[pos[0]*(1-rate),pos[1]*(1-rate),1]]))
        self.__UpdateIMatrix()
        self.update()
    def SetView_Object(self,obj):#将视图中心定位到obj上，并且自动调整好合适的缩放比
        rect=obj.Rect()
        size=self.size()
        center=rect.center()#中心
        if(rect.width() and rect.height()):#防止获取的rect无效
            rate_w=size.width()/rect.width()#宽比
            rate_h=size.height()/rect.height()#高比

            self.SetView_Center(center.x(),center.y())
            self.SetView_Rate(min(rate_w,rate_h)/2)
    def CreateMasking(self,exclude=set(),color=(10,10,10,64)):#创建一张蒙版遮盖整个画面
        '''
            除了exclude外的其他绘制对象都将被盖在下面(点击也会被屏蔽)。蒙版用于突出exclude中的对象
            蒙版可以创建多张，蒙版撤回时依照进出栈原则撤走
            exclude除了传入集合set外，还可以直接传入None，或者传入绘制对象
        '''
        if(exclude==None):
            exclude=set()
        elif(type(exclude)!=set):
            exclude={exclude}
        self.__list_masking.append([QColor(*color),exclude])
        self.__UpdateDrawingOrder()
        self.update()
    def CancelMasking(self):#撤走最近添加的蒙版。当无蒙版可撤时返回False
        if(not self.__list_masking):#如果为空就返回False
            return False
        self.__list_masking.pop()
        self.__UpdateDrawingOrder()
        self.update()
        return True
    
    def mousePressEvent(self,event):
        self.__mouseStatus.UpdateStatus(event)#更新鼠标状态
        self.__clocker.Flush()#刷新计时器
    def mouseReleaseEvent(self,event):#对象的点击事件在鼠标抬起时触发，而不在鼠标按下时触发，这样做是为了避免和拖拽操作相冲突
        mouseStatus=self.__mouseStatus
        status=mouseStatus.GetStatus()#获取鼠标信息
        obj=self.__Sense()#获取感应到的控件
        if(status.isLongClick):#长按
            pass#不需要完成长按后鼠标松开的事件
        elif(status.isMove==False):#说明鼠标没进行拖拽操作，完成的是一轮的点击(处于松开阶段)
            if(obj):#点到绘制对象
                if(status.click==status.ClickType.Double and obj!=self.__selected):#双击，但点到了别的地方
                    status.click=status.ClickType.Single#改成单击
                    if(self.__selected):
                        self.__selected.Interact(None)#传入空值，旨在通知其失去了选中状态
                obj.Interact(mouseStatus)#对其作出响应
                self.__selected=obj
            elif(self.__selected):#点到空白区域，立马取消选中状态
                self.__selected.Interact(None)#传入空值，旨在通知其失去了选中状态
                self.__selected=None
        mouseStatus.UpdateStatus(event)#更新鼠标状态
    def mouseMoveEvent(self,event):
        self.__mouseStatus.UpdateStatus(event)#更新鼠标状态
        status=self.__mouseStatus.GetStatus()
        obj=self.__Sense()#获取感应到的控件
        self.__clocker.Flush()#刷新计时器
        if(self.__selected !=None):#如果有对象被选中
            if(self.__selected!=self.__Sense()):#鼠标不在被选中的对象上
                if(self.__tooltipVisible):#如果tooltip显示中(为了避免多次调用Tooltip_Hide函数
                    self.__selected.Tooltip_Hide()
                    self.__tooltipVisible=False
                    return
        if(status.isPress):#没选中对象，但鼠标处于按下阶段，也就是鼠标处于拖拽状态。虽然可以设置双击拖拽但实际体验并不好
            if(self.__dragable and status.button==self.__dragButton):#本来是设置中键拖拽的，后来不喜欢，改自定义
                offset=status.offset
                self.__matrix[2]=self.__matrix[2]-[*offset,0]
                self.__UpdateIMatrix()
                self.update()
    def wheelEvent(self,event):
        pos=event.pos()
        rate=(1+event.angleDelta().y()/1000)
        if(self.__matrix[0][0]<0.05 and rate<1):#防止过度缩小
            return
        self.__matrix=self.__matrix.dot(np.array([[rate,0,0],[0,rate,0],[pos.x()*(1-rate),pos.y()*(1-rate),1]]))
        self.__UpdateIMatrix()
        self.update()
    def enterEvent(self,event):
        self.__clocker.Start()#运行计时器
    def focusOutEvent(self,event):
        self.__clocker.Pause()#暂停计时器(防止不必要的资源浪费
    def closeEvent(self,event):
        self.__clocker.Pause()#暂停计时器(避免开着个线程导致程序无法顺利退出
    def hideEvent(self,event):
        self.__clocker.Pause()#暂停计时器(避免开着个线程导致程序无法顺利退出
    def paintEvent(self,event):
        pix=QPixmap(self.size())#蒙版
        bit=QBitmap(self.size())#掩模
        pix.fill(QColor(0,0,0,0))#蒙版先搞成透明的
        bit.fill(Qt.white)#掩模也全透明
        painter_mask=QPainter(bit)#掩模专用画笔
        painter_self=QPainter(self)#绘制对象专用画笔
        for obj in self.__list_drawingOrder:
            if(type(obj)==QColor):#如果是QColor说明是蒙版
                pix.setMask(bit)#如果不用掩模预先处理的话最终绘制结果会丑不拉几的，体现在整个画面变得巨黑无比的，可以试着将该句注释掉后运行看看有多丑
                painter_self.drawPixmap(0,0,pix)#把蒙版画上去
                pix.fill(obj)#蒙版上色
                bit.fill(Qt.black)#将掩模涂黑重置
            else:#说明是绘制对象
                obj.Draw(painter_self,False)
                obj.Draw(painter_mask,True)
        painter_mask.end()
        painter_self.end()

    def __logicalClickPos(self,pos):#根据屏幕点击坐标返回逻辑点击坐标
        pos=np.array([*pos,1])
        mat=pos.dot(self.__iMatrix)
        return tuple(mat[:2])
    def __longClick(self):#长按的回调函数
        if(self.__selected):
            self.__selected.Interact(self.__mouseStatus)
    def __tooltip(self):#鼠标悬停显示tooltip的回调函数
        if(self.__selected !=None):#如果有对象被选中
            if(self.__selected==self.__Sense()):#如果鼠标当前位置在被选中的对象上
                if(self.__tooltipVisible==False):#如果tooltip没显示(为了避免多次调用Tooltip_Show函数
                    self.__selected.Tooltip_Show(self.__mouseStatus)#显示tooltip
                    self.__tooltipVisible=True
            else:#鼠标不在被选中的对象上
                if(self.__tooltipVisible):#如果tooltip显示中(为了避免多次调用Tooltip_Hide函数
                    self.__selected.Tooltip_Hide()
                    self.__tooltipVisible=False
    def __Sense(self):#获取鼠标所指的对象(没有则返回None
        status=self.__mouseStatus.GetStatus()#获取鼠标信息
        pos=self.__logicalClickPos(status.pos)#获取逻辑坐标
        # lst=list(self.__posRange.SearchObject(pos))#一般来说，重合在一起的对象少之又少，列表元素个数会远少于画布中的对象个数，遍历这个效率更高
        objs=self.__posRange.SearchObject(pos)#一般来说，重合在一起的对象少之又少，列表元素个数会远少于画布中的对象个数，遍历这个效率更高
        lst=list(objs.intersection(self.__list_masking[-1][-1] if self.__list_masking else objs))

        lst.sort(key=lambda obj:self.__map_id[obj])#先根据id排序一下
        lst=[(obj,self.__map_weight[obj]) for obj in lst]#加入权重以便排序
        lst.sort(key=lambda item:item[1])#以权重进行从小到大排序
        lst=[None]+[obj for obj in map(lambda item:item[0],lst) if obj.Sense(pos)]#调用obj.Sense来获取实际感应到的对象
        return lst[-1]
    def __UpdateIMatrix(self):#更新逆矩阵
        self.__iMatrix=np.linalg.inv(self.__matrix)
    def __UpdateDrawingOrder(self):#更新绘制顺序列表(缓存)
        def __GetOrder(objs):#返回objs的渲染顺序列表
            map_objs={}#{weight:[(obj,id),...],...}
            for obj in objs:
                if(obj in self.__map_weight):
                    weight=self.__map_weight[obj]
                    map_objs.setdefault(weight,[]).append((obj,self.__map_id[obj]))
            for weight in map_objs:
                map_objs[weight].sort(key=lambda nape:nape[1])
            lst=[nape[0] for weight in sorted(map_objs.keys()) for nape in map_objs[weight]]
            return lst

        masking=self.__list_masking
        cache=[]
        union=set()
        for pst in range(len(masking)-1,-1,-1):#要倒着遍历
            nape=masking[pst]
            objs=nape[1].difference(union)#差集，在当前mask上的对象
            union.update(nape[1])
            lst=__GetOrder(objs)#从低到高排好
            lst.extend(cache)#连一起
            cache=lst#更新cache
            cache.insert(0,nape[0])#把蒙版颜色怼进去
        objs=set(self.__map_weight.keys()).difference(union)#差集，最底层的对象
        lst=__GetOrder(objs)#从低到高排好
        lst.extend(cache)#连一起
        cache=lst#更新cache
        cache.insert(0,QColor(0,0,0,0))#怼进一个空颜色，方便重绘
        cache.append(QColor(0,0,0,0))#追加一个空颜色，方便重绘
        self.__list_drawingOrder=cache
        
if __name__=='__main__':
    import sys
    from PyQt5.QtWidgets import QApplication
    Import('Rect','*')
    app = QApplication(sys.argv)

    cv= Canvas()
    cv.show()
    r1=Rect(20,20,100,100)
    r2=Rect(50,50,120,120)
    r3=Rect(40,40,60,60)
    r1.SetColor_Fill((255,255,255,192))
    r2.SetColor_Fill((255,255,255,192))
    r3.SetColor_Fill((255,255,255,192))
    r2.SetText("TQLLLLLLL")
    cv.AddObject(r1,1)
    cv.AddObject(r2,1)
    cv.AddObject(r3,1)
    cv.CreateMasking(r1,(255,0,0,128))
    cv.CreateMasking(r2,(0,255,0,128))
    cv.CreateMasking(r3,(0,0,255,128))
    # cv.CancelMasking()
    # cv.SetView_Center(50,50)
    # cv.SetView_Rate(7)
    cv.SetView_Object(r3)
    sys.exit(app.exec())











