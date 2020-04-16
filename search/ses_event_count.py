#!/usr/bin/env python
from __future__ import print_function

import argparse
from datetime import datetime
import os
import sys

from search import ses_search

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', required=True, help='Elasticsearch host')
    parser.add_argument('--region', required=True, help='AWS region')
    parser.add_argument('--sender', nargs='?', default='*', help='From email address')
    parser.add_argument('--recipient', nargs='?', default='*', help='To email address')
    parser.add_argument('--subject', nargs='?', default='*', help='Subject')
    parser.add_argument('--event', nargs='?', default='*', choices=['Bounce', 'Complaint', 'Delivery', 'Send', 'Open'], help='Event type')
    parser.add_argument('--start_date', nargs='?', default='*', help='Start date (YYYY-MM-DD)', type=lambda d: '*' if d == '*' else datetime.strptime(d, '%Y-%m-%d').strftime('%Y-%m-%d'))
    parser.add_argument('--end_date', nargs='?', default='*', help='End date (YYYY-MM-DD)', type=lambda d: '*' if d == '*' else datetime.strptime(d, '%Y-%m-%d').strftime('%Y-%m-%d'))
    
    args = parser.parse_args()

    aws_access_token = os.environ.get('AWS_ACCESS_KEY_ID')
    aws_access_token_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    if not aws_access_token or not aws_access_token_secret:
        print('Missing AWS credentials. Please set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables')
        parser.print_help()
        sys.exit(-1)

    search = ses_search.EmailSearch(
        args.host,
        args.region,
        aws_access_token,
        aws_access_token_secret)
    events, count = search.query(
        args.event,
        sender=args.sender,
        recipient=args.recipient,
        subject=args.subject,
        start_date=args.start_date,
        end_date=args.end_date)

    print('%d events' % count)
