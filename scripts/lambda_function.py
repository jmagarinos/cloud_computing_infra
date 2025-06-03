import json
import os
import psycopg2
from datetime import datetime
import jwt
from urllib.request import urlopen

def get_cognito_user_id(event):
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
        
        return payload.get('sub')  # 'sub' es el ID único del usuario en Cognito
        
    except Exception as e:
        print(f"Error al obtener el ID de usuario: {str(e)}")
        return None

def validate_vianda_data(data):
    required_fields = {
        'nombre': str,
        'descripcion': str,
        'precio': (int, float),
        'categoria': str,
        'ingredientes': list,
        'calorias': int,
        'tiempo_preparacion': int,
        'disponible': bool
    }
    
    errors = []
    
    for field, field_type in required_fields.items():
        if field not in data:
            errors.append(f"El campo {field} es obligatorio")
        elif not isinstance(data[field], field_type):
            errors.append(f"El campo {field} debe ser de tipo {field_type.__name__}")
    
    if data.get('precio') is not None and data['precio'] <= 0:
        errors.append("El precio debe ser mayor que 0")
    
    if data.get('calorias') is not None and data['calorias'] <= 0:
        errors.append("Las calorías deben ser mayores que 0")
    
    if data.get('tiempo_preparacion') is not None and data['tiempo_preparacion'] <= 0:
        errors.append("El tiempo de preparación debe ser mayor que 0")
    
    return errors

def lambda_handler(event, context):
    try:
        # Verificar autenticación
        user_id = get_cognito_user_id(event)
        if not user_id:
            return {
                'statusCode': 401,
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
        fecha_creacion = datetime.now()
        
        insert_query = """
            INSERT INTO viandas (
                nombre, 
                descripcion, 
                precio, 
                categoria, 
                ingredientes, 
                calorias, 
                tiempo_preparacion, 
                disponible,
                fecha_creacion,
                creador_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        
        cur.execute(insert_query, (
            body['nombre'],
            body['descripcion'],
            body['precio'],
            body['categoria'],
            body['ingredientes'],
            body['calorias'],
            body['tiempo_preparacion'],
            body['disponible'],
            fecha_creacion,
            user_id  # Usamos el ID del usuario de Cognito
        ))
        
        vianda_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vianda creada correctamente',
                'id': vianda_id,
                'fecha_creacion': fecha_creacion.isoformat(),
                'creador_id': user_id
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al crear la vianda',
                'detalles': str(e)
            })
        }
