pyrcc5 -o src.py  src.qrc
pause
: src.py 为生成的二进制描述文件  
: src.qrc 为我们写的 XML 资源文件pyinstaller -w -D --clean XJ_MCAutoFishing.py

:将图片资源转换为py文件便于载入内存中：
:https://blog.csdn.net/gongjianbo1992/article/details/105361880

