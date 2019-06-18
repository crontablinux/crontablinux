import json
from django.http import HttpResponse


def api_response(code, msg='', data=''):
    if msg:
        response_dict = dict(code=code, data=data, msg=msg)
    else:
        response_dict = dict(code=code, data=data)
    return HttpResponse(json.dumps(response_dict), content_type='application/json')