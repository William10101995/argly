resource "aws_cloudfront_distribution" "api" {
  enabled = true
  comment = "${var.project_name} - API distribution (geo-IP + custom domain)"
  aliases = [var.custom_domain_name]

  origin {
    domain_name = var.apigw_domain_name
    origin_id   = "argly-api-gateway"

    custom_origin_config {
      http_port                 = 80
      https_port                = 443
      origin_protocol_policy    = "https-only"
      origin_ssl_protocols      = ["TLSv1.2"]
      origin_read_timeout       = 30
      origin_keepalive_timeout  = 5
    }
  }

  default_cache_behavior {
    target_origin_id       = "argly-api-gateway"
    viewer_protocol_policy = "redirect-to-https"

    allowed_methods = ["GET", "HEAD", "OPTIONS", "PUT", "POST", "PATCH", "DELETE"]
    cached_methods  = ["GET", "HEAD"]

    cache_policy_id          = "4135ea2d-6df8-44a3-9df3-4b5a84be39ad" # CachingDisabled
    origin_request_policy_id = "33f36d7e-f396-46d9-90e0-52428a34d9dc" # AllViewerExceptHostHeader

    compress = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2021"
  }

  price_class = var.price_class
}