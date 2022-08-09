import boto3
import json
import logging
import os
import hashlib

from custom_errors import RequestParameterError, SessionError
from response import Response
from init import init
from utils.handler_transaction import HandlerTransaction
from utils.access_api import AccessAPI

log = logging.getLogger('giro')
response = Response()
cors_allow = os.environ.get('CORS_ALLOW')
table_catalog = os.environ.get('TABLE_TRANSACTIONS')
response_json = dict()

class HandlerAPI:
    
    def __init__(self, **kwargs):
        self.data = dict()
        self.data.update(kwargs)
    
    @classmethod
    def get_data(cls,data):
        return HandlerAPI(**data)
    
    @classmethod
    def set_handler(cls, event):
        try:
            method = event.get('httpMethod')
            paths = event.get('path').split('/')
            path_param = event.get('pathParameters')
            name = ''
            paths.remove('')
            if path_param:
                path_param_values = set(list(path_param.values()))
                paths = [f for f in paths if f not in path_param_values]
            for path in paths:
                name = name + '_' + path
            log.info("name:" + name)
            log.info("method: " + method.lower())
            c_request = cls.create_request(event, method, method.lower() + name)
            response_json = cls.lambda_handler(c_request.data.get('request'))
            log.info('respuesta antes de regresar {}'.format(response_json.data))
            # resp = 
            # if ('statusCode' in response_json.data.get('response') and response_json.data.get('response')['statusCode'] != '200'):
            #     resp = {
            #         'statusCode': response_json.data.get('response')['statusCode'],
            #         'body': json.dumps(response_json.data.get('response')['body'])
            #     }
            #     log.info('respuesta error', resp)
            #     return cls.get_data({'response_finally': response.api_response(response_json.data.get('response'), cors_allow)})
            return cls.get_data({'response_finally': response.api_response(response.correct_answer(response_json.data.get('response')))})
        except Exception as ex:
            #log.error('Varable no declarada', exc_info=1)
            response_json = response.api_response(response.classify_error(ex))
            return cls.get_data({'response_finally': response_json})
            
    @classmethod
    def create_request(cls, event, method, name_json):
        request = dict()
        try:
            if method == 'GET' and event.get("queryStringParameters"):
                request = event['queryStringParameters']
            else:
                body = event['body']
                if body is not None:
                    request.update(json.loads(body))
            extra_data = {
                'ip': event['requestContext']['identity']['sourceIp'],
                'agent': event['requestContext']['identity']['userAgent']
            }
            if('Authorization' in event['headers']):
                extra_data['email'] = event['requestContext']['authorizer']['claims']['email']
                extra_data['is_session'] = True
                session = AccessAPI.get_session(extra_data['email'], event['headers']['Authorization'])
                extra_data["key_encrypt"] = session.get("key")
            else:
                extra_data['is_session'] = False
            if event['headers'].get('x-api-key'):
                extra_data['api_key'] = event['headers'].get('x-api-key')
            
            request.update(extra_data)
            # agrego el nombre del json para consultar el app_id en la tabla transacciones
            log.info('name_json: ' + name_json)
            request['app_id'] = name_json
            return cls.get_data({'request': request})
        except SessionError as ex:
            log.warning('missing field', exc_info=1)
            raise SessionError(ex)
    
    @classmethod
    def lambda_handler(cls, event):
       #  try:
            # logica de negocio
        resp = HandlerTransaction.transactions(event, table_catalog)
        return cls.get_data({'response': resp.data.get('response')})
        # except Exception as ex:
        #     resp_error = response.classify_error(ex)
        #     return cls.get_data({'response': resp_error})
            