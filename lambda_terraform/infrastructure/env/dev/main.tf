terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  backend "s3" {
    bucket = "jai-mlops-zoomcamp-tfstate"
    key    = "test_service_dev"
  }
}

provider "aws" {
  region  = "us-east-1"
  
}

data "aws_caller_identity" "current_identity" {}

locals {
  account_id = data.aws_caller_identity.current_identity.account_id
}



module "lambda" {
  source = "../../modules/lambda"
  environment = var.environment
}

module "apigw" {
  source = "../../modules/api_gateway"
  environment = var.environment
  lambda_invoke_arn = module.lambda.lambda_invoke_arn
}