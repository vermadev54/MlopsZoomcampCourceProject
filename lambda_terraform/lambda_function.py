import os
import json
import base64
import pickle
import boto3
import boto3.session

from this import d
import pandas as pd

from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

from hyperopt import fmin, tpe, hp, STATUS_OK, Trials
from hyperopt.pyll import scope

import mlflow

from prefect import flow, task
from prefect.task_runners import SequentialTaskRunner

cred = boto3.Session().get_credentials()
ACCESS_KEY = cred.access_key
SECRET_KEY = cred.secret_key
SESSION_TOKEN = cred.token  ## optional



#RUN_ID = os.getenv('RUN_ID')

RUN_ID="d5bb00fc5a6345469baebb848ea950f7"
logged_model = f's3://jai-mlops-zoomcamp-tfstate/1/{RUN_ID}/artifacts/models_mlflow'
logged_artifact=f'1/{RUN_ID}/artifacts/encoder/'

model = mlflow.pyfunc.load_model(logged_model)


TEST_RUN = os.getenv('TEST_RUN', 'False') == 'True'


def get_artifact_encoder(artifact_path):

    s3client = boto3.client('s3', 
                            aws_access_key_id = ACCESS_KEY, 
                            aws_secret_access_key = SECRET_KEY, 
                            aws_session_token = SESSION_TOKEN
                           )

    response = s3client.get_object(Bucket='jai-mlops-zoomcamp-tfstate', Key=artifact_path)

    body = response['Body'].read()
    data = pickle.loads(body)
    return data



def prepare_features(data):
    #load encoder from artifact
    le_Gender= get_artifact_encoder(os.path.join(logged_artifact, "le_Gender.pkl"))
    le_Education_Level= get_artifact_encoder(os.path.join(logged_artifact, "le_Education_Level.pkl"))
    le_Marital_Status= get_artifact_encoder(os.path.join(logged_artifact, "le_Marital_Status.pkl"))
    le_Income_Category= get_artifact_encoder(os.path.join(logged_artifact, "le_Income_Category.pkl"))
    le_Card_Category= get_artifact_encoder(os.path.join(logged_artifact, "le_Card_Category.pkl"))

    #encode data
    data['Gender_n'] = le_Gender.transform([data['Gender']])[0]
    data['Education_Level_n'] = le_Education_Level.transform([data['Education_Level']])[0]
    data['Marital_Status_n'] = le_Marital_Status.transform([data['Marital_Status']])[0]
    data['Income_Category_n'] = le_Income_Category.transform([data['Income_Category']])[0]
    data['Card_Category_n'] = le_Card_Category.transform([data['Card_Category']])[0]
    
    # delete redundent columns
    dellist= ['Gender', 'Education_Level', 'Marital_Status', 'Income_Category', 'Card_Category']
    for key in dellist :
        del data[key]
    
    return data


def predict(features):
    pred = model.predict(pd.DataFrame(features,index=[0]))
    return pred[0]


def lambda_handler(profile):
    features = prepare_features(profile)
    response = predict(features)
  
    return {
                
            "statusCode": 200,
            'Attrition_Flag_predicted': response
    }