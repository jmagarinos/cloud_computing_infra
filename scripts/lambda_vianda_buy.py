import json
import os
import psycopg2
from datetime import datetime
import boto3

def lambda_handler(event, context):
    conn = None
    try:
        print("Lambda BUY iniciada")
        print(f"Evento recibido: {json.dumps(event, indent=2)}")

        # Verificar si tenemos el contexto de autorización
        request_context = event.get('requestContext', {})
        authorizer = request_context.get('authorizer', {})
        jwt_info = authorizer.get('jwt', {})
        claims = jwt_info.get('claims', {})

        # Extraer información del usuario
        cognito_sub = claims.get('sub')
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
        vianda_id = body.get('vianda_id')
        cantidad = body.get('cantidad', 1)  # Por defecto 1 si no se especifica

        if not vianda_id:
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

        if cantidad < 1:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': 'La cantidad debe ser mayor a 0'
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

        # Configurar autocommit antes de cualquier operación
        conn.autocommit = False

        cur = conn.cursor()

        # Obtener información del usuario
        user_query = """
            SELECT id FROM persona 
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

        user_id = user_info[0]
        print(f"Usuario encontrado: id = {user_id}")

        try:
            # Verificar si la vianda existe, está disponible y no es del mismo usuario
            cur.execute("""
                SELECT v.disponible, v.fk_dueno 
                FROM vianda v 
                WHERE v.id = %s
            """, (vianda_id,))
            result = cur.fetchone()

            if not result:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'error': 'Vianda no encontrada'
                    })
                }

            disponible, dueno_id = result

            if not disponible:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'error': 'La vianda no está disponible'
                    })
                }

            if dueno_id == user_id:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Access-Control-Allow-Credentials': True
                    },
                    'body': json.dumps({
                        'error': 'No puedes comprar tu propia vianda'
                    })
                }

            # Registrar la compra
            fecha_compra = datetime.now()
            insert_query = """
                INSERT INTO ventas (fk_vianda, fk_persona, cantidad, fecha_venta)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """

            cur.execute(insert_query, (vianda_id, user_id, cantidad, fecha_compra))
            compra_id = cur.fetchone()[0]

            # Confirmar transacción
            conn.commit()

            # Publicar evento SNS
            try:
                sns = boto3.client('sns')
                sns.publish(
                    TopicArn=os.environ['SNS_EVENTOS_ARN'],
                    Message=json.dumps({
                        'tipo_evento': 'compra_vianda',
                        'usuario_id': user_id,
                        'vianda_id': vianda_id,
                        'compra_id': compra_id,
                        'cantidad': cantidad,
                        'timestamp': fecha_compra.isoformat()
                    })
                )
                print("Evento publicado en SNS")
            except Exception as sns_error:
                print(f"Error publicando en SNS: {str(sns_error)}")

            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Credentials': True
                },
                'body': json.dumps({
                    'message': 'Compra realizada correctamente',
                    'compra_id': compra_id,
                    'fecha_compra': fecha_compra.isoformat(),
                    'cantidad': cantidad
                })
            }

        except Exception as e:
            if conn:
                conn.rollback()
            raise e

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
                'error': 'Error al procesar la compra',
                'detalles': str(e)
            })
        }
    finally:
        if conn:
            conn.close()
