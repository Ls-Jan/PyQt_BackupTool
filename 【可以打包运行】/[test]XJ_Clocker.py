
__version__='1.0.0'
__author__='Ls_Jan'


from XJ_UsefulWidget.XJ_Clocker import XJ_Clocker
from time import sleep

if __name__=='__main__':
    clocker=XJ_Clocker()
    clocker.SetCallback(lambda:print("【超时任务！！！】",clocker.GetStatus()[1]),400)
    clocker.Start()
    for i in range(100):
        sleep(0.01)
        print(clocker.GetStatus())
    clocker.Pause()
    print(clocker.GetStatus())
