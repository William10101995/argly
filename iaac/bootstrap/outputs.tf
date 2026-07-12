output "state_bucket" {
  value       = aws_s3_bucket.terraform_state.bucket
  description = "Nombre del bucket S3 donde se almacena el estado remoto."
}

output "dynamodb_table" {
  value       = aws_dynamodb_table.terraform_locks.name
  description = "Nombre de la tabla de DynamoDB utilizada para los bloqueos (Locks)."
}

output "github_actions_role_arn" {
  value       = aws_iam_role.github_actions.arn
  description = "ARN del Rol de IAM que GitHub Actions usará para los despliegues."
}
