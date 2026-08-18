variable "project_name" {
  type = string
}

variable "custom_domain_name" {
  type = string
}

variable "apigw_domain_name" {
  type        = string
  description = "Hostname del endpoint default de API Gateway, SIN https:// (ej: xxxx.execute-api.sa-east-1.amazonaws.com)"
}

variable "certificate_arn" {
  type        = string
  description = "ARN del certificado ACM en us-east-1 (obligatorio para CloudFront)"
}

variable "price_class" {
  type    = string
  default = "PriceClass_100"
}