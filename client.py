import requests


HOST = 'http://127.0.0.1:5000'


data = requests.post(f'{HOST}/ads/',
                     json={
                        'header': 'prodam',
                        'description': 'bystro',
                         'owner': 'ivan'
                     })

# print(data.json())
data1 = requests.get(f'{HOST}/ads/1')
print(data1.json())
data2 = requests.delete(f'{HOST}/ads/1')
# print(data2.json())