resource "aws_acm_certificate" "api_cert" {
  domain_name       = var.custom_domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "api_cert_validation" {
  certificate_arn = aws_acm_certificate.api_cert.arn
}
