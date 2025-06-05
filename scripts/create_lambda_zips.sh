#!/bin/bash

# Crear directorio temporal para los archivos
mkdir -p temp_lambda

# Copiar los archivos Python al directorio temporal
cp lambda_vianda_buy.py temp_lambda/lambda_vianda_buy.py
cd temp_lambda
zip ../lambda_vianda_buy.zip lambda_vianda_buy.py
cd ..

cp lambda_rds_init.py temp_lambda/lambda_rds_init.py
cd temp_lambda
zip ../lambda_rds_init.zip lambda_rds_init.py
cd ..

cp lambda_vianda_create.py temp_lambda/lambda_vianda_create.py
cd temp_lambda
zip ../lambda_vianda_create.zip lambda_vianda_create.py
cd ..

cp lambda_vianda_delete.py temp_lambda/lambda_vianda_delete.py
cd temp_lambda
zip ../lambda_vianda_delete.zip lambda_vianda_delete.py
cd ..

cp lambda_vianda_list.py temp_lambda/lambda_vianda_list.py
cd temp_lambda
zip ../lambda_vianda_list.zip lambda_vianda_list.py
cd ..

cp lambda_vianda_get.py temp_lambda/lambda_vianda_get.py
cd temp_lambda
zip ../lambda_vianda_get.zip lambda_vianda_get.py
cd ..

cp lambda_vianda_profile.py temp_lambda/lambda_vianda_profile.py
cd temp_lambda
zip ../lambda_vianda_profile.zip lambda_vianda_profile.py
cd ..

cp lambda_vianda_profile_update.py temp_lambda/lambda_vianda_profile_update.py
cd temp_lambda
zip ../lambda_vianda_profile_update.zip lambda_vianda_profile_update.py
cd ..

cp lambda_cognito_post_confirmation.py temp_lambda/lambda_cognito_post_confirmation.py
cd temp_lambda
zip ../lambda_cognito_post_confirmation.zip lambda_cognito_post_confirmation.py
cd ..

# Limpiar
rm -rf temp_lambda 