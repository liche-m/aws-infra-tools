data "aws_iam_policy_document" "trust_policy" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_api_permissions" {
  statement {
    sid = "AllowLambdaToListAndDeleteVersions"

    actions = [
      "lambda:ListVersionsByFunction",
      "lambda:DeleteFunction"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "ListDeleteVersionsAccessPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda_api_permissions.json
}

# Attach the Trust Policy to the Lambda Execution Role
resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.app_name}-function-role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json
}

# Attach the Lambda API permissions policy to the Lambda Execution Role
resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# Attach the AWSLambdaBasicExecutionRole policy to the Lambda Execution Role
resource "aws_iam_role_policy_attachment" "attach_cw_access" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}
