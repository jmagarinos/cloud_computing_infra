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
            console.log('Llamando a getVianda con ID:', id);
            console.log('URL:', `${this.baseUrl}/viandas/${id}`);
            console.log('Headers:', this.getAuthHeaders());
            
            const response = await fetch(`${this.baseUrl}/viandas/${id}`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            console.log('Respuesta recibida:', response);
            if (!response.ok) {
                const errorText = await response.text();
                console.error('Error response:', errorText);
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const data = await response.json();
            console.log('Datos recibidos:', data);
            return data;
        } catch (error) {
            console.error('Error en getVianda:', error);
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

    // Cambiar disponibilidad de una vianda
    async toggleDisponibilidad(id) {
        const response = await fetch(`${this.baseUrl}/viandas/${id}/disponibilidad`, {
            method: 'PUT',
            headers: this.getAuthHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al cambiar disponibilidad');
        }
        return await response.json();
    }

    async eliminarVianda(id) {
        const response = await fetch(`${this.baseUrl}/viandas/${id}`, {
            method: 'DELETE',
            headers: this.getAuthHeaders()
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Error al eliminar la vianda');
        }
        return await response.json();
    }

    // ENDPOINTS DE COMPRAS

    // Realizar una compra
    async comprarVianda(compraData) {
        try {
            const response = await fetch(`${this.baseUrl}/comprar`, {
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
    async getUserProfile() {
        try {
            const response = await fetch(`${this.baseUrl}/perfil`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.perfil; // Devolver directamente el objeto perfil
        } catch (error) {
            this.handleError(error);
        }
    }

    // Obtener estadísticas del usuario (ahora incluidas en getUserProfile)
    async getUserStats() {
        try {
            const profile = await this.getUserProfile();
            return profile.estadisticas;
        } catch (error) {
            this.handleError(error);
            // Si hay error, devolvemos valores por defecto
            return {
                totalCompras: 0,
                totalGastado: 0
            };
        }
    }

    // Actualizar perfil del usuario
    async updateUserProfile(perfilData) {
        try {
            const response = await fetch(`${this.baseUrl}/perfil`, {
                method: 'PUT',
                headers: this.getAuthHeaders(),
                body: JSON.stringify(perfilData)
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            const data = await response.json();
            return data.perfil; // Devolver el perfil actualizado
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

    // Obtener las viandas publicadas por el usuario autenticado
    async getMisViandas() {
        try {
            const response = await fetch(`${this.baseUrl}/viandas/usuario`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Obtener las compras realizadas por el usuario
    async getMisCompras() {
        try {
            const response = await fetch(`${this.baseUrl}/compras/usuario`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            console.log('response:', response);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }

    // Obtener las ventas realizadas por el usuario
    async getMisVentas() {
        try {
            const response = await fetch(`${this.baseUrl}/ventas/usuario`, {
                method: 'GET',
                headers: this.getAuthHeaders()
            });
            console.log('response:', response);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return await response.json();
        } catch (error) {
            this.handleError(error);
        }
    }
}

// Crear una instancia de la API con la URL base de la configuración
const api = new LunchBoxAPI(apiConfig.apiUrl);

// Exportar la instancia
export { api };