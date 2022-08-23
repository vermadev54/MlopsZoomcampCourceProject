## Deploying a model as a web-service with flask and mlflow 

* Creating a virtual environment with Pipenv
* Creating a script for predictiong 
* Putting the script into a Flask app
* Packaging the app to Docker


```bash
docker build -t credit-card-attrition:v1 .
```

```bash
docker run -it --rm -p 9696:9696  ride-duration-prediction-service:v1
```


* exporting enviroment variable to download model from S3

```bash
export AWS_ACCESS_KEY_ID="**************"
export AWS_SECRET_ACCESS_KEY="******************************************"
export AWS_DEFAULT_REGION="**************"
```

* deployment with docker container

```bash
docker run -it --rm \
    -p 9696:9696 \
    -e AWS_ACCESS_KEY_ID="${AWS_ACCESS_KEY_ID}" \
    -e AWS_SECRET_ACCESS_KEY="${AWS_SECRET_ACCESS_KEY}" \
    -e AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION}" \
    credit-card-attrition:v1
```

* Run unit test:

```bash
cd test
python model_test.py
```

* Run integration test:

```bash
cd integration-test
./run.sh 
```


