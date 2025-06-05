import json
import os
import psycopg2
import jwt
from urllib.request import urlopen

def get_cognito_user_id(event):
    try:
        print(f"Evento recibido: {json.dumps(event, indent=2)}")
        
        # Verificar si tenemos el contexto de autorización
        request_context = event.get('requestContext', {})
        print(f"Request Context: {json.dumps(request_context, indent=2)}")
        
        authorizer = request_context.get('authorizer', {})
        print(f"Authorizer: {json.dumps(authorizer, indent=2)}")
        
        jwt_info = authorizer.get('jwt', {})
        print(f"JWT Info: {json.dumps(jwt_info, indent=2)}")
        
        claims = jwt_info.get('claims', {})
        print(f"Claims: {json.dumps(claims, indent=2)}")
        
        # Extract user information from claims
        cognito_sub = claims.get('sub')  # Cognito user ID
        username = claims.get('username')
        email = claims.get('email')
        
        print(f"Cognito Sub: {cognito_sub}")
        print(f"Username: {username}")
        print(f"Email: {email}")

        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        
        cur = conn.cursor()
        cur.execute("SELECT id FROM persona WHERE cognito_sub = %s", (cognito_sub,))
        result = cur.fetchone()
        cur.close()
        conn.close()

        return result[0] if result else None
        
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
        
        # Obtener los detalles de la vianda específica
        query = """
            SELECT v.id, v.titulo, v.descripcion, v.precio, v.imagen, v.disponible,
                   p.nombre as creador_nombre, p.apellido as creador_apellido,
                   p.mail as creador_email
            FROM viandas v
            JOIN persona p ON v.fk_dueno = p.id
            WHERE v.id = %s
        """
        
        cur.execute(query, (vianda_id,))
        vianda = cur.fetchone()
        
        if not vianda:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Vianda no encontrada'
                })
            }
        
        # Convertir el resultado a formato JSON
        vianda_data = {
            'id': vianda[0],
            'titulo': vianda[1],
            'descripcion': vianda[2],
            'precio': float(vianda[3]),
            'imagen': vianda[4],
            'disponible': vianda[5],
            'creador': {
                'nombre': vianda[6],
                'apellido': vianda[7],
                'email': vianda[8]
            }
        }
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps(vianda_data)
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al obtener la vianda',
                'detalles': str(e)
            })
        } 