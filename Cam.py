#zero memory overflow checks
#@TODO fix new connection after 1st connection

from threading import Thread
from threading import ThreadError
import time
import numpy as np
from typing import Text
from PyQt5.QtGui import QImage, QWindow
import string
from client import *
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
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QImage, QPixmap, QPalette, QPainter
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter
from PyQt5.QtWidgets import QLabel, QSizePolicy, QScrollArea, QMessageBox, QMainWindow, QMenu, QAction, \
    qApp, QFileDialog

def randomStringGen(size=6, chars=string.ascii_uppercase + string.digits): #stackoverflow
    return ''.join(random.choice(chars) for _ in range(size))

class Camera:
    #might make it a part of the client
    #@TODO use compression to lower bandwidth
    def __init__(self, cam_num = 0):
        self.cam_num = cam_num
        self.cap = None
        self.height = 720
        self.width = 1280
        self.enabled = False

    def changeCamNum(self, cam_num):
        self.cam_num = cam_num

    def initalize(self):
        self.cap = cv2.VideoCapture(self.cam_num, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            print("Camera couldn't start")
            #sys.exit()
        self.enabled = True
        print("camera started")

    def closeCamera(self):
        if self.cap is not None:
            self.enabled = False
            self.cap.release()
            cv2.destroyAllWindows()
    
    def getFrame(self):
        if self.cap.isOpened():
            self.ret, self.frame = self.cap.read()
            return self.frame
        return None

    def captureStream(self, numFrames):
        pass

    def getBrightness(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)

    def setBrightness(self, val):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, val)

    def setRes(height, width):
        pass
    
    def convToQtLabel(self, frame):
        if frame.all() == None:
            return None 

        filtered = self.applyFiltersToFrame(frame)
        h, w, ch = filtered.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(filtered.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        ret = convert_to_Qt_format.scaled(self.width, self.height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(ret)

    def cameraIsOpen(self):
        return self.enabled
    
    def applyFiltersToFrame(self, frame):
        rgb_im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return rgb_im
        pass

    def list_cameras(self):
        #https://stackoverflow.com/questions/57577445/list-available-cameras-opencv-python?noredirect=1&lq=1
        is_working = True
        dev_port = 0
        working_ports = []
        available_ports = []
        while is_working:
            camer = cv2.VideoCapture(dev_port, cv2.CAP_DSHOW)
            if not camer.isOpened():
                is_working = False
                #print("Port %s is not working." %dev_port)
            else:
                is_reading, img = camer.read()
                w = camer.get(3)
                h = camer.get(4)
                if is_reading:
                    #print("Port %s is working and reads images (%s x %s)" %(dev_port,h,w))
                    working_ports.append(dev_port)
                else:
                    #print("Port %s for camer ( %s x %s) is present but does not reads." %(dev_port,h,w))
                    available_ports.append(dev_port)
            dev_port +=1
        cv2.destroyAllWindows()
        return available_ports, working_ports

class ClientWin(QMainWindow):
    def __init__(self, camera = None, *args, **kwargs) -> None:
        super(ClientWin, self).__init__(*args, **kwargs)
        self.setGeometry(100, 100, 1280, 720) 
        self.setMinimumSize(1280, 720)
        if camera != None:
            self.camera = camera
        else:
            self.camera = Camera()
        self.client = Client()
        self.confimation_text = self.client.confirmation_text
        self.stream_video = False
        
        self.initMenuBar()
        self.initSendButton()
        self.initAudioButton()
        self.initChatBox()
        self.initCameraBox()
        self.initComboBox()
        self.initAudioInputCombo()
        self.initAudioOutputCombo()
        self.initSendTextBox()
        self.initStatusBar()
        self.initSelfFrame()
        self.initToolbar()
        self.setlayout()

        self.checkTr = Thread(target=self.checkConnection, args=(1,), daemon=True)
        self.checkTr.start()
        self.videoTr = Thread(target=self.startCamera, args=(), daemon=False)

        self.video_enabled = False


    def updateSelfFrame(self):
        ret = self.camera.getFrame()
        qt_lab = self.camera.convToQtLabel(ret)
        scaled_qt_lab = qt_lab.scaled(self.selfFrameWidth, self.selfFrameHeight, Qt.IgnoreAspectRatio)
        self.selfFrame.setPixmap(scaled_qt_lab)

    def toggleVideo(self, toggle=True):
        toggle=True
        print(toggle)
        if (not self.camera.enabled and toggle):
            if self.videoTr.is_alive():
                self.videoTr.join()
            self.videoTr = Thread(target=self.startCamera, args=(), daemon=False)
            self.videoTr.start()
            self.video_enabled = True
        else:
            print("Dying")
            self.camera.closeCamera()
            self.video_enabled = False


    
    #zn
    def startCamera(self):
        self.camera.initalize()
        print(self.camera.cameraIsOpen())
        try:
            while self.camera.enabled is True:
                self.updateSelfFrame()
        except RuntimeError as re:
            print(re)
        print("Thread finished")
        
    def onNewConnection(self):
        pass

    def initAudioInputCombo(self):
        self.AudioInputList = QComboBox()
        self.AudioInputList.setPlaceholderText("Select input device")
        self.inflateComboBox(self.AudioInputList)
        self.AudioInputList.currentIndexChanged.connect(self.selectAudioIn)
        self.AudioInputList.setToolTip('Select input device')
        self.AudioInputList.setToolTipDuration(1000)

    def initAudioOutputCombo(self):
        self.AudioOutputList = QComboBox()
        self.AudioOutputList.setPlaceholderText("Select output device")
        self.inflateComboBox(self.AudioOutputList)
        self.AudioOutputList.currentIndexChanged.connect(self.selectAudioOut)
        self.AudioOutputList.setToolTip('Select output device')
        self.AudioOutputList.setToolTipDuration(1000)

    def initComboBox(self):
        self.CameraListBox = QComboBox()
        self.CameraListBox.setPlaceholderText("Select camera device")
        av, wo = self.camera.list_cameras()
        self.inflateComboBox(self.CameraListBox, wo)
        self.CameraListBox.setToolTip('Select camera')
        self.CameraListBox.currentIndexChanged.connect(self.selectCamera)
        self.CameraListBox.setToolTipDuration(1000)

    def initStatusBar(self):
        self.status = QStatusBar() 
        self.statusBar().showMessage('Statusbar')
        self.show()

    def initChatBox(self):
        self.ChatWindow = QTextBrowser()
        self.ChatWindow.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.ChatWindow.append('Send over a message, go on.')
        #self.updateChatBox()

    def initSendTextBox(self):
        self.SendTextEditor = QTextEdit()
        self.SendTextEditor.setPlaceholderText("Write something")
        #self.SendTextEditor.keyPressEvent = self.sendTextChanged
        self.SendTextEditor.installEventFilter(self)

    def initAudioButton(self):
        self.toggleAudioButton = QPushButton()
        self.toggleAudioButton.clicked.connect(self.onClickAudioButton)
        self.toggleAudioButton.setEnabled(False)
        self.toggleAudioButton.setText("a/d audio")
        pass

    def onClickAudioButton(self):
        self.client.toogleSound()

    def eventFilter(self, source, event):
        if (event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return and event.key() != Qt.Key_Shift and
            source is self.SendTextEditor):
            self.onSendButton()
            #print("da")
            return True
        return super(ClientWin, self).eventFilter(source, event)

    def sendTextChanged(self, e):
        #super(ClientWin, self).keyPressEvent(e)
        print(e)
        e.accept()

    def selectCamera(self, index):
        self.camera.closeCamera()
        if self.video_enabled is False: #restart video if already was playing
            return

        if self.videoTr.isAlive():
            self.videoTr.signal = False
            self.camera.changeCamNum(index)
            self.videoTr.join()

        self.videoTr = Thread(target=self.startCamera, args=(), daemon=False)
        self.videoTr.start()
#        
 ##       self.videoTr.start()

    def selectAudioOut(self, index):
        pass

    def selectAudioIn(self, index):

        pass

    def inflateComboBox(self, combo, items=["A", "B"]):
        if combo is None:
            return

        for item in items:
            combo.addItem(str(item))
        
    
    def initSendButton(self):
        self.sendButton = QPushButton()
        self.sendButton.setText('send text')
        self.sendButton.clicked.connect(self.onSendButton)
        self.sendButton.setEnabled(False)
    
    def checkConnection(self, everyXSeconds=5):
        while True:
            #print("Waiting on an incoming connection")
            if self.confimation_text in self.ChatWindow.toPlainText():
                self.sendButton.setEnabled(True)
                self.toggleAudioButton.setEnabled(True)
                self.sendButton.setFocusPolicy(Qt.StrongFocus)
                break
            time.sleep(everyXSeconds)

        self.checkTr.terminate()


    def onSendButton(self):
        self.client.send_data_tcp(self.SendTextEditor.toPlainText(), self.ChatWindow)
        self.SendTextEditor.setText("")


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
        self.selfFrameHeight = 150
        self.selfFrameWidth = 180
        self.selfFrame.setMinimumSize(100, 100)
        self.image_ = QImage("tem.png")
        if self.image_.isNull():
            QMessageBox.information(self, "Image Viewer", "Cannot load %s." % "tem.png")
            return

        self.selfFrame.setPixmap(QPixmap.fromImage(self.image_))
        self.scaleFactor = 1.0

        self.StartCameraButton = QPushButton()
        self.StartCameraButton.setText("Start Camera")
        self.StartCameraButton.clicked.connect(self.toggleVideo)

    def initLogButton(self):
        #open dialog and write all messages to a text
        pass
        

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
        layout_hoz_h = QHBoxLayout()
        layout_hoz_h.addWidget(self.CameraListBox)
        layout_hoz_h.addWidget(self.AudioOutputList)
        layout_hoz_h.addWidget(self.AudioInputList)

        layout_hoz.addLayout(layout_hoz_h)

        layout_hoz.addWidget(self.ChatWindow)

        layout_top = QHBoxLayout()
        layout_bottom = QHBoxLayout()
        layout_vert_bot = QVBoxLayout()
        layout_vert_bot.addWidget(self.selfFrame)

        #audio cam on the bot
        layout_vert_bot_h = QHBoxLayout()
        layout_vert_bot_h.addWidget(self.StartCameraButton)
        layout_vert_bot_h.addWidget(self.toggleAudioButton)
        
        layout_vert_bot.addLayout(layout_vert_bot_h)

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
        dl = NewConnDialog(self)
        if dl.exec_():
            ret = dl.getLineTextValue()
            print(ret)
            # if self.client is not None:
            #     del(self.client)
            #     self.client = Client()
            try:
                self.client.set_server_addr()   
                self.client.send_data_tcp(ret)
                self.updateChatBox()
            except:
                print("sth")

        self.sendButton.setEnabled(False)
        self.toggleAudioButton.setEnabled(False)
        #handle client 
        
    def disconnectConnection(self):
        print("Disconnect")


        #print(index)

    def updateChatBox(self):
        self.ChatWindow.clear()
        self.ChatWindow.append("Send over a message")
        self.hookChatWindow()
        pass

    def hookChatWindow(self):
        try:
            self.client.startThreads(self.ChatWindow)
        except ThreadError as e:
            print(str(e))

class NewConnDialog(QDialog):
    def __init__(self, parent=None, *args, **kwargs):
        super(NewConnDialog, self).__init__(*args, **kwargs)
        self.setWindowTitle("Set up a new connection") 
        self.parent = parent
        layout = QVBoxLayout()
        layout_hoz = QHBoxLayout()
        self.setMaximumSize(300, 80)
        
        self.label = QLabel("Enter recipients ip")
        self.label.setText("Enter recipients ip")
        self.lineEdit = QLineEdit()
        self.lineEdit.setAlignment(Qt.AlignRight)
        self.lineEdit.textChanged.connect(self.onlineEditChanged)
        self.setWhatsThis("Insert ip - xxx.xxx.xxx.xxx")
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.lineEdit.setMinimumWidth(100)

        layout_hoz.addWidget(self.label)
        layout_hoz.addWidget(self.lineEdit)

        self.cancelButton = QPushButton()
        self.cancelButton.setText("Close")
        self.cancelButton.clicked.connect(self.close)
        self.cancelButton.setFocusPolicy(Qt.NoFocus)
        self.cancelButton.setFocusPolicy(Qt.StrongFocus)
        self.connectButton = QPushButton()
        self.cancelButton.setAutoDefault(False)
        self.connectButton.setText("Connect")
        self.connectButton.clicked.connect(self.onconnectbutton)
        self.connectButton.setDisabled(True)
        layout_bot = QHBoxLayout()
        layout_bot.setAlignment(Qt.AlignRight)

        layout_bot.addWidget(self.cancelButton)
        layout_bot.addWidget(self.connectButton)

        layout.addLayout(layout_hoz)
        layout.addLayout(layout_bot)
        
        self.setLayout(layout)

    def onconnectbutton(self):
        #parent -> execute get value from dialog  -> then dispose
        if self.parent is None:
            print("No parent")
        self.accept()
        pass
    def onlineEditChanged(self, text):
        self.checkText(text)
        pass

    def checkText(self, text):
        if(self.checkIpv4Adress(text)):
            print("check")
            self.connectButton.setEnabled(True)
        else:
            print("no check")
            self.connectButton.setEnabled(False)

    def getLineTextValue(self):
        return self.lineEdit.text()

    def isIPv4(self, s):
        try: return str(int(s)) == s and 0 <= int(s) <= 255
        except: return False
         
    def checkIpv4Adress(self, ip):
        if ip.count(".") == 3 and all(self.isIPv4(i) for i in ip.split(".")):
            return True
        else:
            return False

    def __del__(self):
        self.lineEdit.setText = ""



#hold a client, and update on 


app = QApplication(sys.argv)
win = ClientWin()
win.show()
sys.exit(app.exec_())
