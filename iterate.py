# This code sample uses the 'requests' library:
# http://docs.python-requests.org

import argparse

import requests
from requests.auth import HTTPBasicAuth

parser = argparse.ArgumentParser()
parser.add_argument("-un", "--username", type=str, required=True)
parser.add_argument("-pw", "--password", type=str, required=True)
parser.add_argument("-ht", "--host", type=str, required=True)
parser.add_argument("-fm", "--from", type=int, required=True)
parser.add_argument("-to", "--to", type=int, required=True)
parser.add_argument("-skey", '--sourkey', type=str, required=True)
parser.add_argument("-dkey", '--destkey', type=str, required=True)

args = parser.parse_args()
url = args.host + "/rest/api/2/issue/"

auth = HTTPBasicAuth(args.username, args.password)

headers = {
    "Accept": "application/json"
}

issue_list = list(range(0, 10))

for issue_id in issue_list:
    response = requests.request(
        "GET",
        url + 'QWN-' + str(issue_id),
        headers=headers,
        auth=auth
    )

    print('Got status code', response.status_code, response.request.path_url)
