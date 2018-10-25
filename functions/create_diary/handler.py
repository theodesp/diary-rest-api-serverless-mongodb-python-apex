import logging
import json
import bson
import os

import client

# Logger settings - CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def handle(event, context={}):
    logger.info("Received event: " + json.dumps(event, indent=2))

    diaries = client.db['diary']
    diary = {
        "title": event["title"],
        "entries": []
    }

    created = create_diary(diaries, diary)
    resp = {}
    resp['isBase64Encoded'] = False
    resp['statusCode'] = 204
    resp['headers'] = {}
    resp['body'] = json.dumps(created, default=json_unknown_type_handler)

    return resp
    # return json.loads(json.dumps(created, default=json_unknown_type_handler))

def create_diary(diaries, diary):
    diary_id = diaries.insert_one(diary).inserted_id

    return diaries.find_one({ "_id": diary_id })

def json_unknown_type_handler(x):
    """
    JSON cannot serialize decimal, datetime and ObjectId.
    """
    if isinstance(x, bson.ObjectId) or isinstance(x, datetime.datetime):
        return str(x)
    raise TypeError("Unknown type")
