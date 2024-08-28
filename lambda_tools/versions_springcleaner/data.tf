data "aws_caller_identity" "this" {}

data "aws_region" "current" {}

locals {
  account_id = data.aws_caller_identity.this.account_id
  aws_region = data.aws_region.current.name
  image_uri  = "${local.account_id}.dkr.ecr.${local.aws_region}.amazonaws.com/infra/versions-springcleaner:${var.image_tag}"
}
