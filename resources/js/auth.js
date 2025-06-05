// Los valores de Cognito se cargarán dinámicamente desde Terraform
let poolData = {
    UserPoolId: '',  // Se llenará dinámicamente
    ClientId: ''     // Se llenará dinámicamente
};

let userPool = null;

// Función para inicializar Cognito con los valores correctos
function initCognito(userPoolId, clientId) {
    console.log('Inicializando Cognito con:', { userPoolId, clientId });
    if (!userPoolId || !clientId) {
        console.error('Error: userPoolId o clientId no están definidos');
        return;
    }
    poolData.UserPoolId = userPoolId;
    poolData.ClientId = clientId;
    userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
    console.log('UserPool inicializado:', userPool);
}

// Función para verificar si el usuario está autenticado
function isAuthenticated() {
    const token = localStorage.getItem('access_token');
    console.log('Token de acceso:', token ? 'Presente' : 'No presente');
    return token !== null;
}

// Función para cerrar sesión
function logout() {
    console.log('Cerrando sesión...');
    
    // Limpiar tokens del localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    
    // Si hay un usuario actual en Cognito, cerrar su sesión
    if (userPool) {
        const cognitoUser = userPool.getCurrentUser();
        if (cognitoUser) {
            console.log('Cerrando sesión de Cognito...');
            cognitoUser.signOut();
        }
    }
    
    console.log('Sesión cerrada exitosamente');
    
    // Redirigir a la página de login
    window.location.href = 'login.html';
}

// Función para actualizar el header según el estado de autenticación
function updateHeader() {
    console.log('Actualizando header...');
    const headerRight = document.querySelector('.header-right');
    if (!headerRight) {
        console.error('No se encontró el elemento header-right');
        return;
    }

    if (isAuthenticated()) {
        console.log('Usuario autenticado, mostrando perfil');
        headerRight.innerHTML = `
            <div class="flex items-center space-x-4">
                <a href="write_vianda.html" class="bg-green-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-green-700 transition duration-200">
                    Crear Vianda
                </a>
                <a href="profile.html" class="flex items-center space-x-2 text-blue-600 hover:text-blue-800">
                    <div class="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                        <span class="text-sm font-medium" id="headerInitials"></span>
                    </div>
                    <span class="font-medium">Mi Perfil</span>
                </a>
            </div>
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
        console.log('Usuario no autenticado, mostrando botón de login');
        headerRight.innerHTML = `
            <a href="login.html" class="bg-blue-600 text-white font-semibold py-2 px-4 rounded-lg hover:bg-blue-700 transition duration-200">
                Iniciar Sesión
            </a>
        `;
    }
}

// Inicializar Cognito cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM cargado, inicializando Cognito...');
    if (typeof cognitoConfig !== 'undefined') {
        console.log('Configuración de Cognito encontrada:', cognitoConfig);
        initCognito(cognitoConfig.userPoolId, cognitoConfig.clientId);
    } else {
        console.error('cognitoConfig no está definido');
    }
    updateHeader();
});

// Hacer la función logout accesible globalmente
window.logout = logout; 