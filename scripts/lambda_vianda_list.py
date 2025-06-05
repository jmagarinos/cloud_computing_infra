import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda LIST iniciada")
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
        
        # Obtener todas las viandas disponibles
        query = """
            SELECT v.id, v.titulo, v.descripcion, v.precio, v.imagen, v.disponible,
                   p.nombre as creador_nombre, p.apellido as creador_apellido
            FROM vianda v
            JOIN persona p ON v.fk_dueno = p.id
            WHERE v.disponible = true
            ORDER BY v.id DESC
        """
        
        print("Ejecutando query de viandas disponibles")
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
        
        print(f"Se encontraron {len(viandas_list)} viandas disponibles")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'viandas': viandas_list
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
                'error': 'Error al obtener las viandas',
                'detalles': str(e)
            })
        }
