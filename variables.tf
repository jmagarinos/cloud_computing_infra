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

variable "db_username" {
  description = "Master username for RDS"
  default     = "postgres_user"
}

variable "db_password" {
  description = "Master password for RDS"
  sensitive   = true
}

variable "private_subnet_cidr" {
  description = "CIDR block for the private subnet"
  default     = "10.0.1.0/24"
}

variable "availability_zone" {
  description = "AZ to launch resources in"
  default     = "us-east-1a"
}

variable "allowed_ingress_cidr" {
  description = "CIDR allowed to access RDS"
  default     = "0.0.0.0/0"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC"
  type        = string
}

variable "environment" {
  description = "Environment (dev, test, prod)"
  type        = string
}

variable "project_team" {
  description = "Project team name"
  type        = string
}

variable "private_subnet_cidrs" {
  description = "Map of AZs to private subnet CIDRs"
  type        = map(string)
}

variable "cognito_callback_url" {
  description = "Callback URL for Cognito Hosted UI"
  type        = string
}

variable "cognito_logout_url" {
  description = "Logout URL"
  type        = string
}

variable "public_subnet_cidr" {
  description = "CIDR block for public subnet"
  type        = string
}

variable "bastion_admin_ip" {
  description = "Dirección IP pública del administrador para acceso SSH"
  type        = string
  default     = "190.16.197.33/32" # podés cambiar el default si querés
}
