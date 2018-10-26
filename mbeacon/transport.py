import pickle
try:
    import simplejson as json
except ImportError:
    import json


class Ascii(object):
    """Simple ASCII format to send info"""
    def dumps(self, data):
        return "|".join(data).encode('utf-8')
    def loads(self, msg):
        return msg.decode('utf-8').split("|")


class Json(object):
    """Use json to transport message"""
    def dumps(self, data):
        return json.dumps(data).encode('utf-8')
    def loads(self, msg):
        return json.loads(msg.decode('utf-8'))


class Pickle(object):
    """Use pickle to transport message"""
    def dumps(self, data):
        return pickle.dumps(data)
    def loads(self, msg):
        return pickle.loads(msg)
