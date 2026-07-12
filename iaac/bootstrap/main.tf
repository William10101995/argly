# Bucket de S3 para almacenar el estado
resource "aws_s3_bucket" "terraform_state" {
  bucket        = "argly-tofu-state-iaac"
  force_destroy = false
}

# Bloquear el acceso público al bucket por seguridad
resource "aws_s3_bucket_public_access_block" "terraform_state_access" {
  bucket                  = aws_s3_bucket.terraform_state.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Habilitar el versionado (permite recuperar un estado anterior si algo sale mal)
resource "aws_s3_bucket_versioning" "terraform_state_versioning" {
  bucket = aws_s3_bucket.terraform_state.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Tabla de DynamoDB para el bloqueo de estado (State Locking)
resource "aws_dynamodb_table" "terraform_locks" {
  name         = "argly-tofu-locks-iaac"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }
}
