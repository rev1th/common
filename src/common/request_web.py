
import requests
import json

URL_STATUS_OK = 200
TIMEOUT_SECS = 20

def url_get(url: str, params: dict[str, any] = None, headers: dict[str, any] = None):
    resp = requests.get(url, params=params, timeout=TIMEOUT_SECS, headers=headers)
    if resp.status_code == URL_STATUS_OK:
        return resp.content.decode()
    else:
        raise Exception(f'{resp.url} URL request failed {resp.reason}')
    # with urlreq.urlopen(url, timeout=TIMEOUT_SECS) as u:
    #     if u.status == URL_STATUS_OK:
    #         return u.read().decode()
    #     else:
    #         raise Exception(f'{u.url} URL request failed {u.reason}')

def url_post(url: str, params: dict[str, any] = None):
    resp = requests.post(url, params=params, timeout=TIMEOUT_SECS)
    if resp.status_code == URL_STATUS_OK:
        return resp.content.decode()
    else:
        raise Exception(f'{resp.url} URL request failed {resp.reason}')

def get_json(content):
    return json.loads(content)
