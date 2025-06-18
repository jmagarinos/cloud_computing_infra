import json
import boto3
import uuid
from datetime import datetime
import os

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['DYNAMO_TABLE'])

def lambda_handler(event, context):
    for record in event['Records']:
        mensaje = json.loads(record['Sns']['Message'])

        item = {
            'id_evento': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat(),
            'usuario_id': mensaje.get('usuario_id'),
            'tipo_evento': mensaje.get('tipo_evento'),
            'detalle': {
                k: v for k, v in mensaje.items() if k not in ['usuario_id', 'tipo_evento']
            }
        }

        table.put_item(Item=item)

    return {'statusCode': 200, 'body': 'Eventos guardados'}
