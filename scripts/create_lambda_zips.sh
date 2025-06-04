#!/bin/bash

# Crear directorio temporal para los archivos
mkdir -p temp_lambda

# Copiar los archivos Python al directorio temporal
cp lambda_vianda_buy.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_buy.zip lambda_function.py
cd ..

cp lambda_rds_init.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_rds_init.zip lambda_function.py
cd ..

cp lambda_vianda_delete.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_delete.zip lambda_function.py
cd ..

cp lambda_vianda_list.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_list.zip lambda_function.py
cd ..

cp lambda_vianda_get.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_get.zip lambda_function.py
cd ..

cp lambda_vianda_create.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_create.zip lambda_function.py
cd ..

cp lambda_cognito_post_confirmation.py temp_lambda/lambda_cognito_post_confirmation.py
cd temp_lambda
zip ../lambda_cognito_post_confirmation.zip lambda_cognito_post_confirmation.py
cd ..

# Limpiar
rm -rf temp_lambda 