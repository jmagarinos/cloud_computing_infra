import json
import os
from unittest import result
import psycopg2
from datetime import datetime
import jwt
from urllib.request import urlopen

def get_cognito_user_id(event):
    try:
        print("Lambda CREATE iniciada")
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
        
        # Parsear el body recibido en el POST
        body = json.loads(event.get('body', '{}'))
        vianda_id = body.get('vianda_id')
        
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
        
        # Verificar si la vianda existe y está disponible
        cur.execute("SELECT disponible FROM viandas WHERE id = %s", (vianda_id,))
        result = cur.fetchone()
        
        if not result:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Vianda no encontrada'
                })
            }
            
        if not result[0]:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'La vianda no está disponible'
                })
            }
        
        # Registrar la compra
        fecha_compra = datetime.now()
        insert_query = """
            INSERT INTO compras (vianda_id, comprador_id, fecha_compra)
            VALUES (%s, %s, %s)
            RETURNING id;
        """
        
        cur.execute(insert_query, (vianda_id, user_id, fecha_compra))
        compra_id = cur.fetchone()[0]
        
        # Marcar la vianda como no disponible
        cur.execute("UPDATE viandas SET disponible = false WHERE id = %s", (vianda_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Compra realizada correctamente',
                'compra_id': compra_id,
                'fecha_compra': fecha_compra.isoformat()
            })
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al procesar la compra',
                'detalles': str(e)
            })
        }
