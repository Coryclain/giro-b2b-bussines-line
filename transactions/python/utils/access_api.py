import boto3
import os
import logging
import hashlib

from custom_errors import SessionError
from datetime import datetime, timezone
from pytz import timezone

log = logging.getLogger('giro')
dynamodb = boto3.resource('dynamodb')
table_sesion = os.environ.get('TABLE_SESSION')

class AccessAPI:
    def __init__(self, **kwargs):
        self.data = dict()
        self.data.update(kwargs)
    
    @classmethod
    def get_data(cls,data):
        return AccessAPI(**data)

    @classmethod
    def get_session(cls,email, token):
        time_zone = os.environ.get("TIME_ZONE")
        if table_sesion:
            table = dynamodb.Table(table_sesion)
            token = hashlib.sha256(str(token).encode()).hexdigest()
            session = table.get_item(Key={'email': email})
            if session.get('Item'):
                now = datetime.now(timezone(time_zone))
                if now.isoformat() >= session['Item']['expiration_date']:
                    raise SessionError("Token no valido")
                if token != session['Item']['token']:
                    raise SessionError('Existe una sesión activa, por tu seguridad se cerrará la sesión')
            else:
                raise SessionError('Existe una sesión activa, por tu seguridad se cerrará la sesión')
            return session.get('Item')
        else:
            raise SessionError('missing table session')
        