// Clase principal para manejar las llamadas a la API
class LunchBoxAPI {
    constructor(baseUrl) {
        if (baseUrl.endsWith('/')) {
            this.baseUrl = baseUrl.slice(0, -1);
        } else {
            this.baseUrl = baseUrl;
        }
    }

    // Obtener el token de autenticación
    getAuthToken() {
        return localStorage.getItem('access_token');
    }

    // Headers comunes para las peticiones autenticadas
    getAuthHeaders() {
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${this.getAuthToken()}`
        };
    }

    // Manejo de errores común
    handleError(error) {
        console.error('Error en la API:', error);
        throw error;
    }

    // ENDPOINTS DE VIANDAS

    // Obtener todas las viandas
    async getViandas() {
        try {
            const response = await fetch(`${this.baseUrl}/viandas`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok){
                console.log('response:', response);
                throw new Error(`HTTP error! status: ${response.status}`);
            } 
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Obtener una vianda específica
    async getVianda(id) {
        try {
            const response = await fetch(`${this.baseUrl}/viandas/${id}`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Crear una nueva vianda
    async createVianda(viandaData) {
        try {
            const response = await fetch(`${this.baseUrl}/viandas`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(viandaData)
            });
            
            if (!response.ok){
                console.log('response:', response);
                throw new Error(`HTTP error! status: ${response.status}`);
            } 
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Actualizar una vianda existente
    async updateVianda(id, viandaData) {
        try {
            const response = await fetch(`${this.baseUrl}/viandas/${id}`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(viandaData)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Eliminar una vianda
    async deleteVianda(id) {
        try {
            const response = await fetch(`${this.baseUrl}/viandas/${id}`, {
                method: 'DELETE',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // ENDPOINTS DE COMPRAS

    // Realizar una compra
    async comprarVianda(compraData) {
        try {
            const response = await fetch(`${this.baseUrl}/ventas`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(compraData)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Obtener historial de compras del usuario
    async getComprasUsuario() {
        try {
            const response = await fetch(`${this.baseUrl}/ventas/usuario`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // ENDPOINTS DE PERFIL

    // Obtener perfil del usuario
    async getPerfilUsuario() {
        try {
            const response = await fetch(`${this.baseUrl}/perfil`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Actualizar perfil del usuario
    async updatePerfilUsuario(perfilData) {
        try {
            const response = await fetch(`${this.baseUrl}/perfil`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(perfilData)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // ENDPOINTS DE BÚSQUEDA

    // Buscar viandas por criterios
    async buscarViandas(criterios) {
        try {
            const queryParams = new URLSearchParams(criterios).toString();
            const response = await fetch(`${this.baseUrl}/viandas/buscar?${queryParams}`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }
}

// Exportar la clase para su uso
export const api = new LunchBoxAPI(apiConfig.apiUrl);