resource "aws_acm_certificate" "cf_cert" {
  provider          = aws.us_east_1
  domain_name       = var.custom_domain_name
  validation_method = "DNS"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_acm_certificate_validation" "cf_cert_validation" {
  provider        = aws.us_east_1
  certificate_arn = aws_acm_certificate.cf_cert.arn
}