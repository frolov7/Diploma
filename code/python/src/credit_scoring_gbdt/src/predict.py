import json
import pandas as pd
import joblib

def predict(model_path, data_path):
    # Загружаем модель
    model = joblib.load(model_path)

    # Загружаем данные
    with open(data_path, "r", encoding="utf-8") as f:
        records = [json.loads(line) for line in f]

    df = pd.DataFrame(records)

    # ❗ Удаляем ненужные признаки
    drop_cols = ["inn", "main_okved", "status", "creditworthy"]
    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

    # ❗ Заполняем пропуски
    df = df.fillna(0)

    # Предсказания
    predictions = model.predict(df)
    df["prediction"] = predictions

    # Сохраняем результат
    df.to_json("data/processed/predictions.jsonl", orient="records", lines=True, force_ascii=False)
    print("✅ Предсказания сохранены в data/processed/predictions.jsonl")

if __name__ == "__main__":
    predict("data/models/credit_model.pkl", "data/processed/credit_data.jsonl")
