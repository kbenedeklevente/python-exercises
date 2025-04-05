import requests
response = requests.get('http://localhost:8000/api/weather/Sydney')
data = response.json()
print(data)