# modules/vpc/outputs.tf

output "vpc_id" {
  value = aws_vpc.main.id
}
