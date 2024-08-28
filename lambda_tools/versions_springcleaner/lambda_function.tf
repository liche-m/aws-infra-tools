resource "aws_lambda_function" "this" {
  architectures = ["x86_64"]
  function_name = "${var.app_name}-function"
  image_uri     = local.image_uri
  memory_size   = 1024
  package_type  = "Image"
  role          = aws_iam_role.lambda_execution_role.arn
  timeout       = 900

  environment {
    variables = {
      Region = var.region
    }
  }

  tags = {
    "Name" = "${var.app_name}-function"
  }

  depends_on = [
    aws_iam_role.lambda_execution_role
  ]

}
