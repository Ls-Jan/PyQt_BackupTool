
__version__='1.0.0'
__author__='Ls_Jan'


import json
import os
from XJImporter import XJImporter
Import=XJImporter(globals()).Import
Import('../XJ_UsefulWidget','XJ_Tree')
Import('./Path','*')

__all__=['ArchiveTree']



class ArchiveTree:#存档树【核心】
    '''
        【存档树】的节点信息为列表，
        列表元素依次是
            文件树(目录结构)的备份时间backupTime(str)
            选中的路径selectedPath(list)[存放的是相对路径]
        补充：
            文件树的父节点指向子节点的key对应着备份时间backupTime(str)，虽然这一点意义都无，但好过用123来设置键key
    '''
    tree=None#XJ_Tree。节点内容为{backupTime:str(),selectedPath:list()}。selectedPath对应结构树的节点位置
    iter_curr=None#当前节点，是self.tree的迭代器。
    iter_focus=None#聚焦节点，是self.tree的迭代器。
    def __init__(self):
        self.tree=XJ_Tree()
    def LoadArchive(self):#读取json文件(读取失败则返回False
        try:
            with open(Path.tree,'r') as f:
                lst=json.loads(f.read())
                self.tree.SetTreeData(lst[0])
                self.iter_curr=self.tree.GetIter_ByPst(lst[1])
                self.iter_focus=self.iter_curr.copy()
            return True
        except:
            return False
    def SaveArchive(self):#保存存档树到json文件
        if(self.iter_curr):
            with open(Path.tree,'w') as f:
                f.write(json.dumps([self.tree.GetTreeData(),self.iter_curr.GetIterPst()], sort_keys=True, ensure_ascii=False, indent=2))        
        else:
            raise Exception('ArchiveTree的iter_curr为None！')






