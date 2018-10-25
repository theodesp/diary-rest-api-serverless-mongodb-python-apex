import logging
import json
import bson
import os
import datetime
import re

from bson.objectid import ObjectId

import client

# Logger settings - CloudWatch
logger = logging.getLogger()
logger.setLevel(logging.INFO)

class DiaryDoesNotExist(Exception): pass

def slugify(s):
    """
    Simplifies ugly strings into something URL-friendly.
    >>> print slugify("[Some] _ Article's Title--")
    some-articles-title

    https://blog.dolphm.com/slugify-a-string-in-python/
    """

    # "[Some] _ Article's Title--"
    # "[some] _ article's title--"
    s = s.lower()

    # "[some] _ article's_title--"
    # "[some]___article's_title__"
    for c in [' ', '-', '.', '/']:
        s = s.replace(c, '_')

    # "[some]___article's_title__"
    # "some___articles_title__"
    s = re.sub('\W', '', s)

    # "some___articles_title__"
    # "some   articles title  "
    s = s.replace('_', ' ')

    # "some   articles title  "
    # "some articles title "
    s = re.sub('\s+', ' ', s)

    # "some articles title "
    # "some articles title"
    s = s.strip()

    # "some articles title"
    # "some-articles-title"
    s = s.replace(' ', '-')

    return s

def handle(event, context={}):
    logger.info("Received event: " + json.dumps(event, indent=2))

    diaries = client.db['diary']
    diary_id = event["diary_id"]
    entry = {
        "_id": slugify(event["title"]),
        "title": event["title"],
        "body": event["body"],
        "created": datetime.datetime.utcnow(),
    }

    resp = {}
    resp['isBase64Encoded'] = False
    resp['headers'] = {}

    created = create_diary_entry(diaries, diary_id, entry)
    if created is not None:
        resp['statusCode'] = 204
        resp['body'] = json.dumps(created, default=json_unknown_type_handler)
        return resp
    else:
        raise DiaryDoesNotExist("Diary with id {} does not exist".format(diary_id))


def create_diary_entry(diaries, diary_id, entry):
    diaries.update_one(
	    {'_id': ObjectId(diary_id)},
	    { '$push': { 'entries': entry } })

    result = list(diaries.aggregate([
            {'$match': {'_id': ObjectId(diary_id)}},
            {
                '$project': {
                    'entries': {
                        '$filter': {
                            'input': "$entries",
                            'as': "entry",
                            'cond': { '$eq': [ "$$entry.slug", entry['_id'] ] }
                        }
                    }
                }
            }]))

    return result[0] if len(result) > 0 else None

def json_unknown_type_handler(x):
    """
    JSON cannot serialize decimal, datetime and ObjectId.
    """
    if isinstance(x, bson.ObjectId) or isinstance(x, datetime.datetime):
        return str(x)
    raise TypeError("Unknown type")
