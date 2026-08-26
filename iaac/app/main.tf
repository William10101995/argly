module "ecr" {
  source       = "../modules/ecr"
  project_name = var.project_name
  source_dir   = "${path.root}/../../"
}

module "acm" {
  source             = "../modules/acm"
  custom_domain_name = "api.argly.com.ar"
}

module "lambda" {
  source       = "../modules/lambda"
  project_name = var.project_name
  image_uri    = module.ecr.image_uri

  environment_variables = {
    SUPABASE_URL         = data.aws_ssm_parameter.supabase_url.value
    SUPABASE_SERVICE_KEY = data.aws_ssm_parameter.supabase_service_key.value
    FLASK_ENV            = "production"
    S3_DATA_BUCKET = "argly-data"
    S3_DATA_REGION = "us-east-1"
  }
}

module "apigateway" {
  source               = "../modules/apigateway"
  project_name         = var.project_name
  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.function_name
  custom_domain_name   = "api.argly.com.ar"
  certificate_arn      = module.acm.certificate_arn
  
  cors_allow_origins = [
    "https://argly.com.ar",
    "https://www.argly.com.ar",
    "http://localhost:3000"
  ]

  depends_on = [module.acm]
}

module "acm_cloudfront" {
  source             = "../modules/acm_cloudfront"
  custom_domain_name = "api.argly.com.ar"

  providers = {
    aws.us_east_1 = aws.us_east_1
  }
}

module "cloudfront_api" {
  source             = "../modules/cloudfront_api"
  project_name       = var.project_name
  custom_domain_name = "api.argly.com.ar"
  apigw_domain_name  = replace(module.apigateway.api_endpoint, "https://", "")
  certificate_arn    = module.acm_cloudfront.certificate_arn
}