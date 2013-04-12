# -*- coding: utf-8 -*-
'''
Created on Aug 17, 2011

@author: jklo
'''
# MIT licensed JWT implementation:  https://github.com/progrium/pyjwt
import jwt
import datetime



__JWT_ALG = "HS256"

def parse_token(serviceid, token):
    decoded = {}
    try:
        decoded = jwt.decode(str(token), str(serviceid), __JWT_ALG)
    except jwt.DecodeError as e:
        decoded = jwt.decode(str(token), verify=False)
        decoded["error"] = e.message

    return decoded


def get_payload(startkey=None, endkey={}, startkey_docid=None, from_date=None, until_date=None, key=None, keys=None, any_tags=None, identity=None):
    payload = {}

    payload["startkey"] = startkey
    payload["endkey"] = endkey

    if key:
        payload["key"] = key

    if keys:
        payload["keys"] = keys

    if startkey_docid:
        payload["startkey_docid"] = startkey_docid

    if any_tags:
        payload['any_tags'] = any_tags

    if identity:
        payload['identity'] = identity

    if from_date and isinstance(from_date, datetime.datetime):
        from lr.lib import helpers as h
        payload["from_date"] = h.convertToISO8601Zformat(from_date)
    if until_date and isinstance(until_date, datetime.datetime):
        payload["until_date"] = h.convertToISO8601Zformat(until_date)

    return payload


def get_offset_payload(offset=None, keys=None, maxResults=None):
    payload = {}

    if offset:
        payload["offset"] = offset
    if keys:
        payload["keys"] = keys
    if maxResults:
        payload["maxResults"] = maxResults

    return payload


def get_token_slice(serviceid, startkey=None, endkey={}, startkey_docid=None, any_tags=None, identity=None, maxResults=None):
    return jwt.encode(get_payload(startkey, endkey, startkey_docid, None, None, None, None, any_tags, identity), serviceid, __JWT_ALG)


def get_token(serviceid, startkey=None, endkey={}, startkey_docid=None, from_date=None, until_date=None, key=None, keys=None, maxResults=None):
    return jwt.encode(get_payload(startkey, endkey, startkey_docid, from_date, until_date, key, keys), serviceid, __JWT_ALG)


def get_offset_token(serviceid, offset=None, keys=None, maxResults=None):
    return jwt.encode(get_offset_payload(offset, keys, maxResults), serviceid, __JWT_ALG)


if __name__ == "__main__":
    from uuid import uuid4
    import json

    params = {
              u'startkey': [u'LODE', None],
              u'endkey': [u'LODE', u'2011-08-12T10:21:04'],
              u'startkey_docid': u'7623e2d6c055481988041e06c156fca8'
              }

    serviceid = uuid4().hex

    token = get_token(serviceid, **params)
    print "Param: %s\n" % repr(params)
    print "Token: %s\n" % token

    parsed = parse_token(serviceid, token)

    assert params == parsed, "Tokens don't match: %s" % repr(parsed)

    params = {
              u'startkey': [u'11, κλάση, εικόνα,', None],
              u'endkey': [u'11, κλάση, εικόνα,', u'2011-08-12T10:21:04'],
              u'startkey_docid': u'7623e2d6c055481988041e06c156fca8'
              }

    serviceid = uuid4().hex

    token = get_token(serviceid, **params)
    print "Unicode Param: %s\n" % repr(params)
    print "Unicode Token: %s\n" % token

    parsed = parse_token(serviceid, token)

    assert params == parsed, "Unicode Tokens don't match: %s" % repr(parsed)







