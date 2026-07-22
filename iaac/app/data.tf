data "aws_ssm_parameter" "supabase_url" {
  name            = "/argly/supabase_url"
  with_decryption = true
}

data "aws_ssm_parameter" "supabase_service_key" {
  name            = "/argly/supabase_service_key"
  with_decryption = true
}