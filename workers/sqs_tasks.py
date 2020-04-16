from __future__ import print_function

import json

def ses_queue(data):
    def unsubscribe_email(email):
        print('[SES Notif Queue] Unsubscribe %s' % email)
        # Application logic here

    def bounce_handler(message):
        bounce = message['bounce']
        bounce_type = bounce.get('bounceType')
        if bounce_type != 'Permanent':
            return
        for recipient in bounce['bouncedRecipients']:
            email = recipient['emailAddress']
            unsubscribe_email(email, 'Bounce')
         
    def complaint_handler(message):
        complaint = message['complaint']
        for recipient in complaint['complainedRecipients']:
            email = recipient['emailAddress']
            unsubscribe_email(email, 'Complaint')

    try:
        message = json.loads(data['Message'])
    except Exception, e:
        print('[SES Notif Queue] "Message" malformed in data, skipping...: %s' % str(e))
        return

    notif_type = message['notificationType']
    notif_handlers = {
        'Bounce': bounce_handler,
        'Complaint': complaint_handler,
    }
    ses_handler = notif_handlers.get(notif_type)
    if not ses_handler:
        print('[SES Notif Queue] Received unknown notification type %s: %s' % (notif_type, str(message)))
        return
    
    ses_handler(message)
