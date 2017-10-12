from json import JSONEncoder

class JsonSerializable:
    # Return a JSON serializable object (list, dict, string, number)
    def __json__(self):
        raise "Implement __json__()"

class MyJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, JsonSerializable):
            return obj.__json__()
        else:
            return json.JSONEncoder.default(self, obj)

