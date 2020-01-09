import json

from audits.models import Alert


class yuoperalog(object):
    def __init__(self, user_id):
        self.user_id = user_id

    def alertGet(self):
        alert = []
        yualert = Alert.objects.filter(user_id = self.user_id).first()
        if yualert:
            if yualert.alert:
                alert = list(eval(yualert.alert))
                Alert.objects.filter(user_id = self.user_id).update(alert='')
        return json.dumps(alert)

    def alertSet(self, state, head, body, timeout=4000, show='slideDown'):
        yualert = Alert.objects.filter(user_id = self.user_id).first()
        if yualert:
            if yualert.alert:
                alert = list(eval(yualert.alert))
                alert.append({'state':state, 'head':head, 'body':body, 'timeout':timeout, 'show':show})
                Alert.objects.filter(user_id = self.user_id).update(alert=alert)
            else:
                Alert.objects.filter(user_id = self.user_id).update(alert=[{'state':state, 'head':head, 'body':body, 'timeout':timeout, 'show':show}])