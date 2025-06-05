# -----------------------------
# Security group configuration
# -----------------------------

module "sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.1.0"

  name = format("rds-sg-%s", var.environment)

  vpc_id      = module.vpc.vpc_id
  description = "Security group created with module"

  ingress_with_cidr_blocks = [
    {
      from_port   = 5432
      to_port     = 5432
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  egress_with_cidr_blocks = [
    {
      from_port   = 0
      to_port     = 0
      protocol    = "-1"
      cidr_blocks = "0.0.0.0/0"
    }
  ]
}

# resource "aws_security_group" "rds_sg" {
#   name        = "rds-security-group"
#   description = "Allow access to RDS"
#   vpc_id      = module.vpc.vpc_id

#   ingress {
#     from_port   = 5432
#     to_port     = 5432
#     protocol    = "tcp"
#     cidr_blocks = [var.allowed_ingress_cidr]
#   }

#   egress {
#     from_port   = 0
#     to_port     = 0
#     protocol    = "-1"
#     cidr_blocks = ["0.0.0.0/0"]
#   }

#   tags = {
#     Name = "rds-sg"
#   }
# }
