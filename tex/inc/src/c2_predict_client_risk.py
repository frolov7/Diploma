import pandas as pd


def predict_client_risk(model, input_df, columns):
    input_df = pd.get_dummies(input_df)
    input_df = input_df.reindex(columns=columns, fill_value=0)

    probability_default = model.predict_proba(input_df)[0][1]
    score = (1 - probability_default) * 1000

    if probability_default < 0.3:
        risk_level = 'Low'
    elif probability_default < 0.6:
        risk_level = 'Medium'
    else:
        risk_level = 'High'

    result = {
        'probability_default': float(probability_default),
        'score': float(score),
        'risk_level': risk_level,
        'decision': int(probability_default >= 0.5)
    }

    return result