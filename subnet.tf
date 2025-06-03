resource "aws_subnet" "private" {
  for_each = var.private_subnet_cidrs

  vpc_id                  = module.vpc.vpc_id
  cidr_block              = each.value
  availability_zone       = each.key
  map_public_ip_on_launch = false

  tags = {
    Name = format("private-subnet-%s-%s", each.key, var.environment)
  }
}

resource "aws_db_subnet_group" "rds" {
  name = format("rds-subnet-group-%s", var.environment)

  subnet_ids = [for subnet in aws_subnet.private : subnet.id]

  tags = {
    Name = format("rds-subnet-group-%s", var.environment)
  }
}
