import pandas as pd
import json
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import classification_report
import joblib

# Загрузка данных
with open("data/processed/credit_data.jsonl", "r", encoding="utf-8") as f:
    records = [json.loads(line) for line in f]

df = pd.DataFrame(records)

# 🧼 Удалим текстовые / нечисловые признаки
df.drop(columns=["inn", "main_okved", "status"], inplace=True)

# 🧼 Заполним NaN нулями
df = df.fillna(0)

# Разделим на X / y
X = df.drop(columns=["creditworthy"])
y = df["creditworthy"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Обучение модели
model = GradientBoostingClassifier()
model.fit(X_train, y_train)

# Сохраняем
joblib.dump(model, "data/models/credit_model.pkl")

# Оценка
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred))
