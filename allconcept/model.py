import os
import json
import base64
import pickle

import boto3
import mlflow
import pandas as pd
import boto3.session
from this import d
from flask import Flask, jsonify, request
from prefect import flow, task
from hyperopt import STATUS_OK, Trials, hp, tpe, fmin
from hyperopt.pyll import scope
from sklearn.metrics import accuracy_score, mean_squared_error
from sklearn.ensemble import RandomForestClassifier
from prefect.task_runners import SequentialTaskRunner
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

cred = boto3.Session().get_credentials()
ACCESS_KEY = cred.access_key
SECRET_KEY = cred.secret_key
SESSION_TOKEN = cred.token  ## optional


def get_model_location(run_id):
    model_location = os.getenv('MODEL_LOCATION')

    if model_location is not None:
        return model_location

    model_bucket = os.getenv('MODEL_BUCKET', 'jai-mlops-data')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '1')

    model_location = f's3://{model_bucket}/{experiment_id}/{run_id}/artifacts/models_mlflow'
    return model_location

def get_model_artifact_location(run_id):
    model_artifact_location = os.getenv('MODEL_ARTIFACT_LOCATION')

    if model_artifact_location is not None:
        return model_artifact_location

    model_artifact_bucket = os.getenv('MODEL_ARTIFACT_BUCKET', 'jai-mlops-data')
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID', '1')

    model_artifact_location = f'{experiment_id}/{run_id}/artifacts/encoder'
   
    return model_artifact_location



def get_artifact_encoder(artifact_path):
    #print(artifact_path)

    s3client = boto3.client('s3', 
                            aws_access_key_id = ACCESS_KEY, 
                            aws_secret_access_key = SECRET_KEY, 
                            aws_session_token = SESSION_TOKEN
                           )

    response = s3client.get_object(Bucket='jai-mlops-data', Key=artifact_path)

    body = response['Body'].read()
    data = pickle.loads(body)
    return data



def load_model(run_id):
    model_path = get_model_location(run_id)
    artifact_path = get_model_artifact_location(run_id)

    #print("path",model_path,artifact_path)

    le_Gender= get_artifact_encoder(os.path.join(artifact_path, "le_Gender.pkl"))
    le_Education_Level= get_artifact_encoder(os.path.join(artifact_path, "le_Education_Level.pkl"))
    le_Marital_Status= get_artifact_encoder(os.path.join(artifact_path, "le_Marital_Status.pkl"))
    le_Income_Category= get_artifact_encoder(os.path.join(artifact_path, "le_Income_Category.pkl"))
    le_Card_Category= get_artifact_encoder(os.path.join(artifact_path, "le_Card_Category.pkl"))
    
    model = mlflow.pyfunc.load_model(model_path)

    return model,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category


def base64_decode(encoded_data):
    decoded_data = base64.b64decode(encoded_data).decode('utf-8')
    ride_event = json.loads(decoded_data)
    return ride_event


class ModelService:
    def __init__(self, model,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category,model_version=None, callbacks=None):
        self.model = model
        self.model_version = model_version
        self.le_Gender=le_Gender
        self.le_Education_Level=le_Education_Level
        self.le_Marital_Status=le_Marital_Status
        self.le_Income_Category=le_Income_Category
        self.le_Card_Category=le_Card_Category
        self.callbacks = callbacks or []

    def prepare_features(self, data):
        features = {}
        #encode data
        data['Gender_n'] = self.le_Gender.transform([data['Gender']])[0]
        data['Education_Level_n'] = self.le_Education_Level.transform([data['Education_Level']])[0]
        data['Marital_Status_n'] = self.le_Marital_Status.transform([data['Marital_Status']])[0]
        data['Income_Category_n'] = self.le_Income_Category.transform([data['Income_Category']])[0]
        data['Card_Category_n'] = self.le_Card_Category.transform([data['Card_Category']])[0]

        # delete redundent columns
        dellist= ['Gender', 'Education_Level', 'Marital_Status', 'Income_Category', 'Card_Category']
        for key in dellist :
            del data[key]
    
        features=data
        return features

    def predict(self, features):
        pred = self.model.predict(pd.DataFrame(features,index=[0]))
        return pred[0]

    def lambda_handler(self, event):
        # print(json.dumps(event))

        predictions_events = []

        for record in event['Records']:
            encoded_data = record['kinesis']['data']
            event = base64_decode(encoded_data)

            print(event)
            profile = event['profile']
            profile_id = event['profile_id']

            features = self.prepare_features(profile)
            prediction = self.predict(features)

            prediction_event = {
                'model': 'Credit_Card_Churn_Prediction',
                'version': self.model_version,
                'prediction': {'Churn_Prediction': prediction, 'profile_id': profile_id},
            }

            for callback in self.callbacks:
                callback(prediction_event)

            predictions_events.append(prediction_event)

        return {'predictions': predictions_events}

class KinesisCallback:
    def __init__(self, kinesis_client, prediction_stream_name):
        self.kinesis_client = kinesis_client
        self.prediction_stream_name = prediction_stream_name

    def put_record(self, prediction_event):
        profile_id = prediction_event['prediction']['profile_id']

        self.kinesis_client.put_record(
            StreamName=self.prediction_stream_name,
            Data=json.dumps(prediction_event),
            PartitionKey=str(profile_id),
        )


def create_kinesis_client():
    endpoint_url = os.getenv('KINESIS_ENDPOINT_URL')

    if endpoint_url is None:
        return boto3.client('kinesis')

    return boto3.client('kinesis', endpoint_url=endpoint_url)





def init(prediction_stream_name: str, run_id: str, test_run: bool):
    model,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category = load_model(run_id)

    callbacks = []

    if not test_run:
        kinesis_client = create_kinesis_client()
        kinesis_callback = KinesisCallback(kinesis_client, prediction_stream_name)
        callbacks.append(kinesis_callback.put_record)

    model_service = ModelService(model=model,le_Gender=le_Gender,le_Education_Level=le_Education_Level,le_Marital_Status=le_Marital_Status,le_Income_Category=le_Income_Category,le_Card_Category=le_Card_Category,model_version=run_id, callbacks=callbacks)

    return model_service
