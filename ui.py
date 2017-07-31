import pandas as pd
import run_test
import sys
from PyQt5 import QtCore
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtWidgets import *

class MainWindow(QWidget):

    def __init__(self):
       QWidget.__init__(self)
       self.setGeometry(100,100,600,400)

       oImage = QImage("beach")
       sImage = oImage.scaled(QSize(600,400))                   # resize Image to widgets size
       palette = QPalette()
       palette.setBrush(10, QBrush(sImage))                     # 10 = Windowrole
       self.setPalette(palette)

       self.combo = QComboBox(self)
       df = pd.read_csv("campaign_index.csv")
       campaigns =  ["All"]  + list(df["Campaign"])
       for i in campaigns:
           self.combo.addItem(i)

       self.combo.move(100, 50)

       button = QPushButton('Check', self)
       button.setToolTip('Click check to run URL checker on selected campaign')
       button.move(100, 70)
       button.clicked.connect(self.on_click)
       # button.clicked(self.on_click)
       # #QGraphicsObject.connect(self.button, QtCore.SIGNAL('clicked()'), self.onClicked)

       # combo.activated[str].connect(self.run_url_checker)

       ##self.label = QLabel('Test', self)                        # test, if it's really backgroundimage
       #self.label.setGeometry(50,50,200,50)
       self.setWindowTitle('Broken URL Checker')
       self.center()
       self.show()

    def on_click(self):
        text = str(self.combo.currentText())
        run_test.run_check(text)

    # def run_url_checker(self, text):
    #     run_test.run_check(text)

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


if __name__ == "__main__":

    app = QApplication(sys.argv)
    oMainwindow = MainWindow()
    sys.exit(app.exec_())
