
import win32file

__all__=['XJ_FileOccupier']

class XJ_FileOccupier:#文件占用器
    def __init__(self,path='.'):
        self.__path=path
        self.__handle=None
    def __del__(self):
        self.ReleaseFile()

    def OccupyFile(self):#占用文件(占用成功或者正在占用的话将返回True
        if(self.__handle==None):
            try:
                self.__handle = win32file.CreateFile(file, win32file.GENERIC_READ, 0, None, win32file.OPEN_EXISTING, win32file.FILE_ATTRIBUTE_NORMAL, None)
            except:
                return False
        return True
    def ReleaseFile(self):#释放文件
        win32file.CloseHandle(self.__handle)
        self.__handle=None
















