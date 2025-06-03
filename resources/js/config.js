// Configuración de Cognito
const cognitoConfig = {
    userPoolId: '${aws_cognito_user_pool.main.id}',
    clientId: '${aws_cognito_user_pool_client.web_client.id}'
}; 