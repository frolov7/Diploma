import pandas as pd

from sklearn.model_selection import train_test_split


def prepare_train_test_data(dataset_path):
    df = pd.read_csv(dataset_path)

    y = df['TARGET']
    X = df.drop(columns=['TARGET', 'SK_ID_CURR'])

    X = pd.get_dummies(X)
    X.columns = X.columns.str.replace(' ', '_')

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    return X_train, X_test, y_train, y_test, X.columns