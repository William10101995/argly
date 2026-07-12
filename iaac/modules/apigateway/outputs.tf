output "api_endpoint" { value = aws_apigatewayv2_api.http_api.api_endpoint }
output "custom_domain_target" {
  value = aws_apigatewayv2_domain_name.custom_domain.domain_name_configuration[0].target_domain_name
}
