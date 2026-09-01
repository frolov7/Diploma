import joblib

from sklearn.model_selection import RandomizedSearchCV
from lightgbm import LGBMClassifier


def train_lightgbm_model(X_train, y_train, feature_columns):
    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

    base_model = LGBMClassifier(
        scale_pos_weight=scale_pos_weight,
        random_state=42,
        n_jobs=-1,
        force_col_wise=True
    )

    param_grid = {
        'n_estimators': [300, 500, 700],
        'learning_rate': [0.01, 0.03, 0.05],
        'num_leaves': [31, 50, 70],
        'max_depth': [6, 8],
        'min_child_samples': [50, 100]
    }

    search = RandomizedSearchCV(
        estimator=base_model,
        param_distributions=param_grid,
        n_iter=15,
        scoring='roc_auc',
        cv=3,
        random_state=42,
        n_jobs=-1
    )

    search.fit(X_train, y_train)

    model = search.best_estimator_

    joblib.dump(model, 'model.pkl')
    joblib.dump(feature_columns, 'columns.pkl')

    return model