import json

def label_creditworthiness(company):
    latest = company["financial_history"][-1] if company["financial_history"] else None
    debts = company.get("debts") or {}
    arrears = debts.get("arrears", 0.0)
    fine = debts.get("fine", 0.0)
    penalty = debts.get("penalty", 0.0)
    total_debt = arrears + fine + penalty

    if not latest:
        return 0

    profitability = latest.get("profitability", 0.0)
    if profitability is None:
        profitability = 0.0

    if profitability < 0.05 or total_debt > 100_000:
        return 0
    return 1


def extract_features(company):
    latest = company["financial_history"][-1] if company["financial_history"] else {}
    debts = company.get("debts") or {}
    arrears = debts.get("arrears", 0.0)
    fine = debts.get("fine", 0.0)
    penalty = debts.get("penalty", 0.0)

    return {
        "inn": company["inn"],
        "foundation_year": company["foundation_year"],
        "status": company["status"],
        "capital": company["capital"],
        "main_okved": company["main_okved"],
        "employee_count": company.get("employee_count", 0),
        "latest_income": latest.get("income", 0.0),
        "latest_profitability": latest.get("profitability", 0.0),
        "total_debt": arrears + fine + penalty,
        "creditworthy": label_creditworthiness(company)
    }

input_path = "data/raw/companies.jsonl"
output_path = "data/processed/credit_data.jsonl"

with open(input_path, "r", encoding="utf-8") as fin, open(output_path, "w", encoding="utf-8") as fout:
    for line in fin:
        company = json.loads(line)
        features = extract_features(company)
        fout.write(json.dumps(features, ensure_ascii=False) + "\n")

print("✅ Разметка завершена: credit_data.jsonl готов.")
