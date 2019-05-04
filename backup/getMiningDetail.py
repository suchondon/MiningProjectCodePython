import requests

x = requests.get(url='https://www.zpool.ca/api/status')
data  = x.json()
algo = ['allium','argon2d-dyn','astralhash','bcd','binarium-v1','bitcore','blake2s','c11','equihash','globalhash','groestl','hex','hmq1725','jeonghash','keccakc','lbry','lyra2v2','lyra2v3','lyra2z','m7m','myr-gr','neoscrypt','nist5','padihash','pawelhash','phi','phi2','polytimos','quark','qubit','rainforest','scrypt','scrypt-ld','sha256','sha256t','sib','skein','skunk','sonoa','timetravel','tribus','x11','x13','x14','x16r','x16rt','x16s','x17','x21s','x22i','xevan','yescrypt','yescryptR16','yescryptR8','yespower']
for i in algo:
    print(i,data[i]['port'])