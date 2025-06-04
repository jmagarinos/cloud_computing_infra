// Configuración de Cognito
const cognitoConfig = {
    userPoolId: '${aws_cognito_user_pool.main.id}',
    clientId: '${aws_cognito_user_pool_client.web_client.id}'
};


// Configuración de la API

const apiConfig = {
    apiUrl: 'https://95iocvra45.execute-api.us-east-1.amazonaws.com/dev'
};


