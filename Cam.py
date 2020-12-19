from PyQt5.QtGui import QImage, QWindow
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import *
import random
import cv2
import sys
from PyQt5 import QtGui
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog


class Camera:
    def __init__(self, cam_num = 0):
        self.cam_num = cam_num
        self.cap = None

    def changeCamNum(self, cam_num):
        self.closeCamera()
        self.cam_num = cam_num
        self.cap = cv2.VideoCapture(self.cam_num)
        if not self.cap.isOpened():
            print("Camera couldn't start")

    def initalize(self):
        self.cam_num = self.cam_num
        self.cap = cv2.VideoCapture(self.cam_num)
        if not self.cap.isOpened():
            print("Camera couldn't start")
            #sys.exit()
    
    def closeCamera(self):
        self.cap.release()
    
    def getFrame(self):
        self.ret, self.frame = self.cap.read()
        return self.frame

    def captureStream(self, numFrames):
        pass
    def getBrightness(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)
    def setBrightness(self, val):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, val)

    def setRes(height, width):
        pass


    def list_cameras(self):
        #https://stackoverflow.com/questions/57577445/list-available-cameras-opencv-python?noredirect=1&lq=1
        is_working = True
        dev_port = 0
        working_ports = []
        available_ports = []
        while is_working:
            camera = cv2.VideoCapture(dev_port)
            if not camera.isOpened():
                is_working = False
                print("Port %s is not working." %dev_port)
            else:
                is_reading, img = camera.read()
                w = camera.get(3)
                h = camera.get(4)
                if is_reading:
                    print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_ports.append(dev_port)
                else:
                    print("Port %s for camera ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_ports.append(dev_port)
            dev_port +=1

        return available_ports,working_ports

class ClientWin(QMainWindow):
    def __init__(self, camera = None, *args, **kwargs) -> None:
        super(ClientWin, self).__init__(*args, **kwargs)
        self.setGeometry(100, 100, 1280, 720) 
        self.setMinimumSize(1280, 720);
        if camera != None:
            self.camera = camera
        else:
            self.camera = Camera()
        
        self.initMenuBar()
        self.initChatBox()
        self.initCameraBox()
        self.initComboBox()
        self.initSendTextBox()
        self.initStatusBar()
        self.initSendButton()
        self.initSelfFrame()
        self.initToolbar()
        self.setlayout()
        

    def initComboBox(self):
        self.CameraListBox = QComboBox()
        self.CameraListBox.setToolTip('select camera')
        self.CameraListBox.setToolTipDuration(1000)

    def initStatusBar(self):
        self.status = QStatusBar() 
        self.statusBar().showMessage('Statusbar')
        self.show()

    def initChatBox(self):
        self.ChatWindow = QTextBrowser()
        self.ChatWindow.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ChatWindow.append('Send over a message, go on.')

    def initSendTextBox(self):
        self.SendTextEditor = QTextEdit()
        
    
    def initSendButton(self):
        self.sendButton = QPushButton()
        self.sendButton.setText('send text')

    def initCameraBox(self):
        self.imageLabel = QLabel()
        self.imageLabel.setBackgroundRole(QPalette.Base)
        self.imageLabel.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.imageLabel.setScaledContents(True)
        mar = self.ChatWindow.getContentsMargins()
        self.imageLabel.setMinimumSize(600, 400)
        self.image = QImage("tem.png")
        if self.image.isNull():
            QMessageBox.information(self, "Image Viewer", "Cannot load %s." % "tem.png")
            return

        self.imageLabel.setPixmap(QPixmap.fromImage(self.image))
        self.scaleFactor = 1.0
    
    def initSelfFrame(self):
        self.selfFrame = QLabel()
        self.selfFrame.setBackgroundRole(QPalette.Highlight)
        self.selfFrame.setMinimumSize(100, 100)
        self.image_ = QImage("tem.png")
        if self.image_.isNull():
            QMessageBox.information(self, "Image Viewer", "Cannot load %s." % "tem.png")
            return

        self.selfFrame.setPixmap(QPixmap.fromImage(self.image_))
        self.scaleFactor = 1.0

        self.StartCameraButton = QPushButton()
        self.StartCameraButton.setText("Start Camera")
        

    def createActions(self):
        pass

    def onToolBarButtonClick(self, s):
        print("click", s)

    def setlayout(self):
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        layout_hoz = QVBoxLayout()
        layout_hoz.addWidget(self.CameraListBox)
        layout_hoz.addWidget(self.ChatWindow)

        layout_top = QHBoxLayout()
        layout_bottom = QHBoxLayout()
        layout_vert_bot = QVBoxLayout()
        layout_vert_bot.addWidget(self.selfFrame)
        layout_vert_bot.addWidget(self.StartCameraButton)
        layout_bottom.addLayout(layout_vert_bot)
        layout_bottom.addWidget(self.SendTextEditor) 
        #layout_bottom.SetFixedSize(300, 200)
        layout_bottom.addWidget(self.sendButton)
        widg = QWidget()
        widg.setLayout(layout_bottom)
        widg.setFixedHeight(200)
        layout_top.addWidget(self.imageLabel)
        self.spaceItem = QSpacerItem(610, 610, QSizePolicy.Ignored)
        layout_top.addSpacerItem(self.spaceItem)
        layout_top.addLayout(layout_hoz)
        

        
        #layout_top.addWidget(self.ChatWindow)
        self.generalLayout.addLayout(layout_top)
        self.bottomspaceItem = QSpacerItem(150, 10, QSizePolicy.Expanding)
        self.generalLayout.addSpacerItem(self.bottomspaceItem)

        #self.generalLayout.addLayout(layout_bottom)
        self.generalLayout.addWidget(widg)
        #self.add

    def initMenuBar(self):
        newConn = QAction(QIcon('NewConnection.png'), '&New Connection', self)
        newConn.setShortcut('Ctrl+N')
        newConn.setStatusTip('Start a new connection')
        newConn.triggered.connect(self.newConnection)

        disConn = QAction(QIcon('DisConnection.png'), '&Disconnect Connection', self)
        disConn.setShortcut('Ctrl+D')
        disConn.setStatusTip('Disconnect from connection')
        disConn.triggered.connect(self.disconnectConnection)

        exitAct = QAction(QIcon('exit.png'), '&Exit', self)
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        menubar = self.menuBar()

        Connections = menubar.addMenu('&Connections')
        Connections.addAction(newConn)
        Connections.addAction(disConn)
        Connections.addAction(QAction(QIcon('NewConnection.png'),'&', self))
        Connections.addSeparator()
    
        Connections.addAction(exitAct)

    def initToolbar(self):
        toolbar = QToolBar("Camera Tool Bar") 
        
        #toolbar.setIconSize(QtGui.QSize(16,16))
        self.addToolBar(toolbar)
        
    
    def newConnection(self):
        print("New connection widget")
    def disconnectConnection(self):
        print("Disconnect")

    def selectCamera(self, index):
        self.camera.changeCamNum(index)
        #print(index)



app = QApplication(sys.argv)
win = ClientWin()
win.show()
sys.exit(app.exec_())
