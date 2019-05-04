import sys
import subprocess
import os
import time
import atexit
import signal
import requests
import re
from influxdb import InfluxDBClient
from datetime import datetime
def sendInfoToDB():
        host = '35.247.130.80'
        port = '8086'
        user = 'Data'
        password = 'GetData'
        dbname = 'GPU'
        

        #client.create_database(dbname)
        while(True):
            process = subprocess.Popen(os.getcwd()+r'\GPU\nvidia-smi.exe --format=csv,noheader --query-gpu=gpu_name,utilization.gpu,utilization.memory,fan.speed,temperature.gpu', shell=True, stdout=subprocess.PIPE).communicate()[0].decode('utf-8').strip()

            time.sleep(1)
            GPUValue = str(process)

            #แทนที่ได้ทีละตัว หาวิธีแทนที่พร้อมกันได้หลายตัว??
            newValue = GPUValue.replace("%", "")
            newValue = newValue.replace(" ", "")
            Value = newValue.split(",")

            #print(datetime.utcnow())

            json_body = [
                    {
                        "measurement": "GPU_Load", #ชื่อเครื่อง
                        "time": datetime.utcnow(), #เวลา
                        "fields": { #ค่าต่่างๆ
                            "load": Value[1],
                            "memory": Value[2],
                            "fan": Value[3],
                            "tem": Value[4]
                    }
                }
            ]

            client = InfluxDBClient(host, port, user, password, dbname)

            client.write_points(json_body)

            result = client.query('select load,memory,fan,tem from GPU_Load;')

            print("Result: {0}".format(result))




sendInfoToDB()