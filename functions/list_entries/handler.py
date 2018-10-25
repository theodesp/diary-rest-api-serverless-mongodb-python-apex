import logging
import json
import bson
import os
import datetime
from bson.objectid import ObjectId

import client

# Logger settings - CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle(event, context={}):
    logger.info("Received event: " + json.dumps(event, indent=2))

    diaries = client.db['diary']
    diary_id = event["diary_id"]

    entries_list = list_entries(diaries, diary_id)
    resp = {}
    resp['isBase64Encoded'] = False
    resp['statusCode'] = 200
    resp['headers'] = {}
    resp['body'] = json.dumps(entries_list, default=json_unknown_type_handler)

    return resp

    # return json.loads(json.dumps(entries_list, default=json_unknown_type_handler))

def list_entries(diaries, diary_id):
    return diaries.find_one({ "_id": ObjectId(diary_id) }, { '_id': 0, 'entries': 1 })

def json_unknown_type_handler(x):
    """
    JSON cannot serialize decimal, datetime and ObjectId.
    """
    if isinstance(x, bson.ObjectId) or isinstance(x, datetime.datetime):
        return str(x)
    raise TypeError("Unknown type")
