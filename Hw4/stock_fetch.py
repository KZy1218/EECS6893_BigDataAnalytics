import yfinance as yf
import statsmodels.api as sm
import pandas as pd
import numpy as np
import statsmodels.api as sm
from sklearn.preprocessing import MinMaxScaler

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


tickers = ['AAPL', 'GOOGL', 'META', 'MSFT', 'AMZN']
error = pd.DataFrame(columns=tickers)
prediction = pd.DataFrame(columns=tickers)
PATH = {
    'error': '~/airflow/dags/error.csv', 
    'prediction': '~/airflow/dags/prediction.csv'}
stock_df = pd.DataFrame()


# train linear regression model and predict next day 'high' given current
def train_predict(**kwargs):
    global prediction, stock_df, error
    names = kwargs['names']
    stock_df = yf.download(names, group_by='ticker').dropna()
    df = stock_df
    scaler = MinMaxScaler()
    result = []
    for n in names:
        data = df[n].drop('Adj Close', axis=1)
        data = pd.DataFrame(scaler.fit_transform(data), columns=data.columns)
        y = data['High'][10:]
        X = np.zeros((y.size, 50))
        for i in range(y.size):
            X[i, :] = data[i: i+10].values.reshape(-1)
        model = sm.OLS(y, X).fit()
        data['High'][10:] = model.predict()
        inversed_data = pd.DataFrame(scaler.inverse_transform(data), columns=data.columns)
        result.append(inversed_data['High'][len(inversed_data['High'])-1])
        
    prediction.loc[len(prediction)] = result
    


# calculate the relative error of the prediction
def calculate(**kwargs):
    names = kwargs['names']
    df = kwargs['df']
    global error, prediction, stock_df
    if len(prediction) == 0 or not df:
        return
    actual = df.iloc[-1, :]
    reletative_error = []
    for n in names:
        reletative_error.append(prediction.iloc[-1, :][n] -  actual[n]['High']) / actual[n]['High']
    error.loc[len(error)] = reletative_error
    
    
# export the error dataframe into a csv file to a path
def export(**kwargs):
    error_path = kwargs['error']
    prediction_path = kwargs['prediction']
    error.to_csv(error_path)
    prediction.to_csv(prediction_path)


args = {
    'owner': 'yizhang',
    'depends_on_past': False,
    'email': ['yz4130@columbia.edu'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
    'schedule _interval': timedelta(minutes=2),
    'start_date': datetime(2022, 11, 20)
}

with DAG(
    'stock_dags',
    default_args=args,
    description='EECS6893 Homework 4 stock problem DAG',
    catchup=False
) as dag:
    
    t_predict = PythonOperator(
        task_id='predict',
        python_callable=train_predict,
        op_kwargs = {
            'names': tickers
        }  
    )
    
    t_calculate = PythonOperator(
        task_id='calculate_error',
        python_callable=calculate,
        op_kwargs = {
            'names': tickers,
            'df': stock_df
        }  
    )
    
    t_export = PythonOperator(
        task_id='export',
        python_callable=export,
        op_kwargs = PATH
    )
    
    # task dependencies 
    t_predict >> t_calculate >> t_export

