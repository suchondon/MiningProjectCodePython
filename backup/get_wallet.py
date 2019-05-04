import requests
from decimal import Decimal

x = requests.get(url='https://www.zpool.ca/api/'+
'wallet?address=3PmdKfoVPU4ZG9PsmKMMdqJmDPhXJMwfgn')
data  = x.json()
d = Decimal(data['unsold'])
print(format(d, 'f'))

# d = data['unsold']
# print(d)


