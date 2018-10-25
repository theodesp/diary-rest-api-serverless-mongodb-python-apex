import logging
import json
import bson
import os
import datetime

import client

# Logger settings - CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle(event, context={}):
    logger.info("Received event: " + json.dumps(event, indent=2))

    diaries = client.db['diary']
    diary_list = list_diaries(diaries)

    resp = {}
    resp['isBase64Encoded'] = False
    resp['statusCode'] = 200
    resp['headers'] = {}
    resp['body'] = json.dumps(diary_list, default=json_unknown_type_handler)

    return resp

def list_diaries(diaries):
    return list(diaries.find({}, { 'title': 1 }))

def json_unknown_type_handler(x):
    """
    JSON cannot serialize decimal, datetime and ObjectId.
    """
    if isinstance(x, bson.ObjectId) or isinstance(x, datetime.datetime):
        return str(x)
    raise TypeError("Unknown type")
