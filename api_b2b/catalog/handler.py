import logging

from init import init
from utils.handler_api import HandlerAPI

log = logging.getLogger('giro')

def handler(event, context):
    init()
    log.info(event)
    response = HandlerAPI.set_handler(event)
    return response.data.get('response_finally')