#!/bin/bash

# Crear directorio temporal para los archivos
mkdir -p temp_lambda

# Copiar los archivos Python al directorio temporal
cp lambda_vianda_buy.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_buy.zip lambda_function.py
cd ..

cp lambda_vianda_delete.py temp_lambda/lambda_function.py
cd temp_lambda
zip ../lambda_vianda_delete.zip lambda_function.py
cd ..

# Limpiar
rm -rf temp_lambda 