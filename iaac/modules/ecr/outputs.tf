output "repository_url" {
  value = aws_ecr_repository.repo.repository_url
}

output "image_uri" {
  value = "${aws_ecr_repository.repo.repository_url}:latest"
}
