import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import numpy as np
#import os
#from django.conf import settings




def trainModel():
    # Load the dataset
    
    #data_path = os.path.join(settings.BASE_DIR, 'meter_data.csv')
    #raw_data = pd.read_csv(data_path)

    raw_data = pd.read_csv('meter_data.csv')
    
    # Prepare the data
    X_data = raw_data.drop(columns=['Date & Time', 'Cost(NGN)', 'Meter Reset'])
    y_data = raw_data['Cost(NGN)']

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X_data, y_data, test_size=0.2)

    # Train the linear regression model
    lr_model = LinearRegression()
    lr_model.fit(X_train, y_train)

    # Save the trained model to a file
    joblib.dump(lr_model, 'linear_regression_model2.pkl')

    # Evaluate the model
    y_test_pred = lr_model.predict(X_test)
    lr_model_MSE = mean_squared_error(y_test, y_test_pred)
    lr_model_R2 = r2_score(y_test, y_test_pred)

    # Print the results
    print(f"Model saved as 'linear_regression_model2.pkl'")
    print(f"Test MSE: {lr_model_MSE}")
    print(f"Test R2 Score: {lr_model_R2}")
    