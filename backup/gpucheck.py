import subprocess
import os
import requests
import time

def line(linetoken,msg):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'content-type':'application/x-www-form-urlencoded','Authorization':'Bearer '+linetoken}
    #msg = 'LINE Notify Eiei'
    result = requests.post(url, headers=headers, data = {'message':msg})
    return(result.status_code)


def readfile(filename):
    try:
        file = open(filename,"r")
        data = file.readline()
        file.close()
        return data
    except IOError:
        return ''


def GPUCheck():
        LoadCount = 0
        FanCount = 0
        TemCount = 0
        while(True):
                process = subprocess.Popen(os.getcwd()+r'\GPU\nvidia-smi.exe --format=csv,noheader --query-gpu=gpu_name,utilization.gpu,utilization.memory,fan.speed,temperature.gpu', shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()
                GPUValue = str(process)
                newValue = GPUValue.replace("%", "")
                newValue = newValue.replace(" ", "")
                Value = newValue.split(",")

                print("0 : "+Value[0])
                print("1 : "+Value[1])
                print("2 : "+Value[2])
                print("3 : "+Value[3])
                print("4 : "+Value[4])

                time.sleep(900)


                if int(Value[1])<40:
                        LoadCount+=1
                        if LoadCount>=3:
                                token = readfile(r'notify\LineToken')
                                line(token,"GPU Load < 40 %")
                                LoadCount=0
                else:
                        LoadCount=0
                        print("reset LoadCount = 0 ")

                if int(Value[3])>90:
                        FanCount+=1
                        if FanCount>=3:
                                token = readfile(r'notify\LineToken')
                                line(token,"GPU FAN > 90 %")
                                FanCount=0
                else:
                        FanCount=0
                        print("reset FanCount = 0 ")

                if int(Value[4])>90:
                        TemCount+=1
                        if TemCount>=3:
                                token = readfile(r'notify\LineToken')
                                line(token,"GPU Tem > 90 C")
                                TemCount=0 
                else:
                        TemCount=0
                        print("reset TemCount = 0 ")
                                

GPUCheck()