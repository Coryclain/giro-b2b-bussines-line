import os
import smtplib
import logging
import boto3
import json

from botocore.exceptions import ClientError

# import email.utils
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.application import MIMEApplication

from custom_errors import RequestParameterError
from dao.templates import Templates

log = logging.getLogger('giro')

# def send_email_lambda(template_id, event, path = False):
#     client = boto3.client('lambda')
#     log = logging.getLogger('giro')
#     lambda_name = os.environ.get('LAMBDA_EMAIL')
#     try:

#         request = {
#             'template_id': template_id,
#             'data': event,
#             'path': path
#         }

#         response = client.invoke(
#             FunctionName=lambda_name,
#             InvocationType='RequestResponse',
#             Payload=json.dumps(request)
#         )

#         if response['ResponseMetadata']['HTTPStatusCode'] == 200:
#             stream = response['Payload']
#             resp_json = json.loads(stream.read())
#             log.info('{}'.format(resp_json))
#             if resp_json['statusCode'] == 200:
#                 return json.loads(resp_json['body'])
#             elif resp_json['statusCode'] in [400,403,409]:
#                 return json.loads(resp_json['body'])
#             else:
#                 log.error('no es 200')
#                 raise RequestParameterError('4056/Error en comunicación') 
#         else:
#             log.error('no es 200 (1)')
#             raise RequestParameterError('4056/Error en comunicación') 
#     except Exception as ex:
#         log.error(ex,exc_info=1)
#         raise RequestParameterError('4056/Error en comunicación')

def send_email(template_id, event, path = False):
    template = Templates.retrivied_by_template_id(template_id)
    print(template)
   
    if template:

        subject = template.data.get('subject')
        for i in template.data.get('replace'):
            key = i['key']
            rep = i['replace']
            subject = subject.replace(rep, str(event.get(key)))
        
        print(subject)
        
        body = template.data.get('template')
        for i in template.data.get('replace'):
            key = i['key']
            rep = i['replace']
            body = body.replace(rep, str(event.get(key)))
        
        if not path:
            print('creating mailing')
            print(event)
            create_mailing(subject, event.get('email'), body)
        # else:
        #     create_and_send_email_pdf(event.get('email'), template.data.get('subject'),body, path)

def create_mailing(subject, to, html):
    log.info('enviando correo')
    email_sender = os.environ.get('SENDER_EMAIL')
    BODY_HTML = html
    CHARSET = "UTF-8"
    ses = boto3.client('ses',region_name="us-east-1")

    try:
        response = ses.send_email(
            Destination={
                'ToAddresses': [to],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': CHARSET,
                        'Data': BODY_HTML,
                    }
                },
                'Subject': {
                    'Charset': CHARSET,
                    'Data': subject,
                },
            },
            Source=email_sender,
        )
    # Display an error if something goes wrong.	
    except ClientError as e:
        raise RequestParameterError(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def lambda_send_email(template_id, event, path = False):
    lambda_name = "{}-services-email-send_email".format(os.environ.get("STAGE"))

    invoke_lambda = boto3.client('lambda')
    try: 
        request = {
            "template_id": template_id,
            "body": event,
            "path": path
        }
        
        print("{}".format(request))
        invoke_lambda.invoke(
            FunctionName = lambda_name,
            InvocationType='Event',
            Payload = json.dumps(request)
            )
    
    except Exception as ex:
        log.error(ex)
        raise Exception('No se invoco la funcion lambda')

    

# def create_and_send_email_pdf(recipient,subject,html, path):
#     email_sender = os.environ.get('SENDER_EMAIL')
#     user_smtp = os.environ.get('USER_SMTP')
#     password = os.environ.get('PASSWORD_SMTP')
#     host = os.environ.get('HOST_SMTP')
#     port = os.environ.get('PORT_SMTP')
#     charset = 'UTF-8'

#     SENDER = email_sender  
#     SENDERNAME = email_sender
#     RECIPIENT  = recipient
#     USERNAME_SMTP = user_smtp
#     PASSWORD_SMTP = password
#     HOST = host
#     PORT = port
        
#     msg = MIMEMultipart('alternative')
#     msg['Subject'] = subject
#     msg['From'] = email.utils.formataddr((SENDERNAME, SENDER))
#     msg['To'] = RECIPIENT
#     part2 = MIMEText(html, 'html')
#     #msg.attach(part2)
#     try:
#         ATTACHMENT = path
#         att = MIMEApplication(open(ATTACHMENT, 'rb').read())
#         att.add_header('Content-Disposition', 'attachment', filename='Contrato-Credito-Giro.pdf')
#         msg.attach(att)

#         msg.attach(part2)  
#         server = smtplib.SMTP(HOST, PORT)
#         server.ehlo()
#         server.starttls()
#         server.ehlo()
#         server.login(USERNAME_SMTP, PASSWORD_SMTP)
#         server.sendmail(SENDER, RECIPIENT, msg.as_string())
#         server.close()
#     # Display an error message if something goes wrong.
#     except Exception as ex:
#         log.info(ex)
#         raise RequestParameterError('3001/Ocurrio un error en el envío del correo electrónico')
#     else:
#         log.info("Email sent!")
