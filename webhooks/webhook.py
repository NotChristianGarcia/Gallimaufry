import os
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# from context get URL from link info
URL=os.getenv('URL')
EVENT_MSG=os.getenv('EVENT_MSG')

# Environment variables, defaults to 3 or 5 if unset
RETRIES_VAR=int(os.getenv('RETRIES_VAR', 3))
TIMEOUT_VAR=int(os.getenv('TIMEOUT_VAR', 5))

# hook
def requests_retry_session(
    retries=RETRIES_VAR, 
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


s = requests.Session()
s.auth = ('user', 'pass')
s.headers.update({'x-test': 'true'})

try:
    res = requests_retry_session().post(
        URL,
        data=EVENT_MSG,
        timeout=TIMEOUT_VAR)
except Exception as e:
    print('Error:', e)
