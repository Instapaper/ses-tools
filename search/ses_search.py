from __future__ import print_function

import os
import json
import time
import datetime
from elasticsearch import Elasticsearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


class EmailEvent(object):
    def __init__(self, event_type, sender, recipient, subject, timestamp):
        self.event_type = event_type
        self.sender = sender
        self.recipient = recipient
        self.subject = subject
        self.timestamp = timestamp

    def __repr__(self):
        return 'EmailEvent(sender="%s", recipient="%s", subject="%s", timestamp="%s")' % (self.sender, self.recipient, self.subject[:50], self.timestamp)

    def __str__(self):
        return 'EmailEvent(sender="%s", recipient="%s", subject="%s", timestamp="%s")' % (self.sender, self.recipient, self.subject[:50], self.timestamp)


class Search(object):
    def __init__(self, host, region, aws_access_key, aws_access_key_secret):
        awsauth = AWS4Auth(
            aws_access_key,
            aws_access_key_secret,
            region,
            'es'
        )
        self.elasticsearch = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )


class EmailSearch(Search):
    def query(self, event_type='*', sender='*', recipient='*',
              subject='*', start_date='*', end_date='*', sort_order='desc'):
        sort_order = 'desc'
        sender = "'\"%s\"" % sender if sender != '*' else sender
        recipient = "\"%s\"" % recipient if recipient != '*' else recipient
        subject = "\"%s\"" % subject if subject != '*' else subject
        query_str = ('eventType:%s AND mail.timestamp:[%s TO %s] AND ' + 
            'mail.commonHeaders.subject:%s AND mail.commonHeaders.from:%s AND ' +
            'mail.commonHeaders.to:%s') % (
            event_type,
            start_date,
            end_date,
            subject,
            sender,
            recipient)
        body = {
            "query": {
                "query_string": {
                    "query": query_str
                }
            },
            "sort": {
                "mail.timestamp": {
                    "order": sort_order
                }
            }
        }
        count_body = {'query': body['query'] }

        try:
            results = self.elasticsearch.search(
                index='events',
                body=json.dumps(body)
            )
            count_results = self.elasticsearch.count(
                index='events',
                body=json.dumps(count_body)
            )
            count = count_results['count']   
        except Exception, e:
            print('[ElasticSearch] Query failed: %s' % str(e))
            return [], 0

        events = []
        for result in results['hits']['hits']:
            event = result['_source']
            event_type = event['eventType']
            mail = event['mail']
            source = mail['source']
            destination = mail['destination'][0]
            subject = mail['commonHeaders']['subject']
            timestamp = mail['timestamp']
            events.append(EmailEvent(event_type, source, destination, subject, timestamp))

        return events, count
