
__version__='1.0.0'
__author__='Ls_Jan'


import sys
from PyQt5.QtWidgets import QApplication

from XJBackup import BackupSystem


if __name__=='__main__':
    app = QApplication(sys.argv)
    system=BackupSystem(r'Data\1号')
    system.show()
    sys.exit(app.exec())
    exit()


