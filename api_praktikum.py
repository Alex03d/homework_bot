import requests

url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': 'OAuth y0_AgAAAAAJvI3SAAYckQAAAADTrQmhyh8tnQ1TQ8aZXZrLSzHFXn0NBQQ'}
payload = {'from_date': 1668166413-86400*30}

homework_statuses = requests.get(url, headers=headers, params=payload)
print(homework_statuses.text)
print(homework_statuses.json())
