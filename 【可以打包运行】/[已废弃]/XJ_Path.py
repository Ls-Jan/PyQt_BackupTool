
import os
import time
import win32file

__all__=['XJ_Path']

#主要用于获取文件信息以及用来占用文件的
class XJ_Path:
    def __init__(self,path='.'):
        self.__path=path
        self.__handle=None
    def __del__(self):
        self.Release()


    def Occupied(self):#占用文件(占用成功或者正在占用的话将返回True
        if(self.__handle==None):
            try:
                self.__handle = win32file.CreateFile(file, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)
            except:
                return False
        return True
    def Release(self):#释放文件
        win32file.CloseHandle(self.__handle)
        self.__handle=None
    def GetTime(self):#获取文件修改时间
        if(self.IsValid()):
            return os.path.getmtime(file)
        return None
    def SetPath(self,path):#更改路径
        if(self.__handle):
            self.Release()
        self.__path=path
    def IsValid(self):#判断路径是否有效/存在
        return os.path.exists(self.__path)
    def IsFile(self):
        return os.path.isfile(self.__path)
    def IsDir(self):
        return os.path.isdir(self.__path)
    def GetPath(self):
        return self.__path

















