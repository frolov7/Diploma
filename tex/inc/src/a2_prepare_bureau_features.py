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