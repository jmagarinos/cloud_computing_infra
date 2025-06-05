import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda DELETE iniciada")
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
        
        print(f"Email autenticado: {email}")

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
        
        if not vianda_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': 'Se requiere el ID de la vianda'
                })
            }
        
        print(f"Vianda a eliminar: id = {vianda_id}")
        
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
        
        # Buscar el ID de la persona por email
        print(f"Buscando persona con cognito_sub: {cognito_sub}")
        cur.execute("SELECT id FROM persona WHERE cognito_sub = %s", (cognito_sub,))
        result = cur.fetchone()
        
        if not result:
            raise Exception("No se encontró la persona con ese email")
        
        persona_id = result[0]
        print(f"Persona encontrada: id = {persona_id}")
        
        # Verificar si la vianda existe y pertenece al usuario
        print("Verificando propiedad de la vianda")
        cur.execute("SELECT fk_dueno FROM vianda WHERE id = %s", (vianda_id,))
        result = cur.fetchone()
        
        if not result:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Vianda no encontrada'
                })
            }
        
        if result[0] != persona_id:
            return {
                'statusCode': 403,
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'Solo puedes eliminar tus propias viandas'
                })
            }
        
        # Eliminar la vianda
        print("Eliminando vianda")
        cur.execute("DELETE FROM vianda WHERE id = %s", (vianda_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Vianda {vianda_id} eliminada correctamente")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vianda eliminada correctamente'
            })
        }
        
    except Exception as e:
        print(f"Error en la Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al eliminar la vianda',
                'detalles': str(e)
            })
        }
