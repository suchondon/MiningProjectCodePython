import requests

#https://www.zpool.ca/api/wallet?address=18ZuJ4BnhPaH8cjeu5L3HF5sVgRBQdD8TR

x = requests.get(url='https://www.zpool.ca/json/algo_profitability.json')
data  = x.json()
profit = 0.0
selectAlgo = ""
algo = ['allium','bitcore','blake2s','c11','groestl','hmq1725','keccakc',
        'lbry','lyra2v2','lyra2v3','lyra2z','myr-gr','neoscrypt','nist5',
        'phi2','polytimos','quark','qubit','scrypt','sha256t','sib',
        'skein','skunk','sonoa','timetravel','tribus','x11','x13','x14',
        'x16r','x16s','x17']
for i in algo:
    data[i].reverse()
    if float(data[i][0][1])>profit:
        profit=float(data[i][0][1])
        selectAlgo = i


# x = requests.get(url='https://www.zpool.ca/api/currencies')
# data  = x.json()
# algo = ["allium","bcd","sib"]
# avg = []

# for j in algo:
#     for i in data:
#         if data[i]['algo']==j:
#             avg[j] = avg[j]+float(data[i]['24h_btc'])
        


# print("json key: ", i)
#         print("json algo: ", data[i]['algo'])
#         print("json 24h_btc: ", data[i]['24h_btc'])
