import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda TOGGLE DISPONIBILIDAD iniciada")
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
        
        if not cognito_sub:
            print("No se encontró el cognito_sub en claims")
            return {
                'statusCode': 401,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'No se encontró el cognito_sub en el token'
                })
            }
        
        # Obtener el ID de la vianda de los parámetros de la URL
        vianda_id = event.get('pathParameters', {}).get('id')
        print(f"ID de vianda solicitada: {vianda_id}")
        
        if not vianda_id:
            print("Error: No se proporcionó ID de vianda")
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': 'Se requiere el ID de la vianda'
                })
            }
        
        # Conexión a la base de datos
        print("Conectando a la base de datos")
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        
        cur = conn.cursor()
        
        # Get user info from database
        user_query = """
            SELECT id FROM persona WHERE cognito_sub = %s
        """
        cur.execute(user_query, (cognito_sub,))
        user_info = cur.fetchone()
        
        if not user_info:
            print(f"No se encontró el usuario con cognito_sub: {cognito_sub}")
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'error': 'Usuario no encontrado',
                    'detalles': 'No se encontró el usuario en la base de datos'
                })
            }
        
        user_id = user_info[0]
        print(f"Usuario encontrado: id = {user_id}")
        
        # Verificar si la vianda existe y pertenece al usuario
        print("Verificando propiedad de la vianda")
        cur.execute("SELECT disponible FROM vianda WHERE id = %s AND fk_dueno = %s", (vianda_id, user_id))
        result = cur.fetchone()
        
        if not result:
            return {
                'statusCode': 404,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'error': 'Vianda no encontrada o no tienes permiso para modificarla'
                })
            }
        
        # Cambiar la disponibilidad
        nueva_disponibilidad = not result[0]
        print(f"Cambiando disponibilidad a: {nueva_disponibilidad}")
        
        cur.execute("UPDATE vianda SET disponible = %s WHERE id = %s", (nueva_disponibilidad, vianda_id))
        conn.commit()
        
        cur.close()
        conn.close()
        
        print("Disponibilidad actualizada correctamente")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'message': 'Disponibilidad actualizada correctamente',
                'disponible': nueva_disponibilidad
            })
        }
        
    except Exception as e:
        print(f"Error en la Lambda: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'error': 'Error al cambiar la disponibilidad',
                'detalles': str(e)
            })
        } 