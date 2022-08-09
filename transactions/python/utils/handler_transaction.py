import boto3
import logging
import importlib

import botocore.exceptions

#from jsonschema import validate
from datetime import datetime

from response import Response
from custom_errors import *
from sql.sql import SQL
from exchange.crypto import AESCipher

from dao.session.session import Session

log = logging.getLogger('giro')
dynamodb = boto3.resource('dynamodb')
response = Response()

class HandlerTransaction:
    
    def __init__(self, **kwargs):
        self.data = dict()
        self.data.update(kwargs)
    
    @classmethod
    def get_data(cls,data):
        return HandlerTransaction(**data)

    #Metodo transactions
    @classmethod
    def transactions(cls, event, table_name):
        sql = None
        try:
            #Ir por item a la tabla
            results = []
            item = cls.get_app_id(table_name, event.get('app_id'))
            # cifrando o descifrando request
            if item.data.get("decrypt_request"):
                event = cls.decrypt_request(event, item.data.get("decrypt_request"))
            results.append(event)
            log.info('item transaction {}'.format(item.data))
            if item.data.get('is_sql'):
                sql = SQL.init()
            #For list de transactions
            for i in item.data.get('tx_models'):
                log.info("execute transactions: {}.{}".format(i['path'],i['method']))
                request = dict()
                module = importlib.import_module(i['path'])
                method = getattr(module, i['method'])
                for k,v in i.get('request').items():
                    #Si el request no se encuentra en el event, no lo mandes o manda vacío
                    if k in results[int(v)]:
                        request[k] = results[int(v)][k]
                #Guardar las respuestas de cada trasactions
                results.append(method(request))
            #Retornar la lista de respuestas
            response_json = dict()
            results.pop(0)
            for k,v in item.data.get('response').items():
                response_json[k] = results[int(v)][k]
            log.info('transaction {}'.format(response_json))
            # buscar si tenemos que cifrar algun dato
            if item.data.get("encrypt_response"):
                response_json = cls.encrypt_response(event, response_json, item.data.get("encrypt_response"))
            if item.data.get('is_sql'):
                sql.commit()
                sql.close()
            return cls.get_data({'response':response_json})
        except ModuleNotFoundError as ex:
            log.error(ex)
            if sql:
                SQL.rollback()
                SQL.close()
            raise KeyError(ex)
        except KeyError as ex:
            log.error(ex)
            if sql:
                SQL.rollback()
                SQL.close()
            raise KeyError("Un atributo no existe")
        except botocore.exceptions.ClientError as ex:
            log.error(ex)
            if sql:
                SQL.rollback()
                SQL.close()
            raise ClientErrorBoto3("Error resource")
        except Exception as ex:
            #Regresa response
            log.error(ex)
            if sql:
                SQL.rollback()
                SQL.close()
            raise ex

    @classmethod
    def get_app_id(cls, table_name, app_id):
        table = dynamodb.Table(table_name)
        item = table.get_item(
            Key={'app_id': app_id}
        )
        if item.get('Item'):
            return cls.get_data(item.get('Item'))
        raise NameError("No existe app_id")

    @classmethod
    def decrypt_request(cls, req, list_decrypt):
        if req.get("is_session"):
            log.info("request with session")
            key = req.get("key_encrypt")
        else:
            log.info("Petición sin sesion")
            exchange = Session.retrivied_by_email(req.get("id","noexiste"))
            if not exchange:
                raise SessionError("Session de intercambio no existe")
            
            today = datetime.utcnow().isoformat()
            if today > exchange.data.get("end_session"):
                raise SessionError("Sesion de intercambio no valida")
            cls.exchange = exchange
            key = exchange.data.get("key")
            
        # descifrando informacion
        cls.list_decrypt = list_decrypt
        cls.cipher = AESCipher(key)
        request = cls.decrypt_attr(req)
        return request

    @classmethod
    def decrypt_attr(cls,obj):
        if isinstance(obj, dict):
            return {k:cls.decrypt(k, cls.decrypt_attr(v)) for k, v in obj.items()}
        elif isinstance(obj, (list, set, tuple)):
            t = type(obj)
            return t(cls.decrypt_attr(o) for o in obj)
        else:
            return obj       

    @classmethod
    def decrypt(cls,key,value):
        if key in cls.list_decrypt:
            return cls.cipher.decrypt(value)
        else:
            return value 
    
    @classmethod
    def encrypt_response(cls,req, resp, list_encrypt):
        if req.get("is_session"):
            log.info("petición con sesion iniciada")
            key = req.get("key_encrypt")
        else:
            log.info("Petición sin sesion")
            key = cls.exchange.data.get("key")
        
        print("valor de la llave",key)
        # descifrando informacion
        cls.list_encrypt = list_encrypt
        cls.cipher = AESCipher(key)
        response = cls.encrypt_attr(resp)
        return response
    
    @classmethod
    def encrypt_attr(cls,obj):
        if isinstance(obj, dict):
            print(obj)
            return {k:cls.encrypt(k, cls.encrypt_attr(v)) for k, v in obj.items()}
        elif isinstance(obj, (list, set, tuple)):
            t = type(obj)
            print(obj)
            return t(cls.encrypt_attr(o) for o in obj)
        else:
            print(obj)
            return obj  
    
    @classmethod
    def encrypt(cls,key,value):
        if key in cls.list_encrypt:
            return cls.cipher.encrypt(str(value))
        else:
            return value 