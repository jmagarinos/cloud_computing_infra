#!/bin/bash

# Directorio base
BASE_DIR="resources/lambda"

# Función para empaquetar una Lambda
package_lambda() {
    LAMBDA_DIR="$1"
    echo "Empaquetando $LAMBDA_DIR..."
    
    # Entrar al directorio de la Lambda
    cd "$BASE_DIR/$LAMBDA_DIR"
    
    # Instalar dependencias
    npm install --production
    
    # Crear el archivo ZIP
    zip -r "../${LAMBDA_DIR}.zip" ./*
    
    # Volver al directorio raíz
    cd ../../..
    
    echo "Lambda $LAMBDA_DIR empaquetada con éxito"
}

# Crear directorio lambda si no existe
mkdir -p "$BASE_DIR"

# Empaquetar cada Lambda
package_lambda "process_image_high_res"
package_lambda "process_image_low_res"

echo "Todas las Lambdas han sido empaquetadas con éxito" 