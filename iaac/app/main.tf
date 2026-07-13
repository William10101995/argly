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
}

module "apigateway" {
  source               = "../modules/apigateway"
  project_name         = var.project_name
  lambda_invoke_arn    = module.lambda.invoke_arn
  lambda_function_name = module.lambda.function_name
  custom_domain_name   = "api.argly.com.ar"
  certificate_arn      = module.acm.certificate_arn
  
  depends_on = [module.acm]
}
