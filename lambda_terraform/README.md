## Deploying a model as a web-service with AppGateway lamda function using terraform

Steps followed: 
* Creating a virtual environment with Pipenv
* Creating a script for lambda function 
* Packaging the app to Docker
* uploading docker image to AWS ECR
* running terraform init -> plan -> apply command to launch the ApiGateway


Build docker
```bash
docker build -t credit-card-attrition-lambda-terraform .
```

Push docker to AWS ECR
```bash
docker push 989500836772.dkr.ecr.us-east-1.amazonaws.com/dev-credit-card-attrition-lambda-terraform:latest
```

Change directory to run LcA
```bash
cd infrastructure/
```
Access ApiGateway
```bash
example uri: https://35wa8mw36h.execute-api.us-east-1.amazonaws.com/development/resource
```
input data:
```bash
{
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
 'Avg_Utilization_Ratio': 0.172
}

```
Output:
```bash
{'statusCode': 200, 'Attrition_Flag_predicted': 'Existing Customer'}
```