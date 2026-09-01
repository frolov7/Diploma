import numpy as np


def add_engineered_features(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)

    df['CREDIT_TO_INCOME'] = df['AMT_CREDIT'] / (df['AMT_INCOME_TOTAL'] + 1)
    df['ANNUITY_TO_INCOME'] = df['AMT_ANNUITY'] / (df['AMT_INCOME_TOTAL'] + 1)
    df['GOODS_TO_CREDIT'] = df['AMT_GOODS_PRICE'] / (df['AMT_CREDIT'] + 1)

    df['AGE_YEARS'] = -df['DAYS_BIRTH'] / 365
    df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace(365243, 0)
    df['EMPLOYED_YEARS'] = -df['DAYS_EMPLOYED'] / 365

    df['ACTIVE_CREDIT_RATIO'] = (
        df['BUREAU_ACTIVE_COUNT'] / (df['BUREAU_CREDIT_COUNT'] + 1)
    )

    df['DEBT_TO_CREDIT'] = (
        df['BUREAU_DEBT_SUM'] / (df['BUREAU_CREDIT_SUM_SUM'] + 1)
    )

    df['LATE_PAYMENT_RATIO'] = (
        df['INSTALMENTS_LATE_COUNT'] / (df['INSTALMENTS_COUNT'] + 1)
    )

    df['REFUSAL_RATIO'] = (
        df['PREV_REFUSED_COUNT'] / (df['PREV_APP_COUNT'] + 1)
    )

    return df