# SES Tools

A suite of utilities for integrating with SES:

* A wrapper for sending emails via SES with support for attachments.
* SQS workers for processing Bounce and Complaint notifications from SES.
* Elasticsearch wrapper for querying email logs generated from SES.

## SES Wrapper

This wrapper is a straightforward utility function to send emails via the SendRawEmail SES API. After configuring your AWS credentials in the environment, you can send email with the following:

```
>>> from ses-tools import ses
>>> ses.send_mail('from@example.com', 'to@example.com', '[Test] Email Subject', text='Sending a test email.')
```

## SQS Worker

The SQS worker is a program that takes the region and an SQS queue name, processes messages from that queue indefinitely, and dispatches those messages to a function with the name queue name. `workers/sqs_tasks.py` contains an example function `ses_queue` that processes events from SES and handles the `Bounce` and `Complaint` events. After configuring your AWS credentials in the environment, you can start processing messages from the SQS queue with the following:

```
PYTHONPATH=. python workers/sqs_worker.py <queue-name>
```

You should update the function in `workers/sqs_tasks.py` to be the same name as `<queue-name>`.

## Elasticsearch Wrapper

SES allows you to create configuration sets to send data to Kinesis then Elasticsearch. The Elasticsearch wrapper provides an easy way to query that elasticsearch cluter, which is helpful for querying from within your application versus in Kinbana. After configuring your AWS credentials in the environment, you can test querying Elasticsearch with the `search/ses_event_count.py` function:

```
PYTHONPATH=. python search/ses_event_count.py --host <Elasticsearch host> --region <AWS region> --event Bounce
```

## License

ses-tools is available under the MIT license. See LICENSE.md for more info.
