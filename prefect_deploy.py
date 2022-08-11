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

@task
def read_dataframe(filename):
    df = pd.read_csv(filename)
    return df

def dump_pickle(obj, filename):
    with open(filename, "wb") as f_out:
        return pickle.dump(obj, f_out)

@task
def preprocess(data: pd.DataFrame,\
               le_Gender: LabelEncoder,\
               le_Education_Level:LabelEncoder,\
               le_Marital_Status:LabelEncoder,\
               le_Income_Category:LabelEncoder,\
               le_Card_Category:LabelEncoder
              ):
    
    #fit encoder
    data['Gender_n'] = le_Gender.fit_transform(data['Gender'])
    data['Education_Level_n'] = le_Education_Level.fit_transform(data['Education_Level'])
    data['Marital_Status_n'] = le_Marital_Status.fit_transform(data['Marital_Status'])
    data['Income_Category_n'] = le_Income_Category.fit_transform(data['Income_Category'])
    data['Card_Category_n'] = le_Card_Category.fit_transform(data['Card_Category'])

    data_n = data.drop(['Gender', 'Education_Level', 'Marital_Status', 'Income_Category', 'Card_Category'], axis = 1)
    data_n = data_n.drop('CLIENTNUM', axis = 1)
    train = data_n.drop('Attrition_Flag',  axis = 1)
    target = data_n['Attrition_Flag']
    
    
    train_ratio = 0.75
    validation_ratio = 0.15
    test_ratio = 0.10

    # train is now 75% of the entire data set
    # the _junk suffix means that we drop that variable completely
    x_train, x_test, y_train, y_test = train_test_split(train, target, test_size=1 - train_ratio)

    # test is now 10% of the initial data set
    # validation is now 15% of the initial data set
    x_val, x_test, y_val, y_test = train_test_split(x_test, y_test, test_size=test_ratio/(test_ratio + validation_ratio)) 

    return x_train, x_test, y_train, y_test, x_val, y_val, le_Gender, le_Education_Level, le_Marital_Status, le_Income_Category, le_Card_Category 



@task
def train_model_search(x_train, y_train, x_val, y_val, SPACE):
    def objective(params):
        with mlflow.start_run():
            mlflow.set_tag("model", "randomforest")
            mlflow.log_params(params)
            params = space_eval(SPACE, params)        
            rf = RandomForestClassifier(**params)
            rf.fit(x_train, y_train)
            
            y_pred = rf.predict(x_val)
            
            accuracy = accuracy_score(y_val, y_pred)
            mlflow.log_metric("accuracy", accuracy)

        return {'loss': - accuracy, 'status': STATUS_OK}


    best_result = fmin(
        fn=objective,
        space=SPACE,
        algo=tpe.suggest,
        max_evals=1,
        trials=Trials()
    )
    return

@task
def train_best_model(x_train, y_train, x_val, y_val,x_test, y_test,\
                    le_Gender, le_Education_Level, le_Marital_Status, le_Income_Category, le_Card_Category):
    with mlflow.start_run():

        
        best_params = {
                'max_depth': 14,
                'n_estimators': 23,
                'min_samples_split': 6,
                'min_samples_leaf': 2,
                'random_state': 42}

        mlflow.log_params(best_params)
        
    
        rf = RandomForestClassifier(**best_params)
        rf.fit(x_train, y_train)
        y_pred = rf.predict(x_val)
        accuracy = accuracy_score(y_val, y_pred)
        mlflow.log_metric("accuracy", accuracy)
        
        dest_path="./models"
        #os.makedirs(dest_path, exist_ok=True)
        
        dump_pickle(le_Gender, os.path.join(dest_path, "le_Gender.pkl"))
        dump_pickle(le_Education_Level, os.path.join(dest_path, "le_Education_Level.pkl"))
        dump_pickle(le_Marital_Status, os.path.join(dest_path, "le_Marital_Status.pkl"))
        dump_pickle(le_Income_Category, os.path.join(dest_path, "le_Income_Category.pkl"))
        dump_pickle(le_Card_Category, os.path.join(dest_path, "le_Card_Category.pkl"))
        dump_pickle((x_train, y_train), os.path.join(dest_path, "train.pkl"))
        dump_pickle((x_val, y_val), os.path.join(dest_path, "valid.pkl"))
        dump_pickle((x_test, y_test), os.path.join(dest_path, "test.pkl"))
   
        
    
            
        mlflow.log_artifact("./models/le_Gender.pkl", artifact_path="preprocessor")
        
        mlflow.sklearn.log_model(rf, artifact_path="models_mlflow")

@flow(task_runner=SequentialTaskRunner())
def main(data_path: str="./data/credit_card_churn.csv"):
    mlflow.set_tracking_uri("http://127.0.0.1:5000")
    mlflow.set_experiment("random-forest-best-models")


    #initilize the encoder
    le_Gender = LabelEncoder()
    le_Education_Level = LabelEncoder()
    le_Marital_Status = LabelEncoder()
    le_Income_Category = LabelEncoder()
    le_Card_Category = LabelEncoder()
    
    # load csv files
    data = read_dataframe(data_path)
    #print(data.head())
    
    x_train, x_test, y_train, y_test, x_val, y_val,\
         le_Gender,le_Education_Level,\
         le_Marital_Status, le_Income_Category,\
        le_Card_Category = preprocess(data,\
                                        le_Gender,\
                                        le_Education_Level,\
                                        le_Marital_Status,\
                                        le_Income_Category,\
                                        le_Card_Category ).result()


    #print(len(train))

    
    #print(len(train))
    
    SPACE = {
    'max_depth': scope.int(hp.quniform('max_depth', 1, 20, 1)),
    'n_estimators': scope.int(hp.quniform('n_estimators', 10, 50, 1)),
    'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 10, 1)),
    'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 4, 1)),
    'random_state': 42}

    train_model_search(x_train, y_train, x_val, y_val, SPACE)
    
    train_best_model(x_train, y_train, x_val, y_val,x_test, y_test,\
                     le_Gender, le_Education_Level, le_Marital_Status, le_Income_Category, le_Card_Category)

from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import IntervalSchedule
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner
from datetime import timedelta

DeploymentSpec(
    flow=main,
    name="model_training",
    schedule=IntervalSchedule(interval=timedelta(minutes=5)),
    flow_runner=SubprocessFlowRunner(),
    tags=["ml"]
)

# DeploymentSpec(
#     flow=main,
#     name="model_training_2021-08-15",
#     schedule=CronSchedule(
#         cron="0 9 15 * *",
#         timezone="America/New_York"),
#     flow_runner=SubprocessFlowRunner(),
#     tags=["ml"]
# )



