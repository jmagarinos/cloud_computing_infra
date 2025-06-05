variable "vpc_cidr" {
  description = "CIDR block de la VPC"
  type        = string
}

variable "environment" {
  description = "Environment (dev, test, prod)"
  type        = string
}
