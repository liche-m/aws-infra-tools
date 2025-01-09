variable "app_name" {
  type        = string
  default     = "detect-idle-lambdas"
  description = "The name of the application/service."
}

variable "image_uri" {
  type        = string
  description = "The URI of the image stored in Amazon ECR."
}

variable "s3_bucket_name" {
  type        = string
  description = "A unique name for the Amazon S3 Bucket."
}
