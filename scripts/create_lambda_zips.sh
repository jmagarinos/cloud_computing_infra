#!/bin/bash

# Crear directorio temporal para los archivos
mkdir -p temp_lambda

# Lista de lambdas
LAMBDAS=(
  lambda_vianda_buy
  lambda_rds_init
  lambda_vianda_create
  lambda_vianda_delete
  lambda_vianda_list
  lambda_vianda_get
  lambda_vianda_profile
  lambda_vianda_profile_update
  lambda_cognito_post_confirmation
  lambda_vianda_toggle_disponibilidad
)

for LAMBDA in "${LAMBDAS[@]}"; do
  if [ -f scripts/${LAMBDA}.py ]; then
    cp scripts/${LAMBDA}.py temp_lambda/${LAMBDA}.py
    cd temp_lambda
    zip ../scripts/${LAMBDA}.zip ${LAMBDA}.py
    cd ..
  else
    echo "No se encontró scripts/${LAMBDA}.py, se omite."
  fi
  rm -f temp_lambda/${LAMBDA}.py

done

# Limpiar
test -d temp_lambda && rm -rf temp_lambda 