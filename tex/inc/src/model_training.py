def prepare_train_test_data(dataset_path, settings):
    df = pd.read_csv(dataset_path)
    
    y = df['TARGET']
    X = pd.get_dummies(df.drop(columns=['TARGET', 'SK_ID_CURR']))
    
    X.columns = X.columns.str.replace(' ', '_')
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=settings['test_size'],
        random_state=settings['random_state'],
        stratify=y
    )
    
    return X_train, X_test, y_train, y_test, X.columns


def train_lightgbm_model(X_train, y_train, feature_columns, settings):
    scale_pos_weight = len(y_train[y_train == 0]) / len(y_train[y_train == 1])

    base_model = LGBMClassifier(
        scale_pos_weight=scale_pos_weight,
        random_state=settings['random_state'],
        n_jobs=-1,
        force_col_wise=True
    )
    
    param_grid = {
        name: settings[name]
        for name in [
            'n_estimators',
            'learning_rate',
            'num_leaves',
            'max_depth',
            'min_child_samples'
        ]
    }
    
    search = RandomizedSearchCV(
        base_model, param_grid,
        n_iter=settings['random_search_iter'],
        scoring=settings['scoring'],
        cv=settings['cv'],
        random_state=settings['random_state'],
        n_jobs=-1
    )
    
    search.fit(X_train, y_train)
    model = search.best_estimator_
    
    joblib.dump(model, 'model.pkl')
    joblib.dump(feature_columns, 'columns.pkl')

    return model