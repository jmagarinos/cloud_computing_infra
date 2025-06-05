import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda PROFILE UPDATE iniciada")
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
        
        # Obtener datos del cuerpo de la solicitud
        body = event.get('body', '{}')
        if isinstance(body, str):
            try:
                body_data = json.loads(body)
            except json.JSONDecodeError:
                print("Error decodificando el body JSON")
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'error': 'Datos inválidos',
                        'detalles': 'El cuerpo de la solicitud no es un JSON válido'
                    })
                }
        else:
            body_data = body
        
        print(f"Datos para actualizar: {json.dumps(body_data, indent=2)}")
        
        # Validar campos requeridos
        required_fields = ['nombre', 'apellido', 'telefono', 'direccion']
        for field in required_fields:
            if field not in body_data or not body_data[field]:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'error': 'Datos incompletos',
                        'detalles': f'El campo {field} es requerido'
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
        
        # Verificar que el usuario existe
        check_user_query = """
            SELECT id FROM persona WHERE cognito_sub = %s
        """
        cur.execute(check_user_query, (cognito_sub,))
        user_result = cur.fetchone()
        
        if not user_result:
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
        
        user_id = user_result[0]
        
        # Actualizar información del usuario
        update_query = """
            UPDATE persona 
            SET nombre = %s, apellido = %s, telefono = %s, direccion = %s
            WHERE cognito_sub = %s
        """
        
        cur.execute(update_query, (
            body_data['nombre'],
            body_data['apellido'],
            body_data['telefono'],
            body_data['direccion'],
            cognito_sub
        ))
        
        # Confirmar la transacción
        conn.commit()
        
        print(f"Usuario {user_id} actualizado exitosamente")
        
        # Obtener los datos actualizados para devolver
        get_updated_query = """
            SELECT id, nombre, apellido, mail, telefono, direccion 
            FROM persona 
            WHERE cognito_sub = %s
        """
        cur.execute(get_updated_query, (cognito_sub,))
        updated_user = cur.fetchone()
        
        cur.close()
        conn.close()
        
        if updated_user:
            user_id, nombre, apellido, db_email, telefono, direccion = updated_user
            
            updated_profile = {
                'id': user_id,
                'nombre': nombre,
                'apellido': apellido,
                'email': db_email,
                'telefono': telefono,
                'direccion': direccion
            }
            
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'mensaje': 'Perfil actualizado exitosamente',
                    'perfil': updated_profile
                })
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'error': 'Error interno',
                    'detalles': 'No se pudo recuperar los datos actualizados'
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
                'error': 'Error al actualizar el perfil',
                'detalles': str(e)
            })
        } 