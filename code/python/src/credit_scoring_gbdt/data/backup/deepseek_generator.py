import json
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("ru_RU")

# Реальные коды с описанием
REAL_OKVED_CODES = [
    ("46.51", "Торговля оптовая компьютерами, периферийными устройствами к компьютерам и программным обеспечением"),
    ("46.49.33", "Торговля оптовая писчебумажными и канцелярскими товарами"),
    ("45.20.2", "Техническое обслуживание и ремонт прочих автотранспортных средств"),
    ("47.11", "Торговля розничная преимущественно пищевыми продуктами, включая напитки, и табачными изделиями в неспециализированных магазинах"),
    ("62.02", "Деятельность консультативная и работы в области компьютерных технологий"),
    ("43.21", "Производство электромонтажных работ"),
    ("47.19", "Торговля розничная прочая в неспециализированных магазинах"),
    ("49.41", "Деятельность автомобильного грузового транспорта"),
    ("68.20.2", "Аренда и управление собственным или арендованным нежилым недвижимым имуществом"),
    ("56.10", "Деятельность ресторанов и услуги по доставке продуктов питания")
]

# Генерация дополнительных кодов с фиктивными описаниями
def generate_fake_okved_codes(count=490):
    codes = set(code for code, _ in REAL_OKVED_CODES)
    while len(codes) < 500:
        code = f"{random.randint(10, 99)}.{random.randint(10, 99)}"
        if code not in codes:
            codes.add(code)
    extra = list(codes - set(code for code, _ in REAL_OKVED_CODES))
    return [(code, f"Описание для ОКВЭД {code}") for code in extra]

OKVED_CODES = REAL_OKVED_CODES + generate_fake_okved_codes()

EXTRA_OKVEDS = list(set(code for code, _ in OKVED_CODES)) + [
    "18.12", "33.12", "33.14", "33.20", "46.18", "46.19", "46.39", "46.43.2",
    "46.43.3", "46.44.1", "46.44.2", "46.49", "46.65", "46.66", "46.69",
    "46.90", "47.30", "47.59.1", "47.62.2", "47.63.1", "47.63.2", "47.73",
    "47.74", "47.75", "47.75.2", "47.78.1", "47.78.9", "52.10", "52.29",
    "53.10.2", "62.01", "62.09", "63.11.1", "68.20", "77.39.23", "78.30",
    "82.99", "95.11", "95.12"
]

REGIONS = [
    "г. Москва", "г. Санкт-Петербург", "обл. Московская", "обл. Ленинградская",
    "обл. Нижегородская", "респ. Татарстан", "обл. Свердловская", "край Краснодарский",
    "обл. Ростовская", "обл. Самарская", "обл. Челябинская", "обл. Новосибирская",
    "респ. Башкортостан", "край Пермский", "обл. Воронежская", "обл. Иркутская"
]

STATUSES = ["Действующее", "Ликвидировано", "В процессе ликвидации", "В процессе банкротства"]

def generate_inn():
    return str(random.randint(1000000000, 9999999999))

def generate_kpp():
    return str(random.randint(100000000, 999999999))

def generate_ogrn():
    return str(random.randint(1000000000000, 9999999999999))

def generate_ogrn_date(start_year):
    start = datetime(start_year, 1, 1)
    end = datetime.today()
    random_date = start + timedelta(days=random.randint(0, (end - start).days))
    return random_date.strftime("%Y-%m-%d")

def generate_address():
    region = random.choice(REGIONS)
    return f"{region}, г. {fake.city()}, ул. {fake.street_name()}, д.{random.randint(1, 200)}"

def generate_financial_history(start_year):
    history = []
    for year in range(start_year, datetime.now().year + 1):
        income = random.randint(500_000, 50_000_000)
        expense = income * random.uniform(0.7, 0.98)
        taxes = {
            "usn": income * 0.06 if random.random() < 0.5 else 0.0,
            "pension": income * 0.022,
            "medical": income * 0.005,
            "social": income * 0.004,
            "penalty": income * 0.001 if random.random() < 0.1 else 0.0,
            "other": income * 0.003
        }
        history.append({
            "year": str(year),
            "income": round(income, 2),
            "expense": round(expense, 2),
            "profitability": round((income - expense) / income, 3),
            "tax_burden": round(sum(taxes.values()) / income, 5),
            "taxes": {k: round(v, 2) for k, v in taxes.items()}
        })
    return history

def generate_company():
    foundation_year = random.randint(2000, datetime.now().year - 1)
    ogrn_date = generate_ogrn_date(foundation_year)
    capital = random.randint(10_000, 1_000_000)
    founders = [{
        "full_name": fake.name(),
        "innfl": generate_inn(),
        "share": capital,
        "percent": 100.0
    }]
    main_okved_code, main_okved_text = random.choice(OKVED_CODES)
    return {
        "inn": generate_inn(),
        "kpp": generate_kpp(),
        "ogrn": generate_ogrn(),
        "ogrn_date": ogrn_date,
        "status": random.choice(STATUSES),
        "foundation_year": foundation_year,
        "capital": capital,
        "main_okved": main_okved_code,
        "main_okved_text": main_okved_text,
        "extra_okved": random.sample(EXTRA_OKVEDS, k=random.randint(1, 5)),
        "address": generate_address(),
        "fias_address": None,
        "ceo": {
            "full_name": fake.name(),
            "innfl": generate_inn(),
            "appointed_at": ogrn_date
        },
        "founders": founders,
        "employee_count": random.randint(1, 200),
        "income": 0.0,
        "expense": 0.0,
        "profitability": 0.0,
        "tax_burden": 0.0,
        "contacts": {
            "phones": [fake.phone_number() for _ in range(random.randint(1, 3))],
            "emails": [fake.email() for _ in range(random.randint(1, 2))]
        },
        "taxes": {
            "profit_tax": None,
            "vat": None,
            "penalty": None
        },
        "debts": {
            "arrears": round(random.uniform(0, 100_000), 2),
            "penalty": round(random.uniform(0, 10_000), 2),
            "fine": round(random.uniform(0, 50_000), 2)
        },
        "history": {
            "ceo_changes": [],
            "capital_changes": [],
            "address_changes": []
        },
        "financial_history": generate_financial_history(foundation_year),
        "licenses": [],
        "branches": []
    }

companies = [generate_company() for _ in range(1000)]

with open("companies_final.json", "w", encoding="utf-8") as f:
    for company in companies:
        json.dump(company, f, ensure_ascii=False)
        f.write("\n")

print("✔️ companies_final.json сгенерирован и сохранён")
