output "certificate_arn" { value = aws_acm_certificate.api_cert.arn }
output "certificate_validation_name" {
  value = tolist(aws_acm_certificate.api_cert.domain_validation_options)[0].resource_record_name
}
output "certificate_validation_value" {
  value = tolist(aws_acm_certificate.api_cert.domain_validation_options)[0].resource_record_value
}
