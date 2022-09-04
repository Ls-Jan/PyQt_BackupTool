



def Importer(module,args=None):
    '''
        模块导入，用于导入模块，返回的是导入结果。如果args长度大于1那么会返回列表(因为导入结果有多个)
        module为模块名所在路径(不需要.py后缀)，支持相对路径：
            导入上一级名为M的模块，那么module='../M'
            导入目录A下的名为M的模块，那么module='A/M'
        args为从module中导入的变量名列表：
            如果args为空，那么仅导入模块module
            如果args不为空，那么将导入模块module中的变量
            
        例子：
            Importer('M')：返回模块M
            Importer('../M')：返回上级目录中的模块M
            Importer('A/M')：返回A目录下的模块M
            Importer('A/M',('info','func'))：返回A目录下的模块M中名为info和func的变量
        
        注：
            ①、请不要在args传入各种奇奇怪怪的值，我可没做好各种极端情况的预防工作
            ②、import失败必然会抛出异常，这没得洗的。请注意自己的代码规范
            ③、py的导入出现“鸡蛋先后问题”算是很日常了。请将该文件复制到要跨目录导入的脚本所在的目录下
    '''
    import sys
    import os
    absolutePath=os.path.split(__file__)[0]#调用该函数的文件所在的路径(绝对路径)
    relativePath,__module=os.path.split(module)#模块所在目录(相对路径)、模块名
    path=os.path.join(absolutePath,relativePath)#模块所在路径(绝对路径)
    
    sys.path.append(path)#将路径临时加入到系统列表中
    if(args):
        exec(f'from {__module} import {",".join(args)}')
        rst=[]#可惜不能用这条语句rst=[eval(val) for val in args]
        for __arg in args:
            rst.append(eval(__arg))
    else:
        exec(f'import {__module}')
        rst=[eval(__module)]
    sys.path.pop()#移除临时加入的路径
    return rst if(len(rst)>1) else rst[0]


exit()

Importer('json')
Importer('json',('load',))
Importer('XJDrawer/XJFunc',('BinarySearcs',))
exit()








import numpy as np
# T=np.array([[1,0,0],[0,1,0],[0,0,lambda:None]])
# A=np.array([[1,0,0],[0,1,0],[0,0,'3']])
# B=np.array([[1,0,0],[0,1,0],[0,0,1]])
# C=np.array([[1,0,0],[0,1,0],[0,0,1]])


# def MatDot(A,B):#主要用途仅仅是研究矩阵点乘



from enum import Enum

class ButtonType(Enum):#按键类型
    Left=1#左键
    Right=2#右键
    Middle=4#中键
    def __str__(self):
        return self.name
print(ButtonType.Left)
print(ButtonType)
print(f'{type(ButtonType.Left).__name__}')
exit()


a = np.array([
              [[1,1,1],
              [1,1,1]],
              [[10,10,10],
              [10,10,10]],
              [[100,100,100],
              [100,100,100]],
              [[1000,1000,1000],
              [1000,1000,1000]],
                ])
c= np.array([
              [1,1,1],
              [10,10,10],
              [100,100,100],
              [1000,1000,1000],
                ])
b = np.array([
              [[[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],],

              [[[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],
              [[1,2,3,4],
               [5,6,7,8],
               [9,10,11,12]],],
               ])

print("a.shape: ",a.shape)
print("c.shape: ",c.shape)
print("b.shape: ",b.shape)
print("a.dot(b).shape: ",a.dot(b).shape)
print("c.dot(b).shape: ",c.dot(b).shape)
print("运算结果: \n",a.dot(b))
print("运算结果: \n",c.dot(b))




switch=2
if switch==2:
    pass











if switch==1:
    lst=[-1,1,2,3,6,8,9,10]#升序
    def BinarySearch(lst,pos):
        L=0
        R=len(lst)-1
        M=(L+R)>>1
        while(L+1<R):
            M=(L+R)>>1
            if(lst[M]>pos):
                R=M
            elif(lst[M]<pos):
                L=M
            else:
                break
        if(len(lst)>0):
            print(L,M,R)
            print(lst[L],lst[M],lst[R])
            absR=abs(lst[R]-pos)
            absM=abs(lst[M]-pos)
            absL=abs(lst[L]-pos)
            tmp=(L,absL) if absL<absR else (R,absR)
            if(tmp[1]<absM):
                absM=tmp[0]
        return M

    print(BinarySearch(lst,5))



















