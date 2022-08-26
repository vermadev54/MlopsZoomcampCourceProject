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
   {"model": "Credit_Card_Churn_Prediction",
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
2. Merge PR to `develop`: `.github/workflows/cd-deploy.yml`
    * Terraform plan, Terraform apply, Docker build & ECR push, Update Lambda config

### Notes

* Unfortunately, the `RUN_ID` (if set via the `ENV` or `ARG` in `Dockerfile`), disappears during lambda invocation.
We'll set it via `aws lambda update-function-configuration` CLI command (refer to `deploy_manual.sh` or `.github/workflows/cd-deploy.yml`)
    
