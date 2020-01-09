from utils import yujson

#   OEM
def yuoem():
    yu_json = yujson.yujson(r'/home/openeyes-master/oem/oem.json')
    oem = yu_json.openjson()
    return oem