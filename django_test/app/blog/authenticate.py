import json
import jwt
import datetime
from django.core.exceptions import PermissionDenied
from config.settings import SECRET_KEY
from uuid import UUID


class UUIDEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, UUID):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


def create_access_token(id, permissions):
    return jwt.encode({
        'user_id': json.dumps(id, cls=UUIDEncoder),
        'permissions': list(permissions),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=1000),
        'iat': datetime.datetime.utcnow()
    }, SECRET_KEY, algorithm='HS256')


def decode_access_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')
        return json.loads(payload['user_id']), payload['permissions']
    except AttributeError:
        raise PermissionDenied('unauthenticated')


def create_refresh_token(id):
    return jwt.encode({
        'user_id': json.dumps(id, cls=UUIDEncoder),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(weeks=1000),
        'iat': datetime.datetime.utcnow()
    }, SECRET_KEY, algorithm='HS256')


def decode_refresh_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms='HS256')

        return payload['user_id']
    except AttributeError:
        raise PermissionDenied('unauthenticated')
