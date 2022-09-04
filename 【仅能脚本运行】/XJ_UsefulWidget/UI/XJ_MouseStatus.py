
__version__='1.0.0'
__author__='Ls_Jan'


from PyQt5.QtCore import pyqtSignal,QObject
from enum import Enum
from time import time,sleep
from threading import Thread

__all__=['XJ_MouseStatus']

class XJ_MouseStatus(QObject):#鼠标状态记录器(简易，不适用于复杂情况
    '''
        应用范围：
            ①、设置长按事件(长按时发出槽信号longClick，需提前对该信号进行connect设置槽函数)
            ②、区分单双击
            ③、区分左中右键

        注意事项：
            ①、不处理多按键同时按下的情况
            ②、不处理拖拽情况
            ③、偏向于处理鼠标按下时的事件
            ④、鼠标状态由函数GetStatus获得，返回的数据类型为XJ_MouseStatus.Status
            ⑤、重写的鼠标事件仅需mousePressEvent和mouseReleaseEvent，不推荐重写mouseDoubleEvent
            ⑥、在重写的鼠标事件函数里调用UpdateStatus函数
    '''
    longClick=pyqtSignal()#当鼠标长按一定时间时将发出信号
    class Status:#鼠标状态信息(仅在鼠标按下时数据不为None；不处理多按键按下的情况
        '''
            有以下数据成员：
                button：鼠标按下时的按键类型(Status.ButtonType)
                click：鼠标按下时的点击模式(Status.ClickType)
                time：鼠标按下时的时间戳(float)
                pos：鼠标的位置(tuple)
                isPress：分辨鼠标是否按下(bool)
            其中，Status.ButtonType(左中右键)和Msg.ClickType(单双击)均为枚举类
        '''
        class ButtonType(Enum):#按键类型
            Left=1#左键
            Right=2#右键
            Middle=4#中键
            def __str__(self):
                #获取类名方法：https://blog.csdn.net/zffustb/article/details/121058157
                #字符串格式化方法：https://blog.csdn.net/zjbyough/article/details/96466658
                #f-string使用方法：https://blog.csdn.net/sunxb10/article/details/81036693
                return f'{type(self).__name__}.{self.name}'
        class ClickType(Enum):#点击模式
            Single=1#鼠标单击
            Double=2#鼠标双击
            def __str__(self):
                return f'{type(self).__name__}.{self.name}'
        def __str__(self):#便于debug
            output=''
            for key in list(filter(lambda key:key[0].islower(),dir(self))):#获取仅以小写字母开头的属性并对其遍历
                val=eval(f'self.{key}')
                output=output+f'  {key}：{val}\n'
            return f'{type(self).__name__}{{\n{output}}}'
        button=None#按键类型(ButtonType)
        click=None#点击模式(ClickType)
        time=0#鼠标按下时的时间(s)
        pos=(0,0)#鼠标的位置
        offset=(0,0)#记录鼠标与上一次鼠标位置之间的偏移量
        isPress=False#鼠标是否按下
        isLongClick=False#鼠标是否被长按
        isMove=True#仅当鼠标按下时该值为False，其余情况为True，以区分鼠标是否发生拖拽操作
    __stat=None#鼠标状态信息
    __interval_doubleClick=None#鼠标双击时间间隔(s)
    __interval_longClick=None#鼠标长按的时长(s)
    __last_button=None#最近一次鼠标点击的类型(Status.ButtonType)
    def __init__(self):
        super().__init__()
        self.__interval_doubleClick=0.5
        self.__interval_longClick=0.5
        self.__stat=self.Status()
    def GetStatus(self):#获取鼠标信息(左右键、单双击、按下位置、按下时间)。如果鼠标没被按下则返回None
        return self.__stat
    def SetInterval_DoubleClick(self,interval):#设置双击的时间间隔(ms)
        self.__interval_doubleClick=interval/1000
    def SetInterval_LongClick(self,interval):#设置长按的时长(ms)
        self.__interval_longClick=interval/1000
    def UpdateStatus(self,event):#把鼠标事件event传进去，以更新鼠标状态信息
        oldTime=self.__stat.time#记录旧时间
        newTime=time()#记录新时间
        button=event.button()#触发事件的鼠标
        buttons=event.buttons()#当前鼠标扔处于按下的键
        pos=event.pos()

        pos=(pos.x(),pos.y())
        status=self.__stat
        status.offset=(status.pos[0]-pos[0],status.pos[1]-pos[1])#设置偏移量
        status.pos=pos#设置位置
        status.isPress= buttons!=0
        if(buttons):#说明有按键按下
            status.isPress=True
            status.isMove=True
            if(button & buttons):#说明传入的event是由鼠标点击触发
                status.isMove=False
                status.button=status.ButtonType(button) if button else None#设置左中右键
                status.time=newTime#设置时间
                if(newTime-oldTime<=self.__interval_doubleClick and self.__last_button==status.button):#设置单双击
                    status.click=status.ClickType.Double
                    self.__last_button=None#设置None是为了防止一直处于“双击”状态
                else:
                    status.click=status.ClickType.Single
                    self.__last_button=status.button
                Thread(target=self.__thread_longClick).start()#鼠标长按的函数丢给线程跑，虽然可以用定时器但我懒得搞
        else:#说明是抬起
            self.__stat.isPress=False
    def ClearStatus(self):#清空状态，恢复到创建时的样子。(总会有要用到这函数的时候
        self.__stat=self.Status()
        self.__last_button=None
    def __thread_longClick(self):#给线程跑的函数：如果鼠标长按，将发出信号
        status=self.__stat
        status.isLongClick=False
        oldTime=status.time#记录一下时间，防止线程醒来时鼠标信息发生变动
        oldButton=self.__last_button#同上
        sleep(self.__interval_longClick)#睡一会儿
        if(oldTime==status.time and oldButton==self.__last_button and status.isPress and status.isMove==False):#醒来时发现鼠标状态没变(还包括位置没变)，发送长按信号
            status.isLongClick=True
            self.longClick.emit()














