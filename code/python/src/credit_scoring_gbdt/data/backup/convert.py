import pandas as pd
import json

# Пути к файлам
xlsx_path = "companies_full.xlsx"
jsonl_path = "companies_restored.jsonl"

# Загружаем Excel
df = pd.read_excel(xlsx_path)

# Преобразуем каждую строку обратно в словарь
with open(jsonl_path, "w", encoding="utf-8") as f:
    for _, row in df.iterrows():
        obj = {}
        for col, val in row.items():
            # Преобразуем ключи с точками в иерархические словари
            if pd.isna(val):
                continue
            parts = col.split(".")
            current = obj
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            try:
                if isinstance(val, str) and val.strip().startswith("[") and val.strip().endswith("]"):
                    val = json.loads(val)
            except:
                pass
            current[parts[-1]] = val

        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

print(f"✅ Восстановлен JSONL: {jsonl_path}")
