import json

class yujson(object):
    def __init__(self, path):
        self.path = path

    def openjson(self):
        try:
            with open(self.path, 'r') as f:
                json_dict = json.load(f)
            return json_dict
        except Exception as e:
            return ''

    def writejson(self, json_dict):
        json_str = json.dumps(json_dict)
        with open(self.path, 'w', encoding='utf-8') as f:
            f.write(json_str)