# pylint: disable=duplicate-code

import json

import requests
from deepdiff import DeepDiff

with open('event.json', 'rt', encoding='utf-8') as f_in:
    event = json.load(f_in)


url = 'http://localhost:8080/2015-03-31/functions/function/invocations'
actual_response = requests.post(url, json=event).json()

print('actual response:')
print(json.dumps(actual_response, indent=2))

expected_response = {
  "predictions": [
    {
      "model": "Credit_Card_Churn_Prediction",
      "version": "f1ba7bfd01624384bb4f2ac6f2741d98",
      "prediction": {
        "Churn_Prediction": "Existing Customer",
        "profile_id": 10
      }
    }
  ]
}

print('expected_response:')
print(json.dumps(expected_response, indent=2))


diff = DeepDiff(actual_response, expected_response, significant_digits=1)
print(f'diff={diff}')

assert 'type_changes' not in diff
assert 'values_changed' not in diff

print("test_docker_all_done")



