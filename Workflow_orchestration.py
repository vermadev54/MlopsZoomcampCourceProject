import argparse
import os
import pickle
import datetime

import mlflow
import numpy as np
from hyperopt import STATUS_OK, Trials, fmin, hp, tpe, space_eval
from hyperopt.pyll import scope
from sklearn.metrics import accuracy_score
from sklearn.ensemble import RandomForestClassifier

from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

from prefect import flow, task,get_run_logger
from prefect.task_runners import SequentialTaskRunner
import prefect


HPO_EXPERIMENT_NAME = "random-forest-hyperopt"
EXPERIMENT_NAME = "random-forest-best-models"

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment(EXPERIMENT_NAME)
mlflow.sklearn.autolog()


SPACE = {
    'max_depth': scope.int(hp.quniform('max_depth', 1, 20, 1)),
    'n_estimators': scope.int(hp.quniform('n_estimators', 10, 50, 1)),
    'min_samples_split': scope.int(hp.quniform('min_samples_split', 2, 10, 1)),
    'min_samples_leaf': scope.int(hp.quniform('min_samples_leaf', 1, 4, 1)),
    'random_state': 42
}

@task
def load_pickle(filename):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)



@task
def train_and_log_model(data_path, params):
    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_valid, y_valid = load_pickle(os.path.join(data_path, "valid.pkl"))
    X_test, y_test = load_pickle(os.path.join(data_path, "test.pkl"))

    with mlflow.start_run():
        params = space_eval(SPACE, params)        
        rf = RandomForestClassifier(**params)
        rf.fit(X_train, y_train)

        # evaluate model on the validation and test sets
        valid_accuracy = accuracy_score(y_valid, rf.predict(X_valid))
        mlflow.log_metric("valid_accuracy", valid_accuracy)
        test_accuracy = accuracy_score(y_test, rf.predict(X_test))
        mlflow.log_metric("test_accuracy", test_accuracy)
    

@task
def get_paths():
    data_dir="./output"
    return data_dir

@task 
def get_log_top():
    return 5


@flow(task_runner=SequentialTaskRunner())
def run():
    data_path   = get_paths()
    log_top     = get_log_top()

    print("run")

    client = MlflowClient()

    # retrieve the top_n model runs and log the models to MLflow
    experiment = client.get_experiment_by_name(HPO_EXPERIMENT_NAME)
    runs = client.search_runs(
        experiment_ids=experiment.experiment_id,
        run_view_type=ViewType.ACTIVE_ONLY,
        max_results=log_top,
        order_by=["metrics.test_accuracy DESC"]
    )
    for run in runs:
        #print(f"run id: {run.info.run_id}, rmse: {run.data.metrics['rmse']:.4f}")
        train_and_log_model(data_path=data_path, params=run.data.params)

    # select the model with the highest test accuracy
    experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
    # best_run = client.search_runs( ...  )[0]
    best_runs = client.search_runs(
                experiment_ids=experiment.experiment_id,
                #filter_string="metrics.rmse < 7",
                run_view_type=ViewType.ACTIVE_ONLY,
                max_results=log_top,
                order_by=["metrics.test_accuracy DESC"]
            )

    # register the best model
    #print(best_run)
    
    for best_run in best_runs:
        print(f"run id: {best_run.info.run_id}, test_accuracy: {best_run.data.metrics['test_accuracy']:.4f}")
        train_and_log_model(data_path=data_path, params=best_run.data.params)

    model_uri = f"runs:/{best_runs[0].info.run_id}/model"
    
    # mlflow.register_model( ... )
    mlflow.register_model(model_uri=model_uri, name="random-forest-best-models")


from prefect.deployments import DeploymentSpec
from prefect.orion.schemas.schedules import CronSchedule
from prefect.flow_runners import SubprocessFlowRunner
from datetime import timedelta




# DeploymentSpec(
#             flow=run,
#             name="model_training_2021-08-15",
#             schedule=CronSchedule(
#                 cron="* * * * *",
#                 timezone="America/New_York"),
#             flow_runner=SubprocessFlowRunner(),
#             tags=["ml"]
#             )
# print("hello")
run()