import json

def loads(s):
    if isinstance(s, (bytes, bytearray)):
        return json.loads(s.decode("utf-8"))
    elif isinstance(s, str):
        return json.loads(s)

def dumps(*args, **kwargs):
    return json.dumps(*args, **kwargs)
