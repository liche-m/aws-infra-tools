variable "app_name" {
  type        = string
  default     = "lambda-versions-springcleaner"
  description = "The name of the application/service."
}

variable "region" {
  type        = string
  default     = "eu-west-1"
  description = "The AWS region where your Lambda Functions are located."
}

variable "account" {
  type        = string
  description = "The name of the AWS account."
}

variable "image_tag" {
  type        = string
  default     = "1"
  description = "The tag associated to the Container Image stored in the Amazon ECR repository."
}
