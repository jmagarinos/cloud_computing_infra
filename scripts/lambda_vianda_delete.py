import json
import os
import psycopg2
import jwt
from urllib.request import urlopen

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

def get_cors_headers():
    """Return CORS headers for all responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

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
        
        # Obtener el ID de la vianda de los parámetros de la URL
        vianda_id = event.get('pathParameters', {}).get('id')
        
        if not vianda_id:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': 'Se requiere el ID de la vianda'
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
        
        # Verificar si la vianda existe y pertenece al usuario
        cur.execute("SELECT creador_id FROM viandas WHERE id = %s", (vianda_id,))
        result = cur.fetchone()
        
        if not result:
            return {
                'statusCode': 404,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Vianda no encontrada'
                })
            }
            
        if result[0] != user_id:
            return {
                'statusCode': 403,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'Solo puedes eliminar tus propias viandas'
                })
            }
        
        # Eliminar la vianda
        cur.execute("DELETE FROM viandas WHERE id = %s", (vianda_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Vianda eliminada correctamente'
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Error al eliminar la vianda',
                'detalles': str(e)
            })
        }
