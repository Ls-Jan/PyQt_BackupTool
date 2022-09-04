
__version__='1.0.0'
__author__='Ls_Jan'


from time import time,sleep
from threading import Thread

__all__=['XJ_Clocker']

class XJ_Clocker():
    '''
        它是计时器(精度默认1ms)，和定时器有很大不同，它的计时可以重置为0，而且可以设置超时任务(感觉还顺便完成了定时器的功能...)
        因为不知道高频率创建线程是否对性能造成影响，于是让计时器精度可自定义(该参数决定创建线程的频率)
        
        不要高频切换计时器状态(即高频调用函数Start、Pause、Flush)，就跟你家的电器一样，高频开关会坏的(做出预料之外的事)
    '''

    __isRunning=False#计时器是否运行(bool)
    __totalTime=0#累计时长(float)
    __time=0#时间戳(float)
    __timeout_func=None#超时任务(无参函数)
    __timeout_period=0#超时时间(s)
    __timeout_flag=False#是否调用过超时任务(bool)
    __interval=0.001#计时器精度(s)
    def __init__(self,precision=1):#设置计时器的时间精度(单位ms)，默认1ms
        self.__interval=precision/1000
    def SetCallback(self,func,peroid):#设置超时任务和超时时间(ms)
        '''
            设置超时任务(无参函数)和超时时间(正数，单位ms)
            如果传入的参数无效(例如func为None、period为非正数的其他玩意儿)则清除计时器当前的超时任务(即计时器超时时无动作)
        '''
        self.__timeout_func=func
        self.__timeout_period=peroid/1000
    def GetStatus(self):#获取计时器运行状态：是否运行(bool)、累计时长(ms)
        return self.__isRunning,int(self.__totalTime*1000)

    def Start(self):#开始计时
        if(not self.__isRunning):
            self.__time=time()#刷新时间戳
            self.__isRunning=True
            self.__timeout_flag=False
            Thread(target=self.__threadFunc).start()#开始计时
    def Pause(self):#暂停计时
        if(self.__isRunning):
            self.__time=time()#刷新时间戳
            self.__isRunning=False
    def Flush(self):#清空累计时长
        if(self.__isRunning):
            self.__time=time()#刷新时间戳
            self.__totalTime=0
            self.__timeout_flag=False
            Thread(target=self.__threadFunc).start()#开始计时
        else:
            self.__totalTime=0

    def __threadFunc(self):#丢给线程运行的函数
        startTime=self.__time#线程开始时的时间戳
        sleep(self.__interval)#睡一小会儿，(很快啊，年轻人你不讲武德
        endTime=self.__time#线程结束时的时间戳
        if(endTime!=startTime):#被横插一脚，白睡1ms
            if(not self.__isRunning):#如果是因为调用了Pause才白睡的话，那也不全白睡
                self.__totalTime=self.__totalTime+(endTime-startTime)
            else:#说明是被Flush踹的一脚，那就真白睡了
                pass
        else:
            if(not self.__isRunning):#如果计时器没在运行，也是废的。
                #因为我没设置严格的线程锁，导致self.__time线程不安全，所以就需要这一条判断语句防爆破
                #虽然这条判断语句是凭感觉加的，完全是补丁行为
                pass
            else:#计时有效
                endTime=time()
                self.__time=endTime#更新时间戳
                self.__totalTime=self.__totalTime+(endTime-startTime)
                if(not self.__timeout_flag and self.__timeout_period and self.__timeout_func):#开始判断是否执行超时任务
                    if(self.__timeout_period<self.__totalTime):#超时了超时了
                        self.__timeout_flag=True
                        self.__timeout_func()#运行超时任务
                Thread(target=self.__threadFunc).start()#接力



if __name__=='__main__':
    clocker=XJ_Clocker()
    clocker.SetCallback(lambda:print("【超时任务！！！】",clocker.GetStatus()[1]),400)
    clocker.Start()
    for i in range(50):
        sleep(0.01)
        print(clocker.GetStatus())
    clocker.Pause()
    print(clocker.GetStatus())


