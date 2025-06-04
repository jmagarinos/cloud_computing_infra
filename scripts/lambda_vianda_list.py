import json
import os
import psycopg2
import jwt
from urllib.request import urlopen

def get_cors_headers():
    """Return CORS headers for all responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

def get_cognito_user_id(event):
    try:
        auth_header = event.get('headers', {}).get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        region = os.environ.get('COGNITO_REGION', 'us-east-1')
        user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
        
        if not user_pool_id:
            raise Exception("COGNITO_USER_POOL_ID no está configurado")
            
        keys_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
        response = urlopen(keys_url)
        keys = json.loads(response.read())['keys']
        
        headers = jwt.get_unverified_header(token)
        key = next((k for k in keys if k['kid'] == headers['kid']), None)
        
        if not key:
            raise Exception("No se encontró la clave para verificar el token")
            
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        
        return payload.get('sub')
        
    except Exception as e:
        print(f"Error al obtener el ID de usuario: {str(e)}")
        return None

def lambda_handler(event, context):
    try:
        # Verificar autenticación
        user_id = get_cognito_user_id(event)
        if not user_id:
            return {
                'statusCode': 401,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'Se requiere autenticación'
                })
            }
        
        # Conexión a la base de datos
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        
        cur = conn.cursor()
        
        # Obtener todas las viandas disponibles
        query = """
            SELECT v.id, v.titulo, v.descripcion, v.precio, v.imagen, v.disponible,
                   p.nombre as creador_nombre, p.apellido as creador_apellido
            FROM viandas v
            JOIN persona p ON v.fk_dueno = p.id
            WHERE v.disponible = true
            ORDER BY v.id DESC
        """
        
        cur.execute(query)
        viandas = cur.fetchall()
        
        # Convertir los resultados a un formato JSON
        viandas_list = []
        for vianda in viandas:
            viandas_list.append({
                'id': vianda[0],
                'titulo': vianda[1],
                'descripcion': vianda[2],
                'precio': float(vianda[3]),
                'imagen': vianda[4],
                'disponible': vianda[5],
                'creador': {
                    'nombre': vianda[6],
                    'apellido': vianda[7]
                }
            })
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'viandas': viandas_list
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Error al obtener las viandas',
                'detalles': str(e)
            })
        } 