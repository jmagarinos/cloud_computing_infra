import json
import os
import psycopg2

def lambda_handler(event, context):
    user_attributes = event['request']['userAttributes']
    
    # Get the Cognito user ID (sub)
    cognito_sub = event['userName']  # This is the Cognito sub/user ID
    
    email = user_attributes.get('email')
    nombre = user_attributes.get('given_name')
    apellido = user_attributes.get('family_name')
    telefono = user_attributes.get('phone_number')
    # The 'address' attribute is collected during signup
    direccion = user_attributes.get('address', '') 

    if not all([email, nombre, apellido, telefono]):
        print(f"Error: Missing one or more required user attributes for email {email}. Required: email, given_name, family_name, phone_number.")
        # Return the event to Cognito; the user is already confirmed.
        # Log the error for monitoring.
        return event

    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            host=os.environ['DB_HOST'],
            database=os.environ['DB_NAME'],
            user=os.environ['DB_USER'],
            password=os.environ['DB_PASSWORD'],
            port=5432  # Default PostgreSQL port
        )
        cur = conn.cursor()

        # Check if user already exists to prevent duplicate entries
        cur.execute("SELECT id FROM persona WHERE mail = %s OR cognito_sub = %s", (email, cognito_sub))
        if cur.fetchone():
            print(f"User with email {email} or cognito_sub {cognito_sub} already exists in persona table.")
            return event # User already exists, successful completion for Cognito

        # Include cognito_sub in the insert
        sql = """
            INSERT INTO persona (nombre, apellido, telefono, direccion, mail, cognito_sub)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id;
        """
        cur.execute(sql, (nombre, apellido, telefono, direccion, email, cognito_sub))
        persona_id = cur.fetchone()[0]
        conn.commit()
        print(f"Successfully inserted user {email} with cognito_sub {cognito_sub} into persona table with ID {persona_id}.")

    except psycopg2.Error as db_error:
        print(f"Database error for email {email}: {str(db_error)}")
        if conn:
            conn.rollback()
        # Return the event to Cognito; the user is already confirmed.
        # Log the error for monitoring.
    except Exception as e:
        print(f"An unexpected error occurred for email {email}: {str(e)}")
        if conn:
            conn.rollback()
        # Return the event to Cognito.
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

    return event