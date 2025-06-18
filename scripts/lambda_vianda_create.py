import json
import os
import psycopg2
import boto3

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

        # --- Extraer contexto de autorización ---
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        jwt_info = authorizer.get('jwt', {})
        claims = jwt_info.get('claims', {})

        cognito_sub = claims.get('sub')
        email = claims.get('email')

        if not cognito_sub:
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

        # --- Parsear body y validar datos ---
        body = json.loads(event.get('body', '{}'))
        validation_errors = validate_vianda_data(body)
        if validation_errors:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': validation_errors
                })
            }

        # --- Conexión a la base de datos ---
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        cur = conn.cursor()

        # Obtener persona ID
        cur.execute("SELECT id FROM persona WHERE cognito_sub = %s", (cognito_sub,))
        result = cur.fetchone()
        if not result:
            raise Exception("No se encontró la persona con ese sub")

        persona_id = result[0]

        # Insertar vianda
        insert_query = """
            INSERT INTO vianda (
                titulo, descripcion, precio, imagen, fk_dueno
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """
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

        # --- Publicar evento en SNS ---
        try:
            topic_arn = os.environ.get("SNS_EVENTOS_ARN")
            if not topic_arn:
                raise Exception("SNS_EVENTOS_ARN no definido en variables de entorno")

            sns = boto3.client("sns")
            response = sns.publish(
                TopicArn=topic_arn,
                Message=json.dumps({
                    "tipo_evento": "creacion_vianda",
                    "usuario_id": persona_id,
                    "vianda_id": vianda_id
                })
            )
            print("Publicación en SNS exitosa:", response)
        except Exception as e:
            print("Error publicando en SNS:", str(e))
            return {
                'statusCode': 500,
                'body': json.dumps({
                    "error": "Error al publicar en SNS",
                    "detalles": str(e)
                })
            }

        # --- Respuesta final ---
        return {
            'statusCode': 200,
            'body': json.dumps({
                "message": "Vianda creada y evento registrado",
                "vianda_id": vianda_id
            })
        }

    except Exception as e:
        print("Error general en Lambda:", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al crear la vianda',
                'detalles': str(e)
            })
        }
