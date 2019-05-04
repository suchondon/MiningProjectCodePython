import socket
import time
import requests




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

print(getHashRate())


# import requests
# import http.client

# test = ""
# try:
#     url = http.client.HTTPConnection('127.0.0.1',4068)
#     url.request('GET', '/summary')
#     response = url.getresponse()
# except http.client.HTTPException as e:
#     test = e

# print(test) 
# test = str(test)
# value = test.split(";")

# for data in value:
#     print(data)



