import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda LIST iniciada")
        
        # Obtener email del usuario autenticado (por si queremos loguear quién hace la consulta)
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
            'body': json.dumps({
                'viandas': viandas_list
            })
        }
        
    except Exception as e:
        print(f"Error en la Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al obtener las viandas',
                'detalles': str(e)
            })
        }
