## Code snippets



#### Execution


1. To create infra (manually, in order to test on staging env)
    ```shell
    # Initialize state file (.tfstate)
    terraform init

    # Check changes to new infra plan
    terraform plan -var-file=vars/stg.tfvars
    ```

    ```shell
    # Create new infra
    terraform apply -var-file=vars/stg.tfvars
    ```

2. To prepare aws env (copy model artifacts, set env-vars for lambda etc.):
    ```
    . ./scripts/deploy_manual.sh
    ```

3. To test the pipeline end-to-end with our new cloud infra:
    ```
    . ./scripts/test_cloud_e2e.sh
    ```

4. And then check on CloudWatch logs. Or try `get-records` on the `output_kinesis_stream` (refer to `integration_test`)

    ```
   {
    "model": "Credit_Card_Churn_Prediction",
    "version": "96a17ab73a2645a2b7ecfeb4ef7cd6cd",
    "prediction": {"Churn_Prediction": "Existing Customer", "profile":52}
    }

    ```


5. Destroy infra after use:
    ```shell
    # Delete infra after your work, to avoid costs on any running services
    terraform destroy
    ```

<br>

### CI/CD

1. Create a PR (feature branch): `.github/workflows/ci-tests.yml`
    * Env setup, Unit test, Integration test, Terraform plan

    ![ci-test](/allconcept/images/CI-tests.png)
2. Merge PR to `develop`: `.github/workflows/cd-deploy.yml`
    * Terraform plan, Terraform apply, Docker build & ECR push, Update Lambda config

    ![cd-deploy](/allconcept/images/CD-deploy.png)
    
    

## Pre-commit-hooks:
    
![pre-commit](/allconcept/images/pre-commit-hooks.png)





## Check stream output:
steps:
1. set input stream
   ```
   KINESIS_STREAM_INPUT='credit_profile_events-credit_card_profile_prediction'

    ```

2. Send the records

   ```
   shell
   aws kinesis put-record \
       --stream-name ${KINESIS_STREAM_INPUT}  \
       --partition-key 1     \
       --data '{"profile": {"Customer_Age": 45, "Gender": "M", "Dependent_count": 3, "Education_Level": "High School", "Marital_Status": "Married", "Income_Category": "$60K - $80K", "Card_Category": "Blue", "Months_on_book": 39, "Total_Relationship_Count": 5, "Months_Inactive_12_mon": 1, "Contacts_Count_12_mon": 3, "Credit_Limit": 12691.0, "Total_Revolving_Bal": 777, "Avg_Open_To_Buy": 11914.0, "Total_Amt_Chng_Q4_Q1": 1.335, "Total_Trans_Amt": 1144, "Total_Trans_Ct": 42, "Total_Ct_Chng_Q4_Q1": 1.625, "Avg_Utilization_Ratio": 0.061}, "profile_id": 56}'
    ```
   output:

    ```
        {
            "ShardId": "shardId-000000000001",
            "SequenceNumber": "49632788809943113530008276481443180948266012360377892882"
        }
    ```

3. set output stream

    ```
    KINESIS_STREAM_OUTPUT="credit_profile_predictions-credit_card_profile_prediction"
    ```

4. set Shard
   ```
    SHARD='shardId-000000000001'
    ```
5. get SHARD_ITERATOR
   ```
    SHARD_ITERATOR=$(aws kinesis \
        get-shard-iterator \
            --shard-id ${SHARD} \
            --shard-iterator-type TRIM_HORIZON \
            --stream-name ${KINESIS_STREAM_OUTPUT} \
            --query 'ShardIterator' \
    )
    ```
6. Get All result
   ```
    RESULT=$(aws kinesis get-records --shard-iterator $SHARD_ITERATOR)
    ```
    ![Records in stream](/allconcept/images/echo1.png)

7. echo result
   ```
    echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode

    ```
    OUTPUT:

    ```
    (temp) (base) ubuntu@ip-172-31-87-216:~/MlopsZoomcampCourceProject$ echo ${RESULT} | jq -r '.Records[0].Data' | base64 --decode

    {"model": "Credit_Card_Churn_Prediction", "version": "96a17ab73a2645a2b7ecfeb4ef7cd6cd", "prediction": {"Churn_Prediction": "Existing Customer", "profile_id": 10}}

    ```

    ![result](/allconcept/images/echo2.png)







### Notes

* Unfortunately, the `RUN_ID` (if set via the `ENV` or `ARG` in `Dockerfile`), disappears during lambda invocation.
We'll set it via `aws lambda update-function-configuration` CLI command (refer to `deploy_manual.sh` or `.github/workflows/cd-deploy.yml`)
