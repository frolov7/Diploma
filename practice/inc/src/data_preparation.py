def load_source_data():
    app = pd.read_csv('application_train.csv')
    bureau = pd.read_csv('bureau.csv')
    bureau_balance = pd.read_csv('bureau_balance.csv')
    previous = pd.read_csv('previous_application.csv')
    installments = pd.read_csv('installments_payments.csv')
    return app, bureau, bureau_balance, previous, installments


def prepare_bureau_features(bureau, bureau_balance):
    bureau_balance['HAS_OVERDUE'] = (
        bureau_balance['STATUS'].isin(['1', '2', '3', '4', '5'])
    ).astype(int)

    balance_agg = bureau_balance.groupby('SK_ID_BUREAU').agg(
        MONTHS_BALANCE_COUNT=('MONTHS_BALANCE', 'count'),
        HAS_OVERDUE_SUM=('HAS_OVERDUE', 'sum')
    )
    bureau = bureau.merge(balance_agg, on='SK_ID_BUREAU', how='left')
    bureau['IS_ACTIVE'] = (bureau['CREDIT_ACTIVE'] == 'Active').astype(int)

    bureau_agg = bureau.groupby('SK_ID_CURR').agg(
        BUREAU_CREDIT_COUNT=('SK_ID_BUREAU', 'count'),
        BUREAU_ACTIVE_COUNT=('IS_ACTIVE', 'sum'),
        BUREAU_DEBT_SUM=('AMT_CREDIT_SUM_DEBT', 'sum'),
        BUREAU_CREDIT_SUM_SUM=('AMT_CREDIT_SUM', 'sum'),
        BUREAU_OVERDUE_MAX=('CREDIT_DAY_OVERDUE', 'max')
    )
    bureau_agg['BUREAU_ACTIVE_RATIO'] = (
        bureau_agg['BUREAU_ACTIVE_COUNT'] /
        bureau_agg['BUREAU_CREDIT_COUNT']
    )
    bureau_agg['BUREAU_HAS_OVERDUE'] = (
        bureau_agg['BUREAU_OVERDUE_MAX'] > 0
    ).astype(int)
    return bureau_agg


def prepare_previous_features(previous):
    previous['IS_APPROVED'] = (
        previous['NAME_CONTRACT_STATUS'] == 'Approved'
    ).astype(int)
    previous['IS_REFUSED'] = (
        previous['NAME_CONTRACT_STATUS'] == 'Refused'
    ).astype(int)
    previous_agg = previous.groupby('SK_ID_CURR').agg(
        PREV_APP_COUNT=('SK_ID_PREV', 'count'),
        PREV_APPROVED_COUNT=('IS_APPROVED', 'sum'),
        PREV_REFUSED_COUNT=('IS_REFUSED', 'sum'),
        PREV_CREDIT_MEAN=('AMT_CREDIT', 'mean'),
        PREV_ANNUITY_MEAN=('AMT_ANNUITY', 'mean')
    )
    previous_agg['APPROVAL_RATIO'] = (
        previous_agg['PREV_APPROVED_COUNT'] /
        previous_agg['PREV_APP_COUNT']
    )

    return previous_agg


def prepare_installments_features(installments):
    installments['LATE'] = (
        installments['DAYS_ENTRY_PAYMENT'] >
        installments['DAYS_INSTALMENT']
    ).astype(int)

    installments['DELAY'] = (
        installments['DAYS_ENTRY_PAYMENT'] -
        installments['DAYS_INSTALMENT']
    )
    installments_agg = installments.groupby('SK_ID_CURR').agg(
        INSTALMENTS_COUNT=('SK_ID_PREV', 'count'),
        INSTALMENTS_LATE_COUNT=('LATE', 'sum'),
        INSTALMENTS_DELAY_MEAN=('DELAY', 'mean'),
        INSTALMENTS_DELAY_MAX=('DELAY', 'max'),
        INSTALMENTS_PAYMENT_MEAN=('AMT_PAYMENT', 'mean'),
        INSTALMENTS_INSTALMENT_MEAN=('AMT_INSTALMENT', 'mean')
    )
    installments_agg['INSTALMENTS_LATE_RATIO'] = (
        installments_agg['INSTALMENTS_LATE_COUNT'] /
        installments_agg['INSTALMENTS_COUNT']
    )

    return installments_agg


def add_engineered_features(df):
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.fillna(0)

    df['CREDIT_TO_INCOME'] = df['AMT_CREDIT'] / (df['AMT_INCOME_TOTAL'] + 1)
    df['ANNUITY_TO_INCOME'] = df['AMT_ANNUITY'] / (df['AMT_INCOME_TOTAL'] + 1)
    df['GOODS_TO_CREDIT'] = df['AMT_GOODS_PRICE'] / (df['AMT_CREDIT'] + 1)

    df['AGE_YEARS'] = -df['DAYS_BIRTH'] / 365
    df['DAYS_EMPLOYED'] = df['DAYS_EMPLOYED'].replace(365243, 0)
    df['EMPLOYED_YEARS'] = -df['DAYS_EMPLOYED'] / 365
    df['EMPLOYED_TO_AGE'] = df['EMPLOYED_YEARS'] / (df['AGE_YEARS'] + 1)

    df['ACTIVE_CREDIT_RATIO'] = (
        df['BUREAU_ACTIVE_COUNT'] / (df['BUREAU_CREDIT_COUNT'] + 1)
    )
    df['DEBT_TO_CREDIT'] = (
        df['BUREAU_DEBT_SUM'] / (df['BUREAU_CREDIT_SUM_SUM'] + 1)
    )
    df['REFUSAL_RATIO'] = df['PREV_REFUSED_COUNT'] / (df['PREV_APP_COUNT'] + 1)
    df['HAS_REFUSALS'] = (df['PREV_REFUSED_COUNT'] > 0).astype(int)

    return df