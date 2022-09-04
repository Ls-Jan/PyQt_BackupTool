
__version__='1.0.0'
__author__='Ls_Jan'


import time
import os
import shutil


def BinarySearch(lst,pos):#二分查找，返回对应下标
    '''
        lst要经过升序排列

        如果lst中无pos这个元素则返回右值
        例子：
            lst=[1,3,5,7,9]
            pos=4
            返回值为2
        也就是，你可以使用BinarySearch来获取列表插入点插入元素，并且不破坏lst的升序情况

        特别的，pos小于最小值会返回0；列表为空返回0；pos大于最大值会返回len(lst)
    '''
    lenLst=len(lst)
    L=0
    R=lenLst-1
    M=(L+R)>>1
    if(lenLst==0):
        return 0
    if(pos<lst[L]):
        return 0
    elif(pos>lst[R]):
        return R+1

    #二分查找
    while(L+1<R):
        M=(L+R)>>1
        if(lst[M]>pos):
            R=M
        else:
            L=M
    return L if lst[L]==pos else R

def GetFormatTime(Time=None):#获取格式化字符串，作为目录名。如果传入空值则默认值为time.time()
    '''
        获取当前时间的字串表示，这将作为文件夹的名字。
        格式为：[年-月-日],[时.分.秒]
    '''
    if(Time==None):
        time.time()
    return time.strftime('[%Y-%m-%d],[%H.%M.%S]',time.localtime(Time))

def DeletePath(path):#删除路径(无论是文件还是目录)，路径不存在则返回True
    try:
        if(os.path.isdir(path)):
            shutil.rmtree(path)
            '''
                #不使用shutil.rmtree的递归删除目录方法
                for root, dirs, files in os.walk(path, topdown=False):
                    for name in files:
                        os.remove(os.path.join(root, name))
                    for name in dirs:
                        os.rmdir(os.path.join(root, name))
                os.rmdir(path)
            '''
        elif(os.path.isfile(path)):
            os.remove(path)
    except:
        return False
    return True

def CopyPath(source,destination):#复制路径，复制成功返回True
    '''
        路径包括文件和目录。如果路径是目录则将目录下的所有对象全复制到destination下
        额外：如果destination以斜杠结尾，那么复制的文件/目录名将和源路径的文件/目录名一致
        额外：如果目标路径已存在或者目标路径所在文件夹无法创建时将复制失败
    '''
    try:
        source=source.strip('/')#用于删去结尾的斜杠
        path=os.path.split(destination)[0]
        if(not os.path.isdir(path)):#目标路径所在目录不存在则将其创建，防止路径不存在而导致复制失败
            os.makedirs(path)
        if(destination[-1]=='/' or destination[-1]=='\\'):
            destination=destination+os.path.split(source)[1]

        if(os.path.isdir(source)):
            shutil.copytree(source,destination)
        elif(os.path.isfile(source)):
            if(not os.path.exists(destination) or os.path.isfile(destination)):
                shutil.copy2(source,destination)
            else:
                return False
        else:#说明source无效不能复制
            return False
    except:
        return False
    return True




def FileIsAltered(path,alterTime):#根据文件的修改时间来判断文件是否被修改。时间不一致则返回True，否则返回False；文件不存在则返回None
    if(os.path.exists(path)):
        return os.path.getmtime(path)!=alterTime
    return None













