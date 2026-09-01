import requests
import json

INN = "7716564434"
API_KEY = "81e3084576e2c56abedb912342c81f914fe1b350"

def fetch_and_filter_company_data(inn: str, api_key: str):
    url = "https://api-fns.ru/api/egr"
    params = {"req": inn, "key": api_key}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Ошибка {response.status_code}: {response.text}")
        return

    data = response.json()
    item = data.get("items", [])[0].get("ЮЛ", {})

    def extract_financial_history():
        raw_list = item.get("История", {}).get("ОткрСведения", [])
        if isinstance(raw_list, dict):
            raw_list = [raw_list]

        by_year = {}

        for entry in raw_list:
            date = entry.get("Дата")
            if not date:
                continue

            year = date[:4]
            if year == "2025":
                continue

            income = float(entry.get("СумДоход", 0) or 0)
            expense = float(entry.get("СумРасход", 0) or 0)
            profitability = float(entry.get("ОтраслевыеПок", {}).get("Рентабельность") or 0)
            tax_burden = float(entry.get("ОтраслевыеПок", {}).get("НалогНагрузка") or 0)

            taxes_raw = entry.get("Налоги", [])
            tax_map = {
                "usn": 0.0,
                "pension": 0.0,
                "medical": 0.0,
                "social": 0.0,
                "penalty": 0.0,
                "other": 0.0
            }

            for tax in taxes_raw:
                name = tax.get("НаимНалог", "").lower()
                amount = float(tax.get("СумУплНал", 0) or 0)
                if "упрощенной системы" in name:
                    tax_map["usn"] += amount
                elif "пенсионное" in name:
                    tax_map["pension"] += amount
                elif "медицинское" in name:
                    tax_map["medical"] += amount
                elif "социальное страхование" in name:
                    tax_map["social"] += amount
                elif "пене" in name:
                    tax_map["penalty"] += amount
                else:
                    tax_map["other"] += amount

            score = income + expense + profitability + tax_burden + sum(tax_map.values())
            if score == 0:
                continue

            existing = by_year.get(year)
            if not existing or score > sum(existing.values()):
                by_year[year] = {
                    "year": year,
                    "income": income if income > 0 else None,
                    "expense": expense if expense > 0 else None,
                    "profitability": profitability if profitability > 0 else None,
                    "tax_burden": tax_burden if tax_burden > 0 else None,
                    "taxes": tax_map
                }

        return sorted(by_year.values(), key=lambda x: x["year"], reverse=True)

    def extract_tax_debts():
        result = {"arrears": 0.0, "penalty": 0.0, "fine": 0.0}
        raw_list = item.get("История", {}).get("ОткрСведения", [])
        if isinstance(raw_list, dict):
            raw_list = [raw_list]

        for entry in raw_list:
            for tax in entry.get("Налоги", []):
                result["arrears"] += float(tax.get("СумНедНалог", 0) or 0)
                result["penalty"] += float(tax.get("СумПени", 0) or 0)
                result["fine"] += float(tax.get("СумШтраф", 0) or 0)

        return result if any(result.values()) else None

    def get_latest_entry():
        data = item.get("ОткрСведения", {})
        if isinstance(data, list):
            data = sorted(data, key=lambda x: x.get("Дата", ""), reverse=True)[0]
        return data

    latest = get_latest_entry()

    filtered = {
        "inn": item.get("ИНН"),
        "kpp": item.get("КПП"),
        "ogrn": item.get("ОГРН"),
        "ogrn_date": item.get("ДатаОГРН"),
        "status": item.get("Статус"),
        "foundation_year": item.get("ДатаОГРН", "")[:4],
        "capital": float(item.get("Капитал", {}).get("СумКап", 0)),

        "main_okved": item.get("ОснВидДеят", {}).get("Код"),
        "main_okved_text": item.get("ОснВидДеят", {}).get("Текст"),
        "extra_okved": [v.get("Код") for v in item.get("ДопВидДеят", [])],

        "address": item.get("Адрес", {}).get("АдресПолн"),
        "fias_address": item.get("Адрес", {}).get("АдресПолнФИАС"),

        "ceo": {
            "full_name": item.get("Руководитель", {}).get("ФИОПолн"),
            "innfl": item.get("Руководитель", {}).get("ИННФЛ"),
            "appointed_at": item.get("Руководитель", {}).get("Дата"),
        },

        "founders": [
            {
                "full_name": u["УчрФЛ"].get("ФИОПолн"),
                "innfl": u["УчрФЛ"].get("ИННФЛ"),
                "share": float(u.get("СуммаУК", 0)),
                "percent": float(u.get("Процент", 0))
            } for u in item.get("Учредители", []) if u.get("УчрФЛ")
        ],

        "employee_count": int(latest.get("КолРаб", 0)),
        "income": float(latest.get("СумДоход", 0) or 0),
        "expense": float(latest.get("СумРасход", 0) or 0),
        "profitability": float(latest.get("ОтраслевыеПок", {}).get("Рентабельность", 0) or 0),
        "tax_burden": float(latest.get("ОтраслевыеПок", {}).get("НалогНагрузка", 0) or 0),

        "contacts": {
            "phones": item.get("Контакты", {}).get("Телефон", []),
            "emails": item.get("Контакты", {}).get("e-mail", [])
        },

        "taxes": {
            "profit_tax": next((float(n.get("СумУплНал", 0)) for n in latest.get("Налоги", []) if "прибыль" in n.get("НаимНалог", "").lower()), None),
            "vat": next((float(n.get("СумУплНал", 0)) for n in latest.get("Налоги", []) if "добавленную стоимость" in n.get("НаимНалог", "").lower()), None),
            "penalty": next((float(n.get("СумУплНал", 0)) for n in latest.get("Налоги", []) if "пене" in n.get("НаимНалог", "").lower()), None),
        },

        "debts": extract_tax_debts(),

        "history": {
            "ceo_changes": list(item.get("История", {}).get("Руководитель", {}).keys()) if item.get("История", {}).get("Руководитель") else [],
            "capital_changes": list(item.get("История", {}).get("Капитал", {}).keys()) if item.get("История", {}).get("Капитал") else [],
            "address_changes": list(item.get("История", {}).get("Адрес", {}).values()) if item.get("История", {}).get("Адрес") else [],
        },

        "financial_history": extract_financial_history(),

        "licenses": [
            {
                "activity": l.get("ВидДеятельности"),
                "valid_until": l.get("СрокДействия")
            } for l in item.get("Лицензии", []) if isinstance(l, dict)
        ],

        "branches": item.get("Филиалы", [])
    }

    filename = f"{inn}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False, indent=4)

    print(f"🎉 Saved company data to {filename}")

# 🚀 Run
fetch_and_filter_company_data(INN, API_KEY)
