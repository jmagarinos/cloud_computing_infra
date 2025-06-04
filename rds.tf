# -----------------------------
# Postgres configuration
# -----------------------------

resource "aws_db_instance" "postgres" {
  identifier                          = "lunchbox-postgres"
  engine                              = "postgres"
  instance_class                      = "db.t3.micro"
  allocated_storage                   = 20
  username                            = var.db_username
  password                            = var.db_password
  db_name                             = "lunchbox"
  db_subnet_group_name                = aws_db_subnet_group.rds.name
  vpc_security_group_ids              = [module.sg.security_group_id]
  depends_on                          = [module.sg]
  skip_final_snapshot                 = true
  publicly_accessible                 = false
  multi_az                            = false
  iam_database_authentication_enabled = true

  tags = {
    Name = format("rds-%s", var.environment)
  }
}


