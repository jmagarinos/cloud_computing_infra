# -----------------------------
# Output: TF Vars
# -----------------------------

my_ip = "203.0.113.25/32"

project_name = "miappweb"

db_username = "postgres_user"
db_password = "rds123456"

private_subnet_cidrs = {
  "us-east-1a" = "10.0.1.0/24"
  "us-east-1b" = "10.0.2.0/24"
}

cognito_callback_url = "https://lunchbox-dev-login.auth.us-east-1.amazoncognito.com/oauth2/idpresponse"

cognito_logout_url = "https://lunchbox-dev-login.auth.us-east-1.amazoncognito.com/logout"

environment  = "dev"
project_team = "dev"
vpc_cidr     = "10.0.0.0/16"

public_subnet_cidr = "10.0.10.0/24"
