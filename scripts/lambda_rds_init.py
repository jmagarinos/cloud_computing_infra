import json
import os
import psycopg2

def lambda_handler(event, context):
    try:
        # Conexión a la base de datos
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432
        )

        cur = conn.cursor()

        cur.execute("DROP TABLE IF EXISTS ventas CASCADE;")
        cur.execute("DROP TABLE IF EXISTS vianda CASCADE;")
        cur.execute("DROP TABLE IF EXISTS persona CASCADE;")
        conn.commit()
        cur.close()

        
        cur = conn.cursor()


        # Crear tabla persona
        cur.execute("""
            CREATE TABLE IF NOT EXISTS persona (
                id SERIAL PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                apellido VARCHAR(100) NOT NULL,
                telefono VARCHAR(20) NOT NULL,
                direccion VARCHAR(200) NOT NULL,
                mail VARCHAR(100) NOT NULL UNIQUE,
                cognito_sub VARCHAR(255) UNIQUE
            );
        """)

        # Crear tabla vianda
        cur.execute("""
            CREATE TABLE IF NOT EXISTS vianda (
                id SERIAL PRIMARY KEY,
                titulo VARCHAR(100) NOT NULL,
                imagen VARCHAR(255),
                descripcion TEXT NOT NULL,
                precio DECIMAL(10,2) NOT NULL,
                disponible BOOLEAN NOT NULL DEFAULT TRUE,
                fk_dueno INTEGER NOT NULL,
                FOREIGN KEY (fk_dueno) REFERENCES persona(id)
            );
        """)


        # Crear tabla ventas
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id SERIAL PRIMARY KEY,
                fk_vianda INTEGER NOT NULL,
                fk_persona INTEGER NOT NULL,
                cantidad INTEGER NOT NULL,
                fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (fk_vianda) REFERENCES vianda(id),
                FOREIGN KEY (fk_persona) REFERENCES persona(id)
            );
        """)

        # Crear índices
        cur.execute("CREATE INDEX IF NOT EXISTS idx_vianda_dueno ON vianda(fk_dueno);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ventas_vianda ON ventas(fk_vianda);")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_ventas_persona ON ventas(fk_persona);")

        conn.commit()
        cur.close()
        conn.close()

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Tablas creadas correctamente'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
