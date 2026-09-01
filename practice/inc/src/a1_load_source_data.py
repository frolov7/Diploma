import pandas as pd


def load_source_data():
    app = pd.read_csv('application_train.csv')
    bureau = pd.read_csv('bureau.csv')
    bureau_balance = pd.read_csv('bureau_balance.csv')
    previous = pd.read_csv('previous_application.csv')
    installments = pd.read_csv('installments_payments.csv')

    return app, bureau, bureau_balance, previous, installments