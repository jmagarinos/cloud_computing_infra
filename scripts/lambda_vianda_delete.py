import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        print("Lambda DELETE iniciada")
        
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
        
        # Obtener el ID de la vianda de los parámetros de la URL
        vianda_id = event.get('pathParameters', {}).get('id')
        
        if not vianda_id:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Datos inválidos',
                    'detalles': 'Se requiere el ID de la vianda'
                })
            }
        
        print(f"Vianda a eliminar: id = {vianda_id}")
        
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
        
        # Verificar si la vianda existe y pertenece al usuario
        print("Verificando propiedad de la vianda")
        cur.execute("SELECT fk_dueno FROM vianda WHERE id = %s", (vianda_id,))
        result = cur.fetchone()
        
        if not result:
            return {
                'statusCode': 404,
                'body': json.dumps({
                    'error': 'Vianda no encontrada'
                })
            }
        
        if result[0] != persona_id:
            return {
                'statusCode': 403,
                'body': json.dumps({
                    'error': 'No autorizado',
                    'detalles': 'Solo puedes eliminar tus propias viandas'
                })
            }
        
        # Eliminar la vianda
        print("Eliminando vianda")
        cur.execute("DELETE FROM vianda WHERE id = %s", (vianda_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        
        print(f"Vianda {vianda_id} eliminada correctamente")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Vianda eliminada correctamente'
            })
        }
        
    except Exception as e:
        print(f"Error en la Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': 'Error al eliminar la vianda',
                'detalles': str(e)
            })
        }
