import requests
import json

# Указываем API URL
url = "https://api-fns.ru/api/egr"

# Параметры запроса
params = {
    "req": "7730269423",  # ИНН компании
    "key": "49a1d12840b39e016611e594a6f761ae4b4f96c7"  # API-ключ
}

# Выполняем GET-запрос
response = requests.get(url, params=params)

# Проверяем статус ответа
if response.status_code == 200:
    data = response.json()  # Преобразуем ответ в JSON
    
    # Сохраняем данные в JSON-файл
    with open("ООО КОМАКС.json", "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)
    
    print("Данные успешно сохранены в ООО КОМАКС.json")
else:
    print(f"Ошибка {response.status_code}: {response.text}")