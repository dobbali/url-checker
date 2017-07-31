import pandas as pd
import run_test
import sys
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPalette, QBrush
from PyQt5.QtWidgets import *
import sys
import datetime
from urlchecker import DataPull
import sys
import os
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import QApplication, QWidget, QDesktopWidget
from PyQt5.QtGui import QIcon




class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()


    def initUI(self):

        screen = QDesktopWidget()
        a = screen.screenGeometry()
        w = a.width() #1440
        h = a.height() #900

        #layout = QFormLayout(self)

        self.qle = QLineEdit(self)
        self.qle.move(w/24, h/15)
        self.qle.setFixedWidth(w/3.6)
        self.qle.setPlaceholderText("Eg: /Users/mdobbali/Desktop/Test")

        #layout.addRow(qle)
        # qle.setEchoMode(QLineEdit.Password)

        self.lbl = QLabel(self)
        self.lbl.setAlignment(Qt.AlignCenter)
        self.lbl.move(w/24, h/22.5)
        self.lbl.setText("Enter Path for Results:")



        self.lbl2 = QLabel(self)
        self.lbl2.setAlignment(Qt.AlignCenter)
        self.lbl2.move(w/24, h/7.5)
        self.lbl2.setText("Select Campaign for URL checking")


        self.toto = QFrame(self)
        self.toto.setFrameShape(QFrame.HLine)
        self.toto.setFrameShadow(QFrame.Sunken)
        self.toto.move(w/23, h/11.5)
        self.toto.setFixedWidth(w/ 2.545454)


        self.combo = QComboBox(self)
        df = pd.read_csv("campaign_index.csv")
        campaigns = ["All"] + list(df["Campaign"]) + ["site links"]
        for i in campaigns:
            self.combo.addItem(i)
        self.combo.move(w/ 24, h/6.42857)
        self.combo.setFixedWidth(w/3.5)


        self.lbl3 = QLabel(self)
        self.lbl3.setAlignment(Qt.AlignCenter)
        self.lbl3.move(w/8, h/5)
        self.lbl3.setText("-------------OR--------------")


        button = QPushButton(' Set Path ', self)
        button.setToolTip('Click to Set Path to find results file')
        button.move(w/3.096774, h/ 16.071428)
        button.clicked.connect(self.set_path)

        button2 = QPushButton('Run Check', self)
        button2.setToolTip('Click run to start URL checking process on selected campaign')
        button2.move(465, 136)
        button2.clicked.connect(self.get_data_check_url)


        self.lbl3 = QLabel(self)
        self.lbl3.setAlignment(Qt.AlignCenter)
        self.lbl3.move(w/6.2, h/3.91304)
        self.lbl3.setText("Upload URL Files")


        button3 = QPushButton('Upload and Run', self)
        button3.setToolTip('Upload Csv File with columns identifier, url')
        button3.move(w/6.69767, h/3.461538)
        button3.clicked.connect(self.openFileNamesDialog)


        #qle.textChanged[str].connect(self.create_dir)

        # Background Image
        oImage = QImage("star-wars-3.jpg")
        sImage = oImage.scaled(QSize(w/1.2, h/1.125))  # resize Image to widgets size
        palette = QPalette()
        palette.setBrush(10, QBrush(sImage))  # 10 = Windowrole
        self.setPalette(palette)

        #
        self.setGeometry(100, 100, w/1.2, h/1.125)
        self.setWindowTitle('Broken URL Checker')
        self.center()
        self.show()



    def openFileNamesDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "Select URL files", "",
                                                "All Files (*);;CSV files (*.csv)", options=options)
        if files:
            print(files)
            run_test.run_check_on_files(files[0])


    def set_path(self):
        path = self.qle.text()
        if os.path.isdir(path + "/"+ datetime.datetime.today().strftime('%Y-%m-%d')+"-campaign_reports"):
            pass
        else:
            os.mkdir(path + "/"+ datetime.datetime.today().strftime('%Y-%m-%d')+"-campaign_reports")


    def get_data_check_url(self, campaign):
        path = self.qle.text()
        final_path =  path + "/"+ datetime.datetime.today().strftime('%Y-%m-%d')+"-campaign_reports"
        text = str(self.combo.currentText())
        run_test.run_check(text, final_path)


    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())



if __name__ == '__main__':
    app = QApplication(sys.argv)
    # screen = app.primaryScreen()
    # print('Screen: %s' % screen.name())
    # size = screen.size()
    # print('Size: %d x %d' % (size.width(), size.height()))
    # rect = screen.availableGeometry()
    # print('Available: %d x %d' % (rect.width(), rect.height()))
    ex = Example()
    sys.exit(app.exec_())


#


