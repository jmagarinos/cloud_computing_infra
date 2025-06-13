// Configuración de Cognito
const cognitoConfig = {
    userPoolId: '${aws_cognito_user_pool.main.id}',
    clientId: '${aws_cognito_user_pool_client.web_client.id}'
};


// Configuración de la API
const apiConfig = {
    apiUrl: 'https://o91hot3cr7.execute-api.us-east-1.amazonaws.com/dev'
};


