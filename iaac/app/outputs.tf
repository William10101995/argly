output "api_url" {
  description = "URL base del API Gateway"
  value       = module.apigateway.api_endpoint
}

output "ecr_repository_url" {
  description = "URL del repositorio ECR para subir la imagen de Docker"
  value       = module.ecr.repository_url
}

output "lambda_function_name" {
  description = "Nombre de la funcion Lambda"
  value       = module.lambda.function_name
}

output "lambda_function_arn" {
  description = "ARN de la funcion Lambda"
  value       = module.lambda.function_arn
}

output "custom_domain_target" {
  description = "El valor CNAME que debes poner en tu DNS para api.argly.com.ar"
  value       = module.apigateway.custom_domain_target
}

output "cert_validation_name" {
  description = "DNS Nombre para validar el certificado ACM"
  value       = module.acm.certificate_validation_name
}

output "cert_validation_value" {
  description = "DNS Valor para validar el certificado ACM"
  value       = module.acm.certificate_validation_value
}

output "cloudfront_distribution_domain" {
  description = "Dominio de CloudFront - usar para pruebas previas y para el corte de DNS"
  value       = module.cloudfront_api.distribution_domain_name
}

output "cert_validation_name_cloudfront" {
  value = module.acm_cloudfront.certificate_validation_name
}

output "cert_validation_value_cloudfront" {
  value = module.acm_cloudfront.certificate_validation_value
}