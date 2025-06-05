# -----------------------------
# DB Admin Bastion
# -----------------------------
resource "aws_key_pair" "bastion_key" {
  key_name   = "bastion-key-${var.environment}"
  public_key = file("${path.module}/keys/bastion_key.pub")
}

resource "aws_security_group" "bastion_sg" {
  name        = "bastion-sg-${var.environment}"
  description = "Permitir SSH desde mi IP + acceso a RDS"
  vpc_id      = module.vpc.vpc_id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.bastion_admin_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "bastion-sg-${var.environment}"
  }
}

resource "aws_instance" "bastion" {
  ami                         = "ami-04b70fa74e45c3917"
  instance_type               = "t3.micro"
  subnet_id                   = aws_subnet.public.id
  vpc_security_group_ids      = [aws_security_group.bastion_sg.id]
  key_name                    = aws_key_pair.bastion_key.key_name
  associate_public_ip_address = true

  tags = {
    Name = "bastion-${var.environment}"
  }
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
