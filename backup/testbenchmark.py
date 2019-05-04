import requests
import configparser
import subprocess
import os
import time
import socket
import signal

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
def getHashRate():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = '127.0.0.1'
        port = 4068
        s.connect((host, port))
        s.send("summary".encode())
        msg = str(s.recv(4096))         #msg = msg.replace('|\\x00','')
        msg = msg.split(';')
        s.close()
        time.sleep(1)
        hashrate = msg[5].split('=')
        return hashrate[1]
    except socket.error:
        return '0'


def benchmark():
    count = 1
    global benchmarkFlag 
    benchmarkFlag = True
    getFromPool = requests.get(url='https://www.zpool.ca/api/status')
    data  = getFromPool.json()
    #['allium','argon2d-dyn','astralhash','bcd','binarium-v1','bitcore','blake2s','c11','equihash','globalhash','groestl','hex','hmq1725','jeonghash','keccakc','lbry','lyra2v2','lyra2v3','lyra2z','m7m','myr-gr','neoscrypt','nist5','padihash','pawelhash','phi','phi2','polytimos','quark','qubit','rainforest','scrypt','scrypt-ld','sha256','sha256t','sib','skein','skunk','sonoa','timetravel','tribus','x11','x13','x14','x16r','x16rt','x16s','x17','x21s','x22i','xevan','yescrypt','yescryptR16','yescryptR8','yespower']
    algo = ['allium','bitcore','blake2s','c11','equihash','groestl','hmq1725','keccakc','lbry','lyra2v2','lyra2v3','lyra2z',
        'myr-gr','neoscrypt','nist5','phi2','polytimos','quark','qubit','scrypt','sha256','sha256t','sib',
        'skein','skunk','sonoa','timetravel','tribus','x11','x13','x14','x16r','x16s','x17']
    for i in algo:
        MiningProcess = subprocess.Popen(os.getcwd()+r'\miner\ccminer\ccminer-x64.exe -b 4068 -a '+i+' -o stratum+tcp://'+i+'.mine.zpool.ca:'+str(data[i]['port'])+' -u 3PmdKfoVPU4ZG9PsmKMMdqJmDPhXJMwfgn -p ID=Test01,c=BTC',shell=False,creationflags=subprocess.CREATE_NEW_CONSOLE)
        while(benchmarkFlag==True and count<=300):
            time.sleep(1)
            count+=1
        count = 1
        hashrate = float(getHashRate())
        if(benchmarkFlag==True):
            saveConfig('algorithm',i,str(hashrate),'benchmark')
        while(benchmarkFlag==True and count<=60):
            time.sleep(1)
            count+=1
        count = 1
        hashrate2 = float(getHashRate())
        if(hashrate2>hashrate):
            if(benchmarkFlag==True):
                saveConfig('algorithm',i,str(hashrate),'benchmark')
        time.sleep(1)
        MiningProcess.kill()
        if(benchmarkFlag==False):
            break
        benchmarkFlag = False

benchmark()