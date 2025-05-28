variable "aws_region" {
  description = "Región de AWS"
  type        = string
  default     = "us-east-1"
}

variable "my_ip" {
  description = "Tu IP pública para acceso SSH y HTTP"
  type        = string
}

variable "project_name" {
  description = "Nombre base para los recursos"
  type        = string
}
