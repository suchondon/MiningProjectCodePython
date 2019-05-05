import sys
import subprocess
import os
import time
import atexit
import signal
import requests
import re
import configparser
import socket
from decimal import Decimal
from influxdb import InfluxDBClient
from datetime import datetime
from threading import Thread
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QLineEdit, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSlot

#global benchmarkFlag
global NotifyFlag
global miningFlag
global MiningProcess
global checkStart
global GPUCheckFlag
global blacklist
global selectAlgo

checkStart = 0 
pastAlgo = ""


def mining(wallet):
    global MiningProcess,checkStart,miningFlag,selectAlgo
    algo = selectAlgo
    print(algo+" | "+wallet)
    miningFlag=True
    try:
        getFromPool = requests.get(url='https://www.zpool.ca/api/status')
        data  = getFromPool.json()
    except requests.exceptions.RequestException:
        pass
    MiningProcess = subprocess.Popen(os.getcwd()+r'\miner\ccminer\ccminer-x64.exe -b 4068 -a '+algo+' -o stratum+tcp://'+algo+'.mine.zpool.ca:'+str(data[algo]['port'])+' -u '+wallet+' -p ID=Test01,c=BTC',shell=False,creationflags=subprocess.CREATE_NEW_CONSOLE)
    checkStart = 1
    atexit.register(MiningProcess.kill)
    TcheckProfit = Thread(target=checkProfit, args=(wallet,))
    TcheckProfit.daemon = True
    TcheckProfit.start()
    while miningFlag:
        if MiningProcess.poll()!=None:
            MiningProcess = subprocess.Popen(os.getcwd()+r'\miner\ccminer\ccminer-x64.exe -b 4068 -a '+algo+' -o stratum+tcp://'+algo+'.mine.zpool.ca:'+str(data[algo]['port'])+' -u '+wallet+' -p ID=Test01,c=BTC',shell=False,creationflags=subprocess.CREATE_NEW_CONSOLE)
            atexit.register(MiningProcess.kill)
        time.sleep(1)

def checkProfit(wallet):
    global miningFlag,MiningProcess,selectAlgo
    while miningFlag:
        limitTime = readConfig('mining','timeprofit','config.ini')
        try:
            getWallet = requests.get(url='https://www.zpool.ca/api/wallet?address='+wallet)
            data  = getWallet.json()
        except requests.exceptions.RequestException:
            pass
        
        money = Decimal(data['unsold'])
        if limitTime!='':
            limitTime = int(limitTime)
            count = 1
            while miningFlag and count<=limitTime:
                print("count Switch")
                time.sleep(1)
                count+=1
            try:
                getWallet = requests.get(url='https://www.zpool.ca/api/wallet?address='+wallet)
                data  = getWallet.json()
            except requests.exceptions.RequestException:
                pass
            
            newmoney = Decimal(data['unsold'])
            if newmoney==money and miningFlag:
                saveConfig('blacklist',selectAlgo,'1','blacklist.txt')
                print('Add '+selectAlgo)
            if miningFlag:
                print("check Profit")
                linetoken = readConfig('notify','tokenline','config.ini')
                line(linetoken,'check Profit')
                switchAlgo(wallet)


def switchAlgo(wallet):
    global MiningProcess,miningFlag,pastAlgo,checkStart,blacklist,selectAlgo
    try:
        x = requests.get(url='https://www.zpool.ca/json/algo_profitability.json')
        data  = x.json()
    except requests.exceptions.RequestException:
        pass
    profit = 0.0
    blacklist = ['']
    AlgoProfit = {}
    selectAlgo = ""
    algo = ['allium','bitcore','blake2s','c11','groestl','hmq1725','keccakc',
            'lbry','lyra2v2','lyra2v3','lyra2z','myr-gr','neoscrypt','nist5',
            'phi2','polytimos','quark','qubit','scrypt','sha256t','sib',
            'skein','skunk','sonoa','timetravel','tribus','x11','x13','x14',
            'x16r','x16s','x17']
    for i in algo:
        block = readConfig('blacklist',i,'blacklist.txt')
        if block!='':
            block = int(block)
            if block==1:
                blacklist.append(i)

    for i in algo:
        data[i].reverse()
        profit=float(data[i][0][1])
        AlgoProfit[i] = profit
    for i in algo:
        for j in blacklist:
            if i==j:
                AlgoProfit.pop(i)
    
    selectAlgo = max(AlgoProfit,key=AlgoProfit.get)
                

    if checkStart==0:
        pastAlgo = selectAlgo
        mining(wallet)
    elif selectAlgo==pastAlgo:
        pass
    elif selectAlgo!=pastAlgo:
        pastAlgo = selectAlgo
        miningFlag = False
        time.sleep(1)
        MiningProcess.kill()
        mining(wallet)

# def benchmark(wallet):
#     count = 1
#     global benchmarkFlag
#     benchmarkFlag = True
#     getFromPool = requests.get(url='https://www.zpool.ca/api/status')
#     data  = getFromPool.json()
#     algo = ['allium','bitcore','blake2s','c11','groestl','hmq1725',
#             'keccakc','lbry','lyra2v2','lyra2v3','lyra2z','myr-gr',
#             'neoscrypt','nist5','phi2','polytimos','quark','qubit',
#             'scrypt','sha256t','sib','skein','skunk','sonoa','timetravel',
#             'tribus','x11','x13','x14','x16r','x16s','x17']
#     for i in algo:
#         benchmarkProcess = subprocess.Popen(os.getcwd()+r'\miner\ccminer\ccminer-x64.exe -b 4068 -a '+i+' -o stratum+tcp://'+i+'.mine.zpool.ca:'+str(data[i]['port'])+' -u '+wallet+' -p ID=Test01,c=BTC',shell=False,creationflags=subprocess.CREATE_NEW_CONSOLE)
#         while(benchmarkFlag and count<=600):
#             time.sleep(1)
#             count+=1
#         count = 1
#         hashrate = float(getHashRate())
#         if(benchmarkFlag):
#             saveConfig('algorithm',i,str(hashrate),'benchmark')
#         while(benchmarkFlag and count<=60):
#             time.sleep(1)
#             count+=1
#         count = 1
#         hashrate2 = float(getHashRate())
#         if(hashrate2>hashrate):
#             if(benchmarkFlag):
#                 saveConfig('algorithm',i,str(hashrate2),'benchmark')
#         time.sleep(1)
#         benchmarkProcess.kill()
#         if(benchmarkFlag):
#             pass
#         else:
#             break

def getHashRate():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '127.0.0.1'
        port = 4068
        s.connect((host, port))
        s.send("summary".encode())
        msg = str(s.recv(4096))         
        msg = msg.split(';')
        s.close()
        time.sleep(1)
        hashrate = msg[5].split('=')
        return hashrate[1]
    except socket.error:
        return '0'

def getAlgorithm():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '127.0.0.1'
        port = 4068
        s.connect((host, port))
        s.send("summary".encode())
        msg = str(s.recv(4096))
        msg = msg.split(';')
        s.close()
        time.sleep(1)
        algo = msg[3].split('=')
        return algo[1]
    except socket.error:
        return ''

def saveConfig(section,field,data,filename):
    try:
        config = configparser.ConfigParser()
        config.read(filename)
        config[section][field] = data
        with open(filename, 'w') as filedata:
            config.write(filedata)
    except KeyError:
        config = configparser.ConfigParser()
        config.read(filename)
        config.add_section(section)
        config[section][field] = data
        with open(filename, 'w') as filedata:
            config.write(filedata)

def readConfig(block,field,filename):
    try:
        config = configparser.ConfigParser()
        config.read(filename)
        return config[block][field]
    except KeyError:
        return ''


def facebook(facetoken,id,msg):
    try:
        url = 'https://graph.facebook.com/'+id+'/feed?access_token='+facetoken
        result = requests.post(url,data={'message':msg})
        return(result.status_code)
    except requests.exceptions.RequestException:
        pass
    
                  
def line(linetoken,msg):
    try:
        url = 'https://notify-api.line.me/api/notify'
        headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+linetoken}
        result = requests.post(url, headers=headers, data = {'message':msg})
        return(result.status_code)
    except requests.exceptions.RequestException:
        pass
    


def sendDataToDB(host,port,user,password,dbname,clientname):
        process = subprocess.Popen(os.getcwd()+r'\GPU\nvidia-smi.exe --format=csv,noheader --query-gpu=gpu_name,utilization.gpu,utilization.memory,fan.speed,temperature.gpu', shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
        GPUValue = str(process)
        newValue = GPUValue.replace("%", "")
        newValue = newValue.replace(" ", "")
        Value = newValue.split(",")

        json_body = [
                {
                    "measurement": clientname, 
                    "time": datetime.utcnow(), 
                    "fields": { 
                        "load": Value[1],
                        "memory": Value[2],
                        "fan": Value[3],
                        "temperature": Value[4],
                        "algorithm": getAlgorithm(),
                        "hashrate": getHashRate()

                }
            }
        ]

        client = InfluxDBClient(host, port, user, password, dbname)
        client.write_points(json_body)


class App(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Crypto-currency Mining Support System'
        self.left = 200
        self.top = 200
        self.width = 640
        self.height = 480
        self.initUI()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.labelTokenLine = QLabel('Line', self)
        self.labelTokenLine.move(35,20)
        self.labelTokenFacebook = QLabel('Facebook', self)
        self.labelTokenFacebook.move(20,50)

    
        self.labelGPU = QLabel('', self)
        self.labelGPU.move(20,350)
        self.labelGPU.setStyleSheet('font: 32px')
        self.labelGPUValue = QLabel('', self)
        self.labelGPUValue.move(20,400)
        self.labelGPUValue.setStyleSheet('font: 26px')

        self.labelNotifyTime = QLabel('Time to Notify<br>(minute)', self)
        self.labelNotifyTime.move(20,120)
        self.textboxNotifyTime = QLineEdit(self)
        self.textboxNotifyTime.move(90, 117)
        self.textboxNotifyTime.resize(50,20)


        self.labelIPaddress = QLabel('IP Address', self)
        self.labelIPaddress.move(320,20)
        self.textboxIPaddress = QLineEdit(self)
        self.textboxIPaddress.move(380, 20)
        self.textboxIPaddress.resize(150,20)
        
        self.labelpot = QLabel(':', self)
        self.labelpot.move(532,20)
        self.labelpot.setStyleSheet('font: 16px')
        self.textboxPort = QLineEdit(self)
        self.textboxPort.move(540, 20)
        self.textboxPort.resize(50,20)

        self.labeluser = QLabel('Username', self)
        self.labeluser.move(320,52)
        self.textboxuser = QLineEdit(self)
        self.textboxuser.move(380, 50)
        self.textboxuser.resize(100,20)

        self.labelPassword = QLabel('Password', self)
        self.labelPassword.move(485,52)
        self.textboxPassword = QLineEdit(self)
        self.textboxPassword.setEchoMode(QLineEdit.Password)
        self.textboxPassword.move(535, 50)
        self.textboxPassword.resize(100,20)

        self.labelDBname = QLabel('Database name', self)
        self.labelDBname.move(320,82)
        self.textboxDBname = QLineEdit(self)
        self.textboxDBname.move(400, 80)
        self.textboxDBname.resize(150,20)

        self.labelClientname = QLabel('Client name', self)
        self.labelClientname.move(339,107)
        self.textboxClientname = QLineEdit(self)
        self.textboxClientname.move(400, 105)
        self.textboxClientname.resize(150,20)

        self.labelWallet = QLabel('Wallet', self)  
        self.labelWallet.move(18,202)
        self.textboxWallet = QLineEdit(self)
        self.textboxWallet.move(50, 200)
        self.textboxWallet.resize(250,20)


        self.labelMigingname = QLabel('Mining name', self)
        self.labelMigingname.move(18,232)
        self.textboxMigingname = QLineEdit(self)
        self.textboxMigingname.move(80, 230)
        self.textboxMigingname.resize(120,20)


        self.btnTokenLine = QPushButton('Token Line', self)
        self.btnTokenLine.setToolTip('Input Token Line')
        self.btnTokenLine.move(80,20) 
        self.btnTokenLine.clicked.connect(self.on_click_saveLineToken)

        self.btnTokenFacebook = QPushButton('Token Facebook', self)
        self.btnTokenFacebook.setToolTip('Input Token Facebook')
        self.btnTokenFacebook.move(80,50) 
        self.btnTokenFacebook.clicked.connect(self.on_click_saveFacebookToken)

        self.btnID = QPushButton('ID', self)
        self.btnID.setToolTip('Input Facebook ID')
        self.btnID.resize(30,23)
        self.btnID.move(170,50)
        self.btnID.clicked.connect(self.on_click_saveFacebookID)


        self.btnStart = QPushButton('Start', self)
        self.btnStart.setStyleSheet('font: 64px')
        self.btnStart.resize(200,100)
        self.btnStart.move(350,190)
        self.btnStart.clicked.connect(self.startmining)

        self.btnSavedashboard = QPushButton('Save influxDB config', self)
        self.btnSavedashboard.setToolTip('Setting to use dashboard')
        self.btnSavedashboard.resize(200,23)
        self.btnSavedashboard.move(390,132)
        self.btnSavedashboard.clicked.connect(self.setDashboard)

        self.btnSaveMining = QPushButton('Save mining config', self)
        self.btnSaveMining.setToolTip('Save setting for start mining')
        self.btnSaveMining.resize(150,23)
        self.btnSaveMining.move(40,260)
        self.btnSaveMining.clicked.connect(self.saveMiningConfig)


        self.btnTestNotify = QPushButton('TEST Notify', self)
        self.btnTestNotify.setToolTip('Test Notify')
        self.btnTestNotify.move(120,80) 
        self.btnTestNotify.clicked.connect(self.on_click_TestNotify)


        self.btnTimeNotify = QPushButton('Set Time', self)
        self.btnTimeNotify.setToolTip('Set time notify')
        self.btnTimeNotify.move(150,115) 
        self.btnTimeNotify.clicked.connect(self.on_click_saveTimeNotify)


        GPUInfo = Thread(target=self.GPUInfo) 
        GPUInfo.daemon = True
        GPUInfo.start()

        sendToDB = Thread(target=self.sendToDB)
        sendToDB.daemon = True
        sendToDB.start()

        Notify = Thread(target=self.runNotify)
        Notify.daemon = True
        Notify.start()

        self.setToStart()


    @pyqtSlot()
    def on_click_TestNotify(self):

        LineValue = readConfig('notify','tokenline','config.ini')
        FacebookValue = readConfig('notify','tokenfacebook','config.ini')
        FacebookIDValue = readConfig('notify','facebookID','config.ini')

        alert = QMessageBox(self)
        alert.setStandardButtons(QMessageBox.Close)
        alert.setIcon(QMessageBox.Information)
        alert.setWindowTitle('Result of notification')


        if FacebookValue != "" and FacebookIDValue != "" and LineValue != "":
            statusLine = line(LineValue,'LINE notification test')
            statusFacebook = facebook(FacebookValue,FacebookIDValue,'FACEBOOK notification test')
            if statusLine==200 and statusFacebook==200:
                alert.setText("<font color='green'>Line notification test Success</font><br><br><font color='green'>Facebook notification test Success</font>")
                alert.exec_()
                
            elif statusLine==200:
                alert.setText("<font color='green'>Line notification test Success </font><br><br><font color='red'>Facebook notification test Fail</font")
                alert.exec_()
                
            elif statusFacebook==200:
                alert.setText("<font color='green'>Facebook notification test Success</font><br><br><font color='red'>Line notification test Fail</font>")
                alert.exec_()
            else:
                alert.setText("<font color='red'>Line notification test Fail</font><br><br><font color='red'>Facebook notification test Fail</font>")
                alert.exec_()

        elif FacebookValue != "" and FacebookIDValue != "":
            statusFacebook = facebook(FacebookValue,FacebookIDValue,'FACEBOOK notification test')
            if statusFacebook==200:
                alert.setText("<font color='green'>Facebook notification test Success</font>")
                alert.exec_()
            else:
                alert.setText("<font color='red'>Facebook notification test Fail</font>")
                alert.exec_()

        elif LineValue != "":
            statusLine = line(LineValue,'LINE notification test')
            if statusLine==200:
                alert.setText("<font color='green'>Line notification test Success</font>")
                alert.exec_()
            else:
                alert.setText("<font color='red'>Line notification test Fail</font>")
                alert.exec_()

        else:
            alert.setText("<font color='red'>Line Token is Empty</font><br><br><font color='red'>Facebook Token is Empty</font>")
            alert.setIcon(QMessageBox.Critical)
            alert.exec_()

    def on_click_saveLineToken(self):
        LineValue = readConfig('notify','tokenline','config.ini')
        inputbox = QInputDialog(self)
        inputbox.setWindowTitle('Line token')
        inputbox.setInputMode( QInputDialog.TextInput) 
        inputbox.setLabelText('Input Line token') 
        inputbox.setTextValue(LineValue)                       
        inputbox.resize(400,100)                             
        ok = inputbox.exec_()                                
        lineToken = inputbox.textValue()
        if ok:
            saveConfig('notify','tokenline',lineToken,'config.ini')
        else:
            pass
        

    def on_click_saveFacebookToken(self):
        FacebookValue = readConfig('notify','tokenfacebook','config.ini')
        inputbox = QInputDialog(self)
        inputbox.setWindowTitle('Facebook token')
        inputbox.setInputMode( QInputDialog.TextInput) 
        inputbox.setLabelText('Input Facebook token')
        inputbox.setTextValue(FacebookValue)                         
        inputbox.resize(400,100)
        ok = inputbox.exec_()                    
        FacebookToken = inputbox.textValue()
        if ok:
            saveConfig('notify','tokenfacebook',FacebookToken,'config.ini')
        else:
            pass
        

    def on_click_saveFacebookID(self):
        FacebookIDValue = readConfig('notify','facebookID','config.ini')
        inputbox = QInputDialog(self)
        inputbox.setWindowTitle('Facebook ID')
        inputbox.setInputMode( QInputDialog.TextInput) 
        inputbox.setLabelText('Input Facebook ID')
        inputbox.setTextValue(FacebookIDValue)                         
        inputbox.resize(250,100)                             
        ok = inputbox.exec_()                                
        FacebookID = inputbox.textValue()
        if ok:
            saveConfig('notify','facebookID',FacebookID,'config.ini')
        else:
            pass

    def GPUInfo(self):
        while True:
            GPUprocess = subprocess.Popen(os.getcwd()+r'\GPU\nvidia-smi.exe --format=csv,noheader --query-gpu=gpu_name,utilization.gpu,utilization.memory,fan.speed,temperature.gpu', shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
            time.sleep(1)
            GPUValue = str(GPUprocess)
            Value = GPUValue.split(",")
            self.labelGPU.setText(Value[0])
            self.labelGPU.adjustSize()
            self.labelGPUValue.setText('Load '+Value[1]+' Memory'+Value[2]+' Fan'+Value[3]+' '+Value[4]+' '+u'\u2103')
            self.labelGPUValue.adjustSize()
        


    def on_click_saveTimeNotify(self):
        SaveNotifyTime = Thread(target=self.saveNotifyTime)
        SaveNotifyTime.daemon = True
        SaveNotifyTime.start()
        

    def saveNotifyTime(self):
        global NotifyFlag
        try:
            timenotify = self.textboxNotifyTime.text()
            timenotify = float(timenotify)
            timenotify = (timenotify*60)
            timenotify = int(timenotify)
            saveConfig('notify','notifyTime',str(timenotify),'config.ini')
            NotifyFlag = False
        except ValueError:
            pass
        

    def runNotify(self):
        global NotifyFlag
        count = 1
        while True:
            NotifyFlag=True
            timenotify = readConfig('notify','notifytime','config.ini')
            if timenotify !='':
                timenotify = int(timenotify)
                while(NotifyFlag and count <=timenotify):
                    time.sleep(1)
                    count+=1
                count = 1
                if NotifyFlag:
                    miningname = readConfig('mining','miningname','config.ini')
                    LineValue = readConfig('notify','tokenline','config.ini')
                    FacebookValue = readConfig('notify','tokenfacebook','config.ini')
                    FacebookIDValue = readConfig('notify','facebookID','config.ini')
                    process = subprocess.Popen(os.getcwd()+r'\GPU\nvidia-smi.exe --format=csv,noheader --query-gpu=gpu_name,utilization.gpu,utilization.memory,fan.speed,temperature.gpu', shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
                    GPUValue = str(process)
                    newValue = GPUValue.replace("%", "")
                    newValue = newValue.replace(" ", "")
                    Value = newValue.split(",")
                    hashrate = float(getHashRate())
                    msg = miningname+' LOAD: '+Value[1]+'% MEMORY: '+Value[2]+'%'+' FAN: '+Value[3]+'% TEMPERATURE: '+Value[4]+u'\u2103'+' ALGORITHM: '+getAlgorithm()+' HASHRATE: '+str(hashrate)+' kH/s'

                    if FacebookValue != "" and FacebookIDValue != "" and LineValue != "":
                        line(LineValue,msg)
                        facebook(FacebookValue,FacebookIDValue,msg)  
                    elif FacebookValue != "" and FacebookIDValue != "":
                        facebook(FacebookValue,FacebookIDValue,msg)
                    elif LineValue != "":
                        line(LineValue,msg)
                    else:
                        pass
                else:
                    pass
            else:
                time.sleep(1)

    def setDashboard(self):
        ip = self.textboxIPaddress.text()
        port = self.textboxPort.text()
        user = self.textboxuser.text()
        password = self.textboxPassword.text()
        dbname = self.textboxDBname.text()
        clientname = self.textboxClientname.text()
        if(ip!=''and port!=''and user!=''and password!=''and dbname!=''and clientname!=''):
            saveConfig('dashboard','ip',ip,'config.ini')
            saveConfig('dashboard','port',port,'config.ini')
            saveConfig('dashboard','username',user,'config.ini')
            saveConfig('dashboard','password',password,'config.ini')
            saveConfig('dashboard','databasename',dbname,'config.ini')
            saveConfig('dashboard','clientname',clientname,'config.ini')
        else:
            pass


    def sendToDB(self):
        while(True): 
            try:
                info = [readConfig('dashboard','ip','config.ini'),
                readConfig('dashboard','port','config.ini'),
                readConfig('dashboard','username','config.ini'),
                readConfig('dashboard','password','config.ini'),
                readConfig('dashboard','databasename','config.ini'),
                readConfig('dashboard','clientname','config.ini')]

                sendDataToDB(info[0],info[1],info[2],info[3],info[4],info[5])
                time.sleep(1)
            except Exception:
                info = [readConfig('dashboard','ip','config.ini'),
                readConfig('dashboard','port','config.ini'),
                readConfig('dashboard','username','config.ini'),
                readConfig('dashboard','password','config.ini'),
                readConfig('dashboard','databasename','config.ini'),
                readConfig('dashboard','clientname','config.ini')]
                time.sleep(1)

    def saveMiningConfig(self):
        wallet = self.textboxWallet.text()
        miningName = self.textboxMigingname.text()
        if(wallet!='' and miningName!=''):
            saveConfig('mining','wallet',wallet,'config.ini')
            saveConfig('mining','miningName',miningName,'config.ini')
        else:
            pass

    def startmining(self):
        # global benchmarkFlag
        # startBenchmarkFlag = Thread(target=benchmark)
        # startBenchmarkFlag.daemon = True
        # startBenchmarkFlag.start()
        # benchmarkFlag = True

        global MiningProcess,checkStart,GPUCheckFlag,miningFlag
        wallet = readConfig('mining','wallet','config.ini')
        if wallet!='':
            if checkStart==0:
                self.btnStart.setEnabled(False)
                self.textboxWallet.setEnabled(False)
                self.textboxMigingname.setEnabled(False)
                self.btnSaveMining.setEnabled(False)
                self.btnStart.setText("Start..")
                StartMining = Thread(target=switchAlgo, args=(wallet,))
                StartMining.daemon = True
                StartMining.start()
                StartStop = Thread(target=self.btnStartStop)
                StartStop.daemon = True
                StartStop.start()
                GPUCheck = Thread(target=self.GPUCheck, args=(wallet,))
                GPUCheck.daemon = True
                GPUCheck.start()
            elif checkStart==1:
                self.btnStart.setText("Start")
                self.textboxWallet.setEnabled(True)
                self.textboxMigingname.setEnabled(True)
                self.btnSaveMining.setEnabled(True)
                MiningProcess.kill()
                checkStart = 0
                GPUCheckFlag = False
                miningFlag = False
        else:
            print('wallet null')


    def btnStartStop(self):
        global checkStart,MiningProcess
        while(checkStart==0):
            pass
        self.btnStart.setEnabled(True)
        self.btnStart.setText("Stop")
        

    def setToStart(self):
        infoMining = [readConfig('mining','wallet','config.ini'),
        readConfig('mining','miningname','config.ini')]
        self.textboxWallet.setText(infoMining[0])
        self.textboxMigingname.setText(infoMining[1])
        
        time = readConfig('notify','notifytime','config.ini')
        if(time!=''):
            (time) = int(int(time)/60)
            self.textboxNotifyTime.setText(str(time))

        infodashboard = [readConfig('dashboard','ip','config.ini'),
                readConfig('dashboard','port','config.ini'),
                readConfig('dashboard','username','config.ini'),
                readConfig('dashboard','password','config.ini'),
                readConfig('dashboard','databasename','config.ini'),
                readConfig('dashboard','clientname','config.ini')]
        if(infodashboard!=''):
            self.textboxIPaddress.setText(infodashboard[0])
            self.textboxPort.setText(infodashboard[1])
            self.textboxuser.setText(infodashboard[2])
            self.textboxPassword.setText(infodashboard[3])
            self.textboxDBname.setText(infodashboard[4])
            self.textboxClientname.setText(infodashboard[5])


    def GPUCheck(self,wallet):
        global GPUCheckFlag,miningFlag,selectAlgo,MiningProcess,checkStart
        GPUCheckFlag = True
        LoadCount = 0
        FanCount = 0
        TemCount = 0
        timeToCheck = 900
        while(GPUCheckFlag):
                gpuload = readConfig('mining','gpuload','config.ini')
                gpufan = readConfig('mining','gpufan','config.ini')
                gputem = readConfig('mining','gputem','config.ini')
                count = 1
                process = subprocess.Popen(os.getcwd()+r'\GPU\nvidia-smi.exe --format=csv,noheader --query-gpu=gpu_name,utilization.gpu,utilization.memory,fan.speed,temperature.gpu', shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
                GPUValue = str(process)
                newValue = GPUValue.replace("%", "")
                newValue = newValue.replace(" ", "")
                Value = newValue.split(",")

                if gpuload!='' and gpufan!='' and gputem!='':
                    print("IF != null")
                    gpuload = int(gpuload)
                    gpufan = int(gpufan)
                    gputem = int(gputem)
                    while GPUCheckFlag and count<=timeToCheck:
                        time.sleep(1)
                        count+=1
                    if GPUCheckFlag:
                        print("IF notify TRUE")
                        if int(Value[1])<gpuload:
                                LoadCount+=1
                                if LoadCount>3:
                                    msg = '"GPU Load < '+gpuload+' %"'
                                    FacebookID = readConfig('notify','facebookID','config.ini')
                                    facebooktoken = readConfig('notify','tokenfacebook','config.ini')
                                    linetoken = readConfig('notify','tokenline','config.ini')
                                    line(linetoken,msg)
                                    facebook(facebooktoken,FacebookID,msg)
                                    saveConfig('blacklist',selectAlgo,'1','blacklist.txt')
                                    if miningFlag:
                                        switchAlgo(wallet)
                                    LoadCount=0
                        else:
                                LoadCount=0

                        if int(Value[3])>gpufan:
                                FanCount+=1
                                if FanCount>3:
                                    msg = 'GPU FAN use > '+gpufan+' % Stop mining now'
                                    FacebookID = readConfig('notify','facebookID','config.ini')
                                    facebooktoken = readConfig('notify','tokenfacebook','config.ini')
                                    linetoken = readConfig('notify','tokenline','config.ini')
                                    line(linetoken,msg)
                                    facebook(facebooktoken,FacebookID,msg)
                                    if miningFlag:
                                        self.btnStart.setText("Start")
                                        self.textboxWallet.setEnabled(True)
                                        self.textboxMigingname.setEnabled(True)
                                        self.btnSaveMining.setEnabled(True)
                                        MiningProcess.kill()
                                        checkStart = 0
                                        GPUCheckFlag = False
                                        miningFlag = False
                                    FanCount=0
                        else:
                                FanCount=0

                        if int(Value[4])>gputem:
                                TemCount+=1
                                if TemCount>3:
                                    msg = 'GPU Temperature > '+gputem+' '+u'\u2103'+' Stop mining now'
                                    FacebookID = readConfig('notify','facebookID','config.ini')
                                    facebooktoken = readConfig('notify','tokenfacebook','config.ini')
                                    linetoken = readConfig('notify','tokenline','config.ini')
                                    line(linetoken,msg)
                                    facebook(facebooktoken,FacebookID,msg)
                                    if miningFlag:
                                        self.btnStart.setText("Start")
                                        self.textboxWallet.setEnabled(True)
                                        self.textboxMigingname.setEnabled(True)
                                        self.btnSaveMining.setEnabled(True)
                                        MiningProcess.kill()
                                        checkStart = 0
                                        GPUCheckFlag = False
                                        miningFlag = False
                                    TemCount=0 
                        else:
                                TemCount=0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = App()
    main.show()
    sys.exit(app.exec_())