import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        # Parsear el body recibido en el POST
        body = json.loads(event.get('body', '{}'))
        
        nombre = body.get('nombre')
        descripcion = body.get('descripcion')
        precio = body.get('precio')
        
        if not nombre or precio is None:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'Faltan campos obligatorios: nombre y precio'})
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
        
        insert_query = """
            INSERT INTO viandas (nombre, descripcion, precio)
            VALUES (%s, %s, %s);
        """
        cur.execute(insert_query, (nombre, descripcion, precio))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Vianda insertada correctamente'})
        }
        
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
