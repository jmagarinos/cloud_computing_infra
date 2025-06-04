import json
import os
import psycopg2
from datetime import datetime
import jwt
from urllib.request import urlopen

def get_cors_headers():
    """Return CORS headers for all responses"""
    return {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
    }

def get_persona_id(event):
    try:
        # Obtener el token del header de autorización
        auth_header = event.get('headers', {}).get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header.split(' ')[1]
        
        # Obtener las claves públicas de Cognito
        region = os.environ.get('COGNITO_REGION', 'us-east-1')
        user_pool_id = os.environ.get('COGNITO_USER_POOL_ID')
        
        if not user_pool_id:
            raise Exception("COGNITO_USER_POOL_ID no está configurado")
            
        keys_url = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}/.well-known/jwks.json'
        response = urlopen(keys_url)
        keys = json.loads(response.read())['keys']
        
        # Decodificar el token
        headers = jwt.get_unverified_header(token)
        key = next((k for k in keys if k['kid'] == headers['kid']), None)
        
        if not key:
            raise Exception("No se encontró la clave para verificar el token")
            
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(key))
        payload = jwt.decode(token, public_key, algorithms=['RS256'])
        
        # Obtener el email del token
        email = payload.get('email')
        if not email:
            raise Exception("No se encontró el email en el token")
            
        # Conectar a la base de datos
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        
        cur = conn.cursor()
        
        # Buscar el ID de la persona por email
        cur.execute("SELECT id FROM persona WHERE mail = %s", (email,))
        result = cur.fetchone()
        
        if not result:
            raise Exception("No se encontró la persona con ese email")
            
        persona_id = result[0]
        
        cur.close()
        conn.close()
        
        return persona_id
        
    except Exception as e:
        print(f"Error al obtener el ID de persona: {str(e)}")
        return None

def validate_vianda_data(data):
    required_fields = {
        'titulo': str,
        'descripcion': str,
        'precio': (int, float)
    }
    
    errors = []
    
    for field, field_type in required_fields.items():
        if field not in data:
            errors.append(f"El campo {field} es obligatorio")
        elif not isinstance(data[field], field_type):
            errors.append(f"El campo {field} debe ser de tipo {field_type.__name__}")
    
    if data.get('precio') is not None and data['precio'] <= 0:
        errors.append("El precio debe ser mayor que 0")
    
    return errors

def lambda_handler(event, context):
    try:
        # Verificar autenticación y obtener ID de persona
        persona_id = get_persona_id(event)
        if not persona_id:
            return {
                'statusCode': 401,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'Se requiere autenticación'
                })
            }
        
        # Parsear el body recibido en el POST
        body = json.loads(event.get('body', '{}'))
        
        # Validar los datos
        validation_errors = validate_vianda_data(body)
        if validation_errors:
            return {
                'statusCode': 400,
                'headers': get_cors_headers(),
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': validation_errors
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
        
        # Preparar los datos para la inserción
        insert_query = """
            INSERT INTO vianda (
                titulo, 
                descripcion, 
                precio, 
                imagen,
                fk_dueno
            )
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        cur.execute(insert_query, (
            body['titulo'],
            body['descripcion'],
            body['precio'],
            body.get('imagen'),
            persona_id  # Usamos el ID de la persona
        ))
        
        vianda_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'message': 'Vianda creada correctamente',
                'id': vianda_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': get_cors_headers(),
            'body': json.dumps({
                'error': 'Error al crear la vianda',
                'detalles': str(e)
            })
        }
