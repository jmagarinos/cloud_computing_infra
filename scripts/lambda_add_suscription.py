import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        # Parsear el evento
        body = json.loads(event['body']) if 'body' in event else event
        comprador_id = body.get('comprador_id')
        cocinero_id = body.get('cocinero_id')

        if not comprador_id or not cocinero_id:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Faltan campos requeridos'})
            }

        # Conexión a la base de datos
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )
        cur = conn.cursor()

        # Insertar suscripción si no existe
        cur.execute("""
            INSERT INTO suscripciones (comprador_id, cocinero_id)
            VALUES (%s, %s)
            ON CONFLICT (comprador_id, cocinero_id) DO NOTHING;
        """, (comprador_id, cocinero_id))

        conn.commit()
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Suscripción registrada correctamente'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
