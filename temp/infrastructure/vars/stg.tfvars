source_stream_name = "stg_credit_profile_events"
output_stream_name = "stg_credit_profile_predictions"
model_bucket = "stg-credit-profile"
lambda_function_local_path = "../lambda_function.py"
docker_image_local_path = "../Dockerfile"
ecr_repo_name = "stg_stream_profile_predictions"
lambda_function_name = "stg_profile_lambda"
