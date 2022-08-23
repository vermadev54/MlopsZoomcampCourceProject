# pylint: disable=duplicate-code

import json

import requests
from deepdiff import DeepDiff


data={
 'Customer_Age': 55,
 'Gender': 'F',
 'Dependent_count': 3,
 'Education_Level': 'Uneducated',
 'Marital_Status': 'Single',
 'Income_Category': 'Unknown',
 'Card_Category': 'Blue',
 'Months_on_book': 47,
 'Total_Relationship_Count': 4,
 'Months_Inactive_12_mon': 3,
 'Contacts_Count_12_mon': 3,
 'Credit_Limit': 14657.0,
 'Total_Revolving_Bal': 2517,
 'Avg_Open_To_Buy': 12140.0,
 'Total_Amt_Chng_Q4_Q1': 0.166,
 'Total_Trans_Amt': 6009,
 'Total_Trans_Ct': 53,
 'Total_Ct_Chng_Q4_Q1': 0.514,
 'Avg_Utilization_Ratio': 0.172}

print(json.dumps(data, indent=2))
url = 'http://localhost:8001/predict'
actual_response = requests.post(url, json=data)
print('actual response:',actual_response.json())
actual_response=actual_response.json()

print(json.dumps(actual_response, indent=2))

expected_response= {'Attrition_Flag_predicted': 'Attrited Customer', 'statusCode': 200}

print(expected_response)



diff = DeepDiff(actual_response, expected_response, significant_digits=1)
print(f'diff={diff}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff

