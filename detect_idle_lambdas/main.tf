provider "aws" {
  region = "eu-west-1"

  # Make it faster by skipping something
  skip_metadata_api_check     = true
  skip_region_validation      = true
  skip_credentials_validation = true
}

terraform {
  backend "s3" {
    bucket         = "<terraform-state-s3-bucket>"
    key            = "<terraform-state-s3-bucket-key>"
    dynamodb_table = "<terraform-statelock-dynamodb>"
    region         = "<aws-region>"
  }
}
