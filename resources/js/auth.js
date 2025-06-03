const poolData = {
    UserPoolId: 'us-east-1_JosgMkDGE',  // User Pool ID de Cognito
    ClientId: '4femhf9urmn6vfu07k19jdod5a' // Client ID de Cognito
};

const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);

// Función para verificar si el usuario está autenticado
function isAuthenticated() {
    return localStorage.getItem('access_token') !== null;
}

// Función para actualizar el header según el estado de autenticación
function updateHeader() {
    const headerRight = document.querySelector('.header-right');
    if (!headerRight) return;

    if (isAuthenticated()) {
        headerRight.innerHTML = `
            <a href="profile.html" class="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                    <span class="text-sm font-medium" id="headerInitials"></span>
                </div>
                <span class="font-medium">Mi Perfil</span>
            </a>
        `;

        // Obtener y mostrar las iniciales del usuario
        const user = userPool.getCurrentUser();
        if (user) {
            user.getUserAttributes((err, attributes) => {
                if (!err && attributes) {
                    const email = attributes.find(attr => attr.getName() === 'email').getValue();
                    const initials = email.charAt(0).toUpperCase();
                    document.getElementById('headerInitials').textContent = initials;
                }
            });
        }
    } else {
        headerRight.innerHTML = `
            <a href="login.html" class="bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200">
                Iniciar Sesión
            </a>
        `;
    }
}

// Actualizar el header cuando se carga la página
document.addEventListener('DOMContentLoaded', updateHeader); 