import json
import logging
import os

from custom_errors import *
from decimal import Decimal
from datetime import datetime

class Response:

    log = logging.getLogger('giro')

    def classify_error(self, error):

        error_string = str(error).split('/')
        body = {}
        if len(error_string) == 2:
            body = {'code':error_string[0], 'message':error_string[1]}
        elif len(error_string) == 3:
            body = {'code':error_string[0], 'message':error_string[1], 'end': error_string[2]}
        elif len(error_string) == 4:
            body = {'code':error_string[0], 'message':error_string[1], 'end': error_string[2], 'remaining_time': error_string[3]}
        elif len(error_string) == 5:
            body = {'code':error_string[0], 'message':error_string[1], 'remaining_time': error_string[3], 'step': error_string[4]}
        else:
            body = {'message':error_string[0]}
            
        error_string_second = str(error).split('&')
        if len(error_string_second) == 2:
            body = {'property':error_string_second[0], 'message':error_string_second[1]}
        
        message = json.dumps(body)

        if isinstance(error, RequestParameterError):
            response = {
                "statusCode": 409,
                "body": message
            }
        elif isinstance(error, ClientErrorBoto3):
            response = {
                "statusCode": 502,
                "body": message
            }
        elif isinstance(error, NameError):
            response = {
                "statusCode": 502,
                "body": message
            }
        elif isinstance(error, SQLException):
            response = {
                "statusCode": 502,
                "body": message
            }
        elif isinstance(error, KeyError):
            response = {
                "statusCode": 502,
                "body": message
            }
        elif isinstance(error, SessionError):
            response = {
                "statusCode": 401,
                "body": message
            }
        else:
            response = {
                "statusCode": 409,
                "body": message,
            }

        return response

    def correct_answer(self, message):
        response = {
            "statusCode": 200,
            "body": json.dumps(message, default=self.default)
        }
        return response

    def bad_request_answer(self, message):

        message = json.dumps({"message": str(message)})

        response = {
            "statusCode": 400,
            "body": str(message)
        }
        return response

    def api_response(self, message):
        api_message = {
            "statusCode": message['statusCode'],
            "body": message['body'],
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Headers": "*"
            }
        }

        return api_message

    def api_bad_request_answer(self, message):

        message = json.dumps({'message': 'bad request'})

        response = {
            "statusCode": 400,
            "body": message,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Headers": "*"
            }
        }
        return response

    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
