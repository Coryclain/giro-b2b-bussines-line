import logging

log = logging.getLogger('giro')

def send_sms(mobile, message, replace=None, values=None):
    log.info('send_sms')
    '''url_wsdl = os.environ.get('URL_MARCATEL')
    user = os.environ.get('USER_MARCATEL')
    password = os.environ.get('PASSWORD_MARCATEL')

    if replace:
        for i in replace:
            key = i['key']
            rep = i['replace']
            message = message.replace(rep, str(values.get(key)))

    client = Client(url=url_wsdl)
    response = client.service.InsertaMensajes_xl_Corto(
        message,
        mobile,
        user,
        password,
        "",
        "1",
        "",
        "52"
    )

    log.info("{}".format(response))'''

    #return {'code': response['code']}
    return {'code': 200}