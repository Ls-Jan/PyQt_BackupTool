# Python_BackupSystem

本项目十分蹩脚，是个自己都不太敢用的玩意儿(因为仍存在不少bug，现在只能说是能运行而已)，
就这还花了好几个月时间(虽然不少时间是拿来玩了，但从萌生出搞这烂活到初步完成这个烂活的确是过了那么长的时间)

<br>

这里简述一下目前有多少问题：<br/>
①、在本备份工具创建了新的备份项目后，备份源路径若是不存在的话那么在再次打开该备份项目时会报错<br/>
②、创建备份节点时即使不选中目录，一样会被选中(见下面的[使用说明](#使用说明)<br/>
③、没有完成“严格恢复”功能(见下面的[使用说明](#使用说明)<br/>
④、没有完成“节点重命名”功能和“节点删除”功能(见下面的[使用说明](#使用说明)<br/>
⑤、没有完成“备份进度条”功能，即创建备份和恢复备份时弹出窗口(就跟在windows复制文件时弹出的进度窗体一样)<br/>
⑥、没有完成“风格样式自定义”功能，也就是换色改大小啥的(该功能不重要)<br/>
⑦、没做过多的测试还不知道有多少隐藏的bug<br/>
⑧、......(不列了。高情商“还有进步空间”，低情商“好烂”<br/>

<br>
<br>


## 碎碎念

①、项目里的Qt控件基本重写过，纯纯的车轮人行为

②、几个月前我那同学在用什么语言来做备份工具 <a href='https://github.com/lraty-li/VisualBranching'>[跳转查看]</a>，问我矩阵啥的，当时我就很疑惑，
为啥要搞矩阵，他说那api要往里头丢矩阵，于是联想到我以前做的其中一个整活 <a href='https://github.com/Ls-Jan/PyQt_MCCloakMaker'>MC披风生成器</a> ，
其中的截图工具的底层实现我是硬生生的一个像素坐标一个像素坐标这样算的，于是我那时就把“要用矩阵”这事给记下了。在这次整活中特意在画布中使用了矩阵
（算是弥补了知识空白？只不过公式是抄书的，啥也没学只知道个模糊概念）

③、前段时间为了管理好python项目(因为要搞多目录跨目录导入)我写了一个专门用于相对路径下模块导入的类 <a href='https://github.com/Ls-Jan/Python_ModuleImporter'>XJImporter</a> ，
正用得挺爽呢，在打包的时候，发现，诶我exe文件咋报错的？几经排查立马确定是我这个类的锅(暂未深究出错根源)，于是就把用到这个类的地方全改成相对导入，并且把模块的测试代码全部搬到项目根路径下，
于是你能在我的这个github项目里看到有两个目录“【仅能脚本运行】”、“【可以打包运行】”，其中“【可以打包运行】”搞的乱七八糟的我都不想维护了。

④、忙完了这阵就要接着忙下一阵了。该项目有空才会继续完善。

<br>
<br>
<br>
<br>

# 【使用说明】

<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/1.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/2.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/3.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/4.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/5.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/6.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/7.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/8.png"/>
<img src="https://github.com/Ls-Jan/Python_BackupSystem/blob/main/RunningResult%5BPNG%5D/9.png"/>

