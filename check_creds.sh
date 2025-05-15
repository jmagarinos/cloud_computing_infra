#!/bin/bash

echo "🔍 Verificando credenciales de AWS..."

# Ejecutamos un comando simple para validar la sesión
aws sts get-caller-identity --output text >/dev/null 2>&1

# Evaluamos el resultado
if [ $? -eq 0 ]; then
    echo "✅ Credenciales activas. Todo listo para usar Terraform."
else
    echo "❌ Credenciales inválidas o vencidas."
    echo ""
    echo "👉 Si estás usando AWS Academy:"
    echo "   1. Andá al portal de AWS Academy."
    echo "   2. Copiá las líneas de credenciales temporales (Access Key, Secret Key, Session Token)."
    echo "   3. Ejecutá los 'export' nuevamente o usá el script 'export_aws_credentials.sh'."
    echo ""
    echo "🛑 Terraform no funcionará hasta que esto se arregle."
    exit 1
fi
