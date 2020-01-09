from utils import yujson

#   Version
def yuversion():
    yu_json = yujson.yujson(r'/home/openeyes-master/version/version.json')
    version = yu_json.openjson()
    return version