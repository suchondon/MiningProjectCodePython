import socket
import time
import requests




def getAlgorithm():
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
                algo = msg[3].split('=')
                return algo[1]
        except socket.error:
                return ''

print(getAlgorithm())