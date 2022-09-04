
__version__='1.0.0'
__author__='Ls_Jan'


import os
import json

__all__=['Path']




class Path:#路径，必须先调用初始化函数Init，禁用构造函数。(本想弄单例类，但发现多此一举，就直接弄成静态数据
    storage=None#数据路径(存放着存档树json文件、文件树json文件、路径列表json文件)
    source=None#源文件路径
    backup=None#备份文件路径
    tree=None#存档树文件路径。该json文件存放的是列表，第一个元素为存档树，第二个是iter_curr节点位置
    def __init__(self):
        raise None
    def Init(path:str):#Path静态数据的初始化，path为库目录路径。库目录下有三类json文件，分别存放存档树、文件树、路径列表。【【如果路径文件缺失的话会抛出异常】】为
        paths=os.path.join(path,'_paths.json')
        tree=os.path.join(path,'_tree.json')
        if(os.path.isdir(path) and os.path.isfile(paths)):
            Path.storage=path
            Path.tree=tree
            with open(paths,'r') as f:
                paths=json.loads(f.read())
                Path.source=paths[0]
                Path.backup=paths[1]
            return 
        raise Exception(f'【路径“{path}”无效】')





