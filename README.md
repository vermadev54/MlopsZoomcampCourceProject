## MlopsZoomcampCourceProject 2022
Repository includes code and document related to project for MLOps Zoomcamp course  https://github.com/DataTalksClub/mlops-zoomcamp

## Problem statement: Credit Card Attrition

### Overview

- Attrition on credit cards has become a major worry for the banking industry.
Given that the expense of obtaining new consumers is higher than the expense of keeping existing customers, it significantly affects profitability.
- In this work, a selection of supervised Machine Learning models to identify which customers want to cancel their credit cards is evaluated.
- Attrition prediction models are important to reduce the cancellation of credit card products and analyze which customers have a greater tendency to cancel. 
- This work was carried out through a strategic segmentation focusing on the client to generate campaigns according to the profile of each one, to understand and anticipate their behavior. Likewise, productive resources were focused on high-value groups, as it is cheaper to retain a client than attract a new one.

### Objective

Predicting customers who are likely to drop off credit card. to work on customer retaintion strategy like running compaigns.  

## Dataset 
[Credit Card Churn Prediction](https://www.kaggle.com/datasets/anwarsan/credit-card-bank-churn) used for this project.

## Solution i have build random forest classification model with accuracy ~98%

* Model training 
```bash
python3 train.py --data_path 

```
* data preprocessing/training/mlflow experiment tracking /prefect Workflow orchestration 
```bash
python3 preprocessing_data.py
```

* Model registery
```bash
python3 registry_model.py --data_path ./output
```

* Prefect deployment with scheduled crons

```bash
prefect deployment create prefect_deploy.py
```

## running mlflow server with cloud db and s3 storage
```bash 
mlflow server -h 0.0.0.0 -p 5000 --backend-store-uri postgresql://mlflow:FdXoiuOCyQvyiDL0Gftk@mlflow-database.ciuzmsnp32jg.us-east-1.rds.amazonaws.com:5432/mlflow_db --default-artifact-root s3://jai-mlops-zoomcamp-tfstate
```

## running prefect server on remeote server for Workflow orchestration 
```bash
prefect config unset PREFECT_ORION_UI_API_URL
prefect config set PREFECT_ORION_UI_API_URL="http://54.146.195.209:4200/api"
prefect orion start --host 0.0.0.0
```
