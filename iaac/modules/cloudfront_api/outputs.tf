output "distribution_id" {
  value = aws_cloudfront_distribution.api.id
}

output "distribution_domain_name" {
  value = aws_cloudfront_distribution.api.domain_name
}

output "distribution_hosted_zone_id" {
  value = aws_cloudfront_distribution.api.hosted_zone_id
}