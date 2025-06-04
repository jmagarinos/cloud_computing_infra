# Lunchbox - Backend & Infraestructura (Terraform + AWS Lambda + API Gateway + RDS + S3 + Cognito)

Este proyecto define y despliega la infraestructura backend completa para la app **Lunchbox**, que permite a usuarios:

✅ Registrarse y loguearse  
✅ Consultar y comprar viandas  
✅ Administrar viandas  
✅ Almacenar imágenes de viandas procesadas  
✅ Persistir datos en base de datos RDS (PostgreSQL)

---

## Infraestructura

La infraestructura se define completamente en **Terraform**.

### Componentes

- **VPC**, subredes, security groups
- **EC2** (opcional para tareas administrativas)
- **RDS (PostgreSQL)** para almacenar datos de usuarios y viandas
- **S3** para imágenes de viandas (originales + thumbnails)
- **Cognito** para autenticación y gestión de usuarios
- **API Gateway** para exponer las Lambdas vía HTTP
- **Lambdas** para lógica del backend
- **Static Website** (HTML/JS) para frontend

---

## Estructura del proyecto

code/
├── api_gateway.tf
├── cognito.tf
├── ec2.tf
├── internet_gateway.tf
├── lambda.tf
├── outputs.tf
├── provider.tf
├── rds.tf
├── s3.tf
├── scripts/                   # Lambdas y script para empaquetarlas
│   ├── lambda_vianda_create.py
│   ├── lambda_vianda_list.py
│   ├── lambda_vianda_get.py
│   ├── lambda_vianda_delete.py
│   ├── lambda_vianda_buy.py
│   ├── lambda_rds_init.py
│   ├── lambda_cognito_post_confirmation.py
│   ├── lambda_image_processor.py
│   └── create_lambda_zips.sh
├── layers/                    # Layers (psycopg2, PIL, jwt)
│   ├── psycopg2-layer.zip
│   ├── PIL_layer.zip
│   └── jwt_layer.zip
├── modules/
│   └── vpc/                   # Módulo para VPC
│       ├── main.tf
│       ├── outputs.tf
│       └── variables.tf
├── resources/                 # Archivos estáticos HTML + JS + SQL
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── profile.html
│   ├── mis-compras.html
│   ├── write_vianda.html
│   ├── vianda-detail.html
│   ├── error.html
│   ├── confirm.html
│   ├── db_init.sql
│   ├── init_db.sh
│   └── js/
│       ├── auth.js
│       ├── config.js
│       └── api.js
├── securitygroup.tf
├── subnet.tf
├── terraform.tfvars
├── variables.tf
├── versions.tf
└── Diagrama.jpeg              # Diagrama del proyecto

---

## 🚀 Lambdas

**Lógicas principales:**

- `lambda_vianda_create` → Crear nueva vianda
- `lambda_vianda_list` → Listar viandas disponibles
- `lambda_vianda_get` → Obtener detalle de vianda
- `lambda_vianda_delete` → Eliminar vianda
- `lambda_vianda_buy` → Realizar compra
- `lambda_rds_init` → Inicializar base de datos
- `lambda_cognito_post_confirmation` → Hook post-confirmación de usuario
- `lambda_image_processor` → Procesar imágenes y generar thumbnails

---

## 🌍 Frontend

El sitio web estático se encuentra en `resources/`:

- `index.html` → Home
- `login.html`, `signup.html` → Autenticación
- `profile.html`, `mis-compras.html` → Perfil de usuario
- `write_vianda.html` → Crear vianda
- `vianda-detail.html` → Detalle de vianda

JS en `resources/js/`:

- `auth.js`
- `config.js`
- `api.js`

---

## Base de datos

El schema de la base se encuentra en:

resources/db_init.sql

1️⃣ Configurar credenciales de AWS
Opcional: podés usar el script helper:

./check_creds.sh
O configurar con:

aws configure

2️⃣ Inicializar Terraform

terraform init

3️⃣ Planificar cambios

terraform plan

4️⃣ Aplicar cambios

terraform apply

5️⃣ Empaquetar Lambdas

./scripts/create_lambda_zips.sh

6️⃣ Subir ZIPs a Lambda
Una vez empaquetados, los ZIPs se encuentran en:

/scripts/*.zip
