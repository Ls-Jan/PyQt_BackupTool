
__version__='1.0.0'
__author__='Ls_Jan'


from XJBackup.BaseSystem import BaseSystem

if __name__=='__main__':
    bs=BaseSystem(r'Data\1号')

    bs.SwitchNode_Focus(2)
    rst=bs.GetStructInfo_Focus()
    for data in rst[0]:
        print(data.GetIterData())

