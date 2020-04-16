import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def format_email(sender, recipient, subject,
                 text=None, html=None, attachments=None):
    msg = MIMEMultipart('mixed')
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject
    
    msg_body = MIMEMultipart('alternative')
    if text:
        text_msg = MIMEText(text, 'plain', 'utf-8')
        msg_body.attach(text_msg)
    if html:
        html_msg = MIMEText(html, 'html', 'utf-8')
        msg_body.attach(html_msg)
    msg.attach(msg_body)

    attachments = attachments or []
    for filename, data in attachments:
        attachment_msg = MIMEApplication(data)
        attachment_msg.add_header('Content-Disposition', 'attachment', filename=filename)
        msg.attach(attachment_msg)
    
    return msg.as_string()

def send_email(sender, recipient, subject,
               text=None, html=None, attachments=None,
               region='us-east-1', configuration=''):
    client = boto3.client('ses', region)
    formatted_email = format_email(
        sender, recipient, subject, text=text, html=html, attachments=attachments)

    client.send_raw_email(
        Source=sender,
        Destinations=[recipient],
        RawMessage={'Data': formatted_email},
        ConfigurationSetName=configuration)
