from sklearn.metrics import (
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score
)


def evaluate_model(model, X_test, y_test, threshold=0.3):
    y_proba = model.predict_proba(X_test)[:, 1]
    y_pred = (y_proba > threshold).astype(int)

    metrics = {
        'ROC-AUC': roc_auc_score(y_test, y_proba),
        'Precision': precision_score(y_test, y_pred, zero_division=0),
        'Recall': recall_score(y_test, y_pred),
        'F1-score': f1_score(y_test, y_pred)
    }

    return metrics