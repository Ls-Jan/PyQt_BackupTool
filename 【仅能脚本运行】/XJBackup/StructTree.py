
__version__='1.0.0'
__author__='Ls_Jan'


import json
import os
from XJImporter import XJImporter

Import=XJImporter(globals()).Import
Import('../XJFunc')
Import('../XJ_UsefulWidget','XJ_Tree')
Import('./Path','*')

__all__=['StructTree']


class StructTree:#文件结构树【核心】
    '''
        【文件树】对应着目录结构，节点信息为列表，
        列表元素依次是
            修改时间time(float)
                [吐槽：由于无缘由的不可抗力，我愣是没找到能设置目录创建时间的方法，只能找到访问时间和修改时间的：https://www.runoob.com/python/os-utime.html]
            文件大小size(int)
                [仅节点对应的是文件时有效]
            备份文件所在目录backupTime(str)
                [仅节点对应的是文件时有效]
                [该元素不一定存在...有备份就有该信息，没备份就没这信息]
                [该元素不总代表有效...要查询路径判断备份是否失效]
        补充：
            文件树的父节点指向子节点的key对应着子节点的文件/目录名。
    '''
    tree=XJ_Tree()#树。节点如果对应的是文件则其内容为[time,size,backupTime]，否则为[time]。time为文件创建/修改时间
    backupTime=''#当前时间，由XJFunc.GetCurrentTime函数获得。该变量会在GetStruct和LoadStruct函数中刷新
    def __init__(self):
        self.tree=XJ_Tree()
    def copy(self):
        tree=StructTree()
        tree.tree=self.tree.copy()
        tree.backupTime=self.backupTime
        return tree
    def GetSourceStruct(self):#获取源路径Path.source下的文件结构。如果路径不存在则返回False
        source=Path.source
        if(not os.path.exists(source)):
            return False
        self.backupTime=XJFunc.GetFormatTime()
        tree=self.tree
        tree.ClearTree()
        # iter=tree.GetIter_Root()
        # iter.SetIterData([os.path.getctime(source)])
        iter=tree.GetIter_Root().CreateNext([os.path.getctime(source)],source)
        record={source:iter}
        for root,folders,files in os.walk(source):
            iter=record[root]
            for file in files:
                path=os.path.join(root,file)
                iter.CreateNext([os.path.getmtime(path),os.path.getsize(path)],file)
            for folder in folders:
                path=os.path.join(root,folder)
                record[path]=iter.CreateNext([os.path.getmtime(path)],folder)
        return True
    def LoadStruct(self,backupTime:str):#根据备份时间读取文件树json文件(如果读取失败将返回False
        self.backupTime=backupTime
        return self.tree.LoadJSON(os.path.join(Path.storage,backupTime+'.json'))
    def SaveStruct(self):#保存文件树到json文件(文件名为备份时间self.backupTime)
        self.tree.SaveJSON(os.path.join(Path.storage,self.backupTime+'.json'))








