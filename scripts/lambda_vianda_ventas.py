import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda VENTAS iniciada")
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
        
        # Obtener todas las ventas del usuario
        query = """
            SELECT v.id, v.titulo, v.descripcion, v.precio, v.imagen, v.disponible,
                   p.nombre as comprador_nombre, p.apellido as comprador_apellido, p.mail as comprador_mail,
                   vta.fecha_venta, vta.cantidad,
                   CASE WHEN v.fk_dueno = %s THEN true ELSE false END as es_creador
            FROM ventas vta
            JOIN vianda v ON vta.fk_vianda = v.id
            JOIN persona p ON vta.fk_persona = p.id
            WHERE v.fk_dueno = %s
            ORDER BY vta.fecha_venta DESC
        """
        
        print("Ejecutando query de ventas")
        cur.execute(query, (user_id, user_id))
        ventas = cur.fetchall()
        
        # Convertir los resultados a un formato JSON
        ventas_list = []
        for venta in ventas:
            print("Venta row:", venta)
            ventas_list.append({
                'id': venta[0],
                'titulo': venta[1],
                'descripcion': venta[2],
                'precio': float(venta[3]),
                'imagen': venta[4],
                'disponible': venta[5],
                'comprador': {
                    'nombre': venta[6],
                    'apellido': venta[7],
                    'mail': venta[8]
                },
                'fecha_compra': venta[9].isoformat() if venta[9] else None,
                'cantidad': venta[10],
                'es_creador': venta[11]
            })
        
        cur.close()
        conn.close()
        
        print(f"Se encontraron {len(ventas_list)} ventas")
        
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Credentials': True
            },
            'body': json.dumps({
                'viandas': ventas_list
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
                'error': 'Error al obtener las ventas',
                'detalles': str(e)
            })
        } 