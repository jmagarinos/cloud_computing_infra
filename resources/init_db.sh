#!/bin/bash

# Verificar que tenemos las credenciales de AWS configuradas
if ! aws sts get-caller-identity &>/dev/null; then
    echo "Error: No se encontraron credenciales de AWS válidas"
    echo "Por favor, ejecuta 'aws configure' primero"
    exit 1
fi

# Obtener el endpoint de RDS
DB_IDENTIFIER="lunchbox-postgres"
REGION="us-east-1"

echo "Creando token de autenticación temporal para RDS..."
TOKEN=$(aws rds generate-db-auth-token \
    --hostname $DB_IDENTIFIER.ctojwthmht1z.$REGION.rds.amazonaws.com \
    --port 5432 \
    --region $REGION \
    --username postgres_user)

# Exportar las variables para psql
export PGPASSWORD=$TOKEN
export PGHOST=$DB_IDENTIFIER.ctojwthmht1z.$REGION.rds.amazonaws.com
export PGPORT=5432
export PGUSER=postgres_user
export PGDATABASE=lunchbox

echo "Intentando conectar a la base de datos..."
psql -f db_init.sql

if [ $? -eq 0 ]; then
    echo "Base de datos inicializada correctamente"
else
    echo "Error al inicializar la base de datos"
    echo "Verifica que:"
    echo "1. Las credenciales de AWS estén configuradas correctamente"
    echo "2. La base de datos exista y esté disponible"
    echo "3. PostgreSQL esté instalado en tu sistema (ejecuta: sudo apt-get install postgresql-client)"
fi 