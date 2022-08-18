import json
import os
import pickle

import pandas
from prefect import flow, task
from pymongo import MongoClient
import pyarrow.parquet as pq

from evidently import ColumnMapping

from evidently.dashboard import Dashboard
from evidently.dashboard.tabs import DataDriftTab,RegressionPerformanceTab,ClassificationPerformanceTab

from evidently.model_profile import Profile
from evidently.model_profile.sections import DataDriftProfileSection, RegressionPerformanceProfileSection,ClassificationPerformanceProfileSection


from this import d
import pandas as pd
import pickle
import os

from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error

from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

import xgboost as xgb

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials,space_eval
from hyperopt.pyll import scope

import mlflow

from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner



RUN_ID="f1ba7bfd01624384bb4f2ac6f2741d98"
logged_model = f's3://jai-mlops-data/1/{RUN_ID}/artifacts/models_mlflow'
logged_artifact=f'1/{RUN_ID}/artifacts/encoder/'
model = mlflow.pyfunc.load_model(logged_model)

@task
def fetch_data():
    client = MongoClient("mongodb://localhost:27018/")
    data = client.get_database("prediction_service").get_collection("credit_card").find()
    df = pandas.DataFrame(list(data))
    return df

@task
def upload_target(filename):
    df=pd.read_csv(filename)
    client = MongoClient("mongodb://localhost:27018/")
    collection = client.get_database("prediction_service").get_collection("credit_card")
    collection.insert_many(df.to_dict('records'))
    client.close()

@task
def load_reference_data(filename):
    df=pd.read_csv(filename)
    reference_data= df.drop(['Unnamed: 0.1', 'Unnamed: 0','target'], axis=1)
    #print(df.columns)
    df['prediction'] = model.predict(pd.DataFrame(reference_data))
    print(df.prediction)
    return df

@task
def save_report(result):
    client = MongoClient("mongodb://localhost:27018/")
    client.get_database("prediction_service").get_collection("report_creditcard").insert_one(result[0])


@task
def save_html_report(result):
    result[1].save("evidently_report_credit_card_card.html")

@flow
def run_evidently(ref_data, data):

    numerical_features=["Customer_Age","Dependent_count","Months_on_book","Total_Relationship_Count",\
        "Months_Inactive_12_mon","Contacts_Count_12_mon","Credit_Limit","Total_Revolving_Bal",\
            "Avg_Open_To_Buy","Total_Amt_Chng_Q4_Q1","Total_Trans_Amt","Total_Trans_Ct","Total_Ct_Chng_Q4_Q1"]
    categorical_features=["Avg_Utilization_Ratio","Gender_n","Education_Level_n",\
        "Marital_Status_n","Income_Category_n","Card_Category_n"]

    profile = Profile(sections=[DataDriftProfileSection(), ClassificationPerformanceProfileSection()])
    mapping = ColumnMapping(prediction="prediction", numerical_features=numerical_features,
                            categorical_features=categorical_features,
                            datetime_features=[])
    profile.calculate(ref_data, data, mapping)

    dashboard = Dashboard(tabs=[DataDriftTab(), ClassificationPerformanceTab(verbose_level=0)])
    dashboard.calculate(ref_data, data, mapping)
    return json.loads(profile.json()), dashboard


@flow
def batch_analyze():
    upload_target("batch_monitoring_data/target1.csv")
    ref_data = load_reference_data("batch_monitoring_data/refrence_data.csv")
    data = fetch_data()

    #ref_data.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1, inplace=True)
    #data.drop(['Unnamed: 0.1', 'Unnamed: 0'], axis=1, inplace=True)

    #print("ref_data.columns",ref_data.columns)
    #print("data.columns",ref_data.prediction)

    result = run_evidently(ref_data, data)
    #run_evidently(ref_data, data)

    save_report(result)
    save_html_report(result)
 


if __name__ == "__main__":
    batch_analyze()

