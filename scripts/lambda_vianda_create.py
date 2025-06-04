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
        print("Lambda iniciada")
        
        # Obtener email del usuario autenticado
        claims = event['requestContext']['authorizer']['claims']
        email = claims.get('email')
        
        if not email:
            print("No se encontró el email en claims")
            return {
                'statusCode': 401,
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'No se encontró el email en el token'
                })
            }
        
        print(f"Email autenticado: {email}")
        
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
        cur.execute("SELECT id FROM persona WHERE mail = %s", (email,))
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
