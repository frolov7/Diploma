import requests
import joblib
import pandas as pd
import numpy as np
import json
import os
import logging

MODEL = joblib.load("../../data/models/credit_model.pkl")
API_KEY = "81e3084576e0c56abedb912342c81f914fe1b350"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/credit_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("credit_bot")

def fetch_company_data(inn: str) -> dict | None:
    url = "https://api-fns.ru/api/egr"
    params = {"req": inn, "key": API_KEY}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        item = r.json().get("items", [])[0].get("ЮЛ", {})
        latest = item.get("ОткрСведения", {})
        if isinstance(latest, list):
            latest = sorted(latest, key=lambda x: x.get("Дата", ""), reverse=True)[0]
        return {
            "inn": item.get("ИНН"),
            "foundation_year": int(item.get("ДатаОГРН", "")[:4] or 2000),
            "status": item.get("Статус") or "Неизвестен",
            "capital": float(item.get("Капитал", {}).get("СумКап", 0) or 0),
            "main_okved": item.get("ОснВидДеят", {}).get("Код", "00.00"),
            "employee_count": int(latest.get("КолРаб", 0) or 0),
            "latest_income": float(latest.get("СумДоход", 0) or 0),
            "latest_profitability": float(latest.get("ОтраслевыеПок", {}).get("Рентабельность", 0) or 0),
            "total_debt": sum([
                float(latest.get("СумНедНалог", 0) or 0),
                float(latest.get("СумПени", 0) or 0),
                float(latest.get("СумШтраф", 0) or 0),
            ])
        }
    except requests.exceptions.HTTPError as e:
        logging.error(f"[API ERROR] HTTP {r.status_code}: {r.text}")
        return None
    except Exception as e:
        logging.exception(f"[FETCH FAIL] Unexpected error for INN {inn}")
        return None


def predict_from_dict(d: dict) -> int:
    drop = ["inn", "main_okved", "status"]
    df = pd.DataFrame([d])
    df = df.drop(columns=[col for col in drop if col in df], errors="ignore")
    df = df.fillna(0)
    return int(MODEL.predict(df)[0])

def extract_latest_financial(company_data: dict) -> dict:
    history = company_data.get("financial_history", [])
    if not history:
        return {}

    latest = max(history, key=lambda x: int(x.get("year", 0)))
    return {
        "year": int(latest.get("year", 0)),
        "income": float(latest.get("income", 0)),
        "expense": float(latest.get("expense", 0)),
        "profit": float(latest.get("income", 0)) - float(latest.get("expense", 0)),
        "profitability": float(latest.get("profitability", 0) or 0),
        "tax_burden": float(latest.get("tax_burden", 0) or 0)
    }


def explain_prediction(company_data: dict, prediction: int) -> str:
    fin = extract_latest_financial(company_data)
    reasons = []

    years = 2025 - int(company_data.get("foundation_year", 2020))
    profit = fin.get("profit", 0)
    revenue = fin.get("income", 0)
    employees = int(company_data.get("employee_count", 0))

    if prediction == 0:
        if years < 2:
            reasons.append("Компания зарегистрирована менее 2 лет назад.")
        if profit < 0:
            reasons.append("Финансовый результат отрицательный (убыток).")
        if revenue < 1_000_000:
            reasons.append("Недостаточный годовой доход.")
        if employees <= 3:
            reasons.append("Малый штат сотрудников.")
        return "Причина отказа:\n• " + "\n• ".join(reasons) if reasons else "Недостаточная информация."

    else:
        if profit > 0:
            reasons.append("Финансовый результат положительный.")
        if revenue > 5_000_000:
            reasons.append("Высокий годовой доход.")
        if years >= 3:
            reasons.append("Компания работает более 3 лет.")
        if employees >= 5:
            reasons.append("Средний или крупный штат сотрудников.")
        return "Положительные факторы:\n• " + "\n• ".join(reasons) if reasons else "Общие показатели в норме."

def load_filtered_json(inn: str) -> dict | None:
    path = os.path.abspath(f"../../data/filtered/{inn}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)