import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda PROFILE iniciada")
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
            SELECT id, nombre, apellido, mail, telefono, direccion 
            FROM persona 
            WHERE cognito_sub = %s
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
        
        user_id, nombre, apellido, db_email, telefono, direccion = user_info
        print(f"Usuario encontrado: {nombre} {apellido} ({db_email})")
        
        # Obtener estadísticas del usuario
        stats_query = """
            SELECT 
                COUNT(v.id) as total_compras,
                COALESCE(SUM(vi.precio * v.cantidad), 0) as total_gastado
            FROM ventas v
            JOIN vianda vi ON v.fk_vianda = vi.id
            WHERE v.fk_persona = %s
        """
        
        cur.execute(stats_query, (user_id,))
        stats_result = cur.fetchone()
        
        total_compras = stats_result[0] if stats_result[0] else 0
        total_gastado = float(stats_result[1]) if stats_result[1] else 0.0
        
        print(f"Estadísticas del usuario: {total_compras} compras, ${total_gastado} gastado")
        
        cur.close()
        conn.close()
        
        # Construir respuesta del perfil
        profile_data = {
            'id': user_id,
            'nombre': nombre,
            'apellido': apellido,
            'email': db_email,
            'telefono': telefono,
            'direccion': direccion,
            'estadisticas': {
                'totalCompras': total_compras,
                'totalGastado': total_gastado
            }
        }
        
        print(f"Perfil del usuario: {json.dumps(profile_data, indent=2)}")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'perfil': profile_data
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
                'error': 'Error al obtener el perfil',
                'detalles': str(e)
            })
        } 