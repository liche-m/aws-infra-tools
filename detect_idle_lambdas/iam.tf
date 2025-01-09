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

data "aws_iam_policy_document" "s3_permissions" {
  statement {
    sid = "AllowLambdaToUploadToS3"

    actions = [
      "s3:PutObject"
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}",
      "arn:aws:s3:::${var.s3_bucket_name}/*"
    ]
  }
}

data "aws_iam_policy_document" "cw_permissions" {
  statement {
    sid = "AllowLambdaToGetInvocationData"

    actions = [
      "cloudwatch:GetMetricData"
    ]

    resources = [
      "*"
    ]
  }
}

data "aws_iam_policy_document" "lambda_api_permissions" {
  statement {
    sid = "AllowLambdaToCallReadOnlyLambdaAPIs"

    actions = [
      "lambda:GetFunction",
      "lambda:ListFunctions"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_policy" "s3_policy" {
  name   = "S3UploadAccessPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.s3_permissions.json
}

resource "aws_iam_policy" "cw_policy" {
  name   = "CWGetMetricDataAccessPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.cw_permissions.json
}

resource "aws_iam_policy" "lambda_policy" {
  name   = "LambdaReadOnlyAccessPolicy"
  path   = "/"
  policy = data.aws_iam_policy_document.lambda_api_permissions.json
}

# Attach the Trust Policy to the Lambda Execution Role
resource "aws_iam_role" "lambda_execution_role" {
  name               = "${var.app_name}-function-role"
  assume_role_policy = data.aws_iam_policy_document.trust_policy.json
}

# Attach the AWSLambdaBasicExecutionRole policy to the Lambda Execution Role
resource "aws_iam_role_policy_attachment" "attach_lambda_basic_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Attach the S3UploadAccessPolicy policy to the Lambda Execution Role
resource "aws_iam_role_policy_attachment" "attach_s3_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.s3_policy.arn
}

# Attach the CWGetMetricDataAccessPolicy policy to the Lambda Execution Role
resource "aws_iam_role_policy_attachment" "attach_cw_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.cw_policy.arn
}

# Attach the LambdaReadOnlyAccessPolicy policy to the Lambda Execution Role
resource "aws_iam_role_policy_attachment" "attach_lambda_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}
