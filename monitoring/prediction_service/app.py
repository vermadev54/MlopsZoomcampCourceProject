from ast import Str
import os
import pickle
from unittest.util import strclass

import requests
from flask import Flask
from flask import request
from flask import jsonify
import mlflow

from pymongo import MongoClient


MODEL_FILE = os.getenv('MODEL_FILE', "my_model")

EVIDENTLY_SERVICE_ADDRESS = os.getenv('EVIDENTLY_SERVICE', 'http://127.0.0.1:5000')
MONGODB_ADDRESS = os.getenv("MONGODB_ADDRESS", "mongodb://127.0.0.1:27017")

model = mlflow.pyfunc.load_model(MODEL_FILE)



app = Flask('duration')
mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("credit_card")


@app.route('/predict', methods=['POST'])
def predict(features):
    pred = model.predict(features)

    result = {
        'credir_alter': str(pred),
    }

    save_to_db(record, str(y_pred))
    send_to_evidently_service(record, str(y_pred))
    return jsonify(result)


def save_to_db(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    collection.insert_one(rec)


def send_to_evidently_service(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    requests.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/credit_card", json=[rec])


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9695)