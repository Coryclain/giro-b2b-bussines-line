import os
import requests
import json
import logging

log = logging.getLogger('giro')

def send_push(client_id, template, datos=None):
    log.info('Enviando push')
    log.info(client_id)
    url = os.environ.get('SENDER_PUSH')

    body = template.get('template')
    # Si contiene elementos a remplazar se realiza.
    if template.get('replace'):
        body = template.get('template')
        for i in template.get('replace'):
            key = i['key']
            rep = i['replace']
            body = body.replace(rep, str(datos.get(key)))
    
    payload = json.dumps({
        "client_id": client_id,
        "title": template.get('subject'),
        "body": body,
        "type_send": "push"
    })
    headers = {
        'x-api-key': os.environ.get('PUSH_API_KEY'),
        'Authorization': os.environ.get('PUSH_AUTHORIZATION'),
        'Content-Type': 'application/json'
    }
    log.info(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    log.info(response.text)
    return response.text
