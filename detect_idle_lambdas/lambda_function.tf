resource "aws_lambda_function" "idle_function_detector" {
  architectures = ["x86_64"]
  function_name = "${var.app_name}-function"
  image_uri     = var.image_uri
  memory_size   = 1024
  package_type  = "Image"
  role          = aws_iam_role.lambda_execution_role.arn
  timeout       = 900

  environment {
    variables = {
      s3_bucket = var.s3_bucket_name
    }
  }

  tags = {
    "Name" = "${var.app_name}-function"
  }

}
