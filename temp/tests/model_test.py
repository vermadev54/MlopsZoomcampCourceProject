from pathlib import Path

import model
RUN_ID='96a17ab73a2645a2b7ecfeb4ef7cd6cd'


def read_text(file):
    test_directory = Path(__file__).parent

    with open(test_directory / file, 'rt', encoding='utf-8') as f_in:
        return f_in.read().strip()


def test_base64_decode():
    base64_input = read_text('data.b64')

    actual_result = model.base64_decode(base64_input)
    expected_result = {'model': 'Credit_Card_Churn_Prediction', 'version': '96a17ab73a2645a2b7ecfeb4ef7cd6cd', 'prediction': {'Churn_Prediction': 'Existing Customer', 'profile_id': 52}}

    assert actual_result == expected_result



def test_prepare_features():
    model_pkl,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category= model.load_model(RUN_ID)
    model_service = model.ModelService(model_pkl,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category)

    data = {
                'Customer_Age': 45,
                'Gender': 'M',
                'Dependent_count': 3,
                'Education_Level': 'High School',
                'Marital_Status': 'Married',
                'Income_Category': '$60K - $80K',
                'Card_Category': 'Blue',
                'Months_on_book': 39,
                'Total_Relationship_Count': 5,
                'Months_Inactive_12_mon': 1,
                'Contacts_Count_12_mon': 3,
                'Credit_Limit': 12691.0,
                'Total_Revolving_Bal': 777,
                'Avg_Open_To_Buy': 11914.0,
                'Total_Amt_Chng_Q4_Q1': 1.335,
                'Total_Trans_Amt': 1144,
                'Total_Trans_Ct': 42,
                'Total_Ct_Chng_Q4_Q1': 1.625,
                'Avg_Utilization_Ratio': 0.061
                }

    actual_features = model_service.prepare_features(data)

    expected_fetures = {
                        'Customer_Age': 45,
                        'Dependent_count': 3,
                        'Months_on_book': 39,
                        'Total_Relationship_Count': 5,
                        'Months_Inactive_12_mon': 1,
                        'Contacts_Count_12_mon': 3,
                        'Credit_Limit': 12691.0,
                        'Total_Revolving_Bal': 777,
                        'Avg_Open_To_Buy': 11914.0,
                        'Total_Amt_Chng_Q4_Q1': 1.335,
                        'Total_Trans_Amt': 1144,
                        'Total_Trans_Ct': 42,
                        'Total_Ct_Chng_Q4_Q1': 1.625,
                        'Avg_Utilization_Ratio': 0.061,
                        'Gender_n': 1,
                        'Education_Level_n': 3,
                        'Marital_Status_n': 1,
                        'Income_Category_n': 2,
                        'Card_Category_n': 0
                        }
    

    assert actual_features == expected_fetures


class ModelMock:
    def __init__(self, value):
        self.value = value

    def predict(self, X):
        n = len(X)
        return [self.value] * n


def test_predict():
    model_pkl,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category= model.load_model(RUN_ID)
    model_service = model.ModelService(model_pkl,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category)

    features = {
                'Customer_Age': 45,
                'Dependent_count': 3,
                'Months_on_book': 39,
                'Total_Relationship_Count': 5,
                'Months_Inactive_12_mon': 1,
                'Contacts_Count_12_mon': 3,
                'Credit_Limit': 12691.0,
                'Total_Revolving_Bal': 777,
                'Avg_Open_To_Buy': 11914.0,
                'Total_Amt_Chng_Q4_Q1': 1.335,
                'Total_Trans_Amt': 1144,
                'Total_Trans_Ct': 42,
                'Total_Ct_Chng_Q4_Q1': 1.625,
                'Avg_Utilization_Ratio': 0.061,
                'Gender_n': 1,
                'Education_Level_n': 3,
                'Marital_Status_n': 1,
                'Income_Category_n': 2,
                'Card_Category_n': 0
                }


    

    actual_prediction = model_service.predict(features)
    expected_prediction = 'Existing Customer'

    assert actual_prediction == expected_prediction


def test_lambda_handler():
    model_service_1 = model.init(
    prediction_stream_name=None,
    run_id=RUN_ID,
    test_run=False,
)
    model_pkl,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category= model.load_model(RUN_ID)
    model_service = model.ModelService(model_pkl,le_Gender,le_Education_Level,le_Marital_Status,le_Income_Category,le_Card_Category)

    base64_input = read_text('data2.b64')



    event = {
        "Records": [
            {
                "kinesis": {
                    "data": base64_input,
                },
            }
        ]
    }

    actual_predictions = model_service.lambda_handler(event)
    expected_predictions = {
        'predictions': [
                    {
                    "model": "Credit_Card_Churn_Prediction",
                    "version": None,
                    "prediction": {"Churn_Prediction": "Existing Customer", "profile_id":50}
                    }
        ]
    }


    assert actual_predictions == expected_predictions
