
__version__='1.0.0'
__author__='Ls_Jan'

from threading import Thread
import XJFunc 


class XJ_FileManager:#文件管理器，目前功能为文件的复制和删除。【没做严格的线程安全，请勿在多线程中对同个对象进行高频调用】
    def __init__(self):
        self.__thread=None#线程
        self.__running=False#用来停止线程运行的
        self.__undisposed=[]#待执行的记录
        self.__success=[]#执行成功的记录
        self.__fail=[]#执行失败的记录
        self.__processing=None#执行中的记录
    def Start(self,paths,newPaths=[]):#开始
        '''
            paths是列表，形如[(A1,A2),(B1,B2),(C,True),(D,False),(E,)...]，每个元组代表一个操作。
            如果是(A1,A2)、(B1,B2)这样有两个元素的，说明是复制操作，代表将A1复制到A2。
            如果是(C,True)这样的第二个元素是True，说明是个“可向下访问的路径”，也就是目录，那就创建一个空文件夹
            如果是(D,False)这样的第二个元素是False，说明是个文件，将创建个空文件
            如果是(E,)这样仅一个元素的，说明是删除操作，代表将E删除。
                [元组长度是1的，代表删除操作]
                [元组长度为2的，代表创建/复制操作]
        '''
        if(self.__thread==None):
            self.__undisposed=paths.copy()
            self.__thread=Thread(target=self.__ThreadFunc)
            self.__thread.start()
    def Stop(self):#停止(不会立即停下，请根据IsRunning来判断是否真的停了下来
        self.__running=False
    def IsRunning(self):#判断是否运行中
        return self.__thread!=None
    def GetStatus(self):#获取运行状态，返回 成功、失败、正处理、未处理 的操作
        return {'success':self.__success.copy(),'fail':self.__fail.copy(),'processing':self.__processing,'undisposed':self.__undisposed.copy()}
    def __ThreadFunc(self):#给线程使用的函数
        self.__running=True
        self.__fail.clear()
        self.__success.clear()
        self.__processing=None
        while(self.__running and len(self.__undisposed)>0):
            nape=self.__undisposed.pop(0)
            self.__processing=nape
            rst=self.__success
            if(len(nape)==1):#删除操作
                if(not XJFunc.DeletePath(nape[0])):
                    rst=self.__fail
            else:#创建、复制操作
                if(type(nape[1]) is bool):#创建操作
                    try:
                        if(nape[1]):#创建空目录
                            os.makedirs(nape[0])
                        else:#创建空文件
                            open(nape[0],'w').close()
                    except:
                        rst=self.__fail
                else:#复制操作
                    if(not XJFunc.CopyPath(nape[0],nape[1])):
                        rst=self.__fail
            rst.append(nape)
            self.__processing=None
        self.__thread=None
        

# if __name__=='__main__':
    # path=[
        # (r'C:\Users\Administrator\Desktop\CopyFile\1.jpg',r'C:\Users\Administrator\Desktop\CopyFile\XX\\')
    # ]

    # fm=XJ_FileManager()
    # fm.Start(path)
    # for i in range(100):
        # print(fm.GetStatus())

