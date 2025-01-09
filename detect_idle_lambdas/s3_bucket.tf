resource "aws_s3_bucket" "store_csv_files" {
  bucket = var.s3_bucket_name

  tags = {
    Name = var.s3_bucket_name
  }
}
