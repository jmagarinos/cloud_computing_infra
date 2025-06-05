import json
import os
import psycopg2

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
        
        # Parsear el body recibido en el POST
        body = json.loads(event.get('body', '{}'))
        print(f"Body recibido: {body}")
        
        # Validar los datos
        validation_errors = validate_vianda_data(body)
        if validation_errors:
            print(f"Errores de validación: {validation_errors}")
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': validation_errors
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
        
        # Buscar el ID de la persona por email
        print(f"Buscando persona con email: {email}")
        cur.execute("SELECT id FROM persona WHERE cognito_sub = %s", (cognito_sub,))
        result = cur.fetchone()
        
        if not result:
            raise Exception("No se encontró la persona con ese email")
        
        persona_id = result[0]
        print(f"Persona encontrada: id = {persona_id}")
        
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
        
        print("Insertando vianda")
        cur.execute(insert_query, (
            body['titulo'],
            body['descripcion'],
            body['precio'],
            body.get('imagen'),
            persona_id
        ))
        
        vianda_id = cur.fetchone()[0]
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Vianda creada correctamente con id = {vianda_id}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vianda creada correctamente',
                'id': vianda_id
            })
        }
        
    except Exception as e:
        print(f"Error en la Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al crear la vianda',
                'detalles': str(e)
            })
        }
