# This code sample uses the 'requests' library:
# http://docs.python-requests.org

import argparse
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.auth import HTTPBasicAuth

parser = argparse.ArgumentParser()
parser.add_argument("-un", "--username", type=str, required=True,
                    help="Your Jira email id. Script is tested with admin access")
parser.add_argument("-pw", "--password", type=str, required=True,
                    help="Your Jira API token.")
parser.add_argument("-ht", "--host", type=str, required=True,
                    help="Jira host url. eg: https://www.google.atlassian.net")
parser.add_argument("-skey", '--sourkey', type=str, required=True,
                    help="Project key of old project")
parser.add_argument("-dkey", '--destkey', type=str, required=True,
                    help="project key for new project")
parser.add_argument("-c", "--clean", type=bool, required=False, default=True,
                    help="Set this flag to try if you want to delete all issues " +
                         "and fix versions in destination project before creating " +
                         "anything new")

args = parser.parse_args()
url = args.host

auth = HTTPBasicAuth(args.username, args.password)

headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}

issue_map = {}
non_migrated_issue = {}

# status -> transition id
transition_map = {}


def transitions(sample_issue_key):
    if len(transition_map) > 0:
        return

    response = requests.request(
        "GET",
        url + "/rest/api/2/issue/{}/transitions".format(sample_issue_key),
        headers=headers,
        auth=auth
    )

    data = response.json()
    for tsn in data["transitions"]:
        transition_map[tsn["name"].upper()] = tsn["id"]


def field_exist(obj, field):
    return True if obj.get(field) and obj.get(field) is not None else False


# Create All fix versions
def create_fix_versions():
    response = requests.request(
        "GET",
        url + "/rest/api/2/project/" + args.sourkey + "/versions",
        headers=headers,
        auth=auth
    )

    print("Found {} released in your source projects. Duplicating them.".format(len(response.json())))

    for release in response.json():
        data = {
            "description": release["description"],
            "name": release["name"],
            "archived": release["archived"],
            "released": release["released"],
            "project": args.destkey
        }

        response = requests.request(
            "POST",
            url + "/rest/api/2/version",
            headers=headers,
            auth=auth,
            json=data
        )

        if response.status_code > 300:
            print("Error in creating release", response.json()["errors"])

        print("Created release", data["name"])


def create_issues(issue_type):
    start_at = 0
    max_results_requested = 50
    result_received = max_results_requested
    while max_results_requested == result_received:
        print("retrieving {} {} from {}".format(max_results_requested, issue_type, start_at))
        search_url = url + "/rest/api/2/search?jql=project={} AND issuetype={}&startAt={}&maxResults={}".format(
            args.sourkey,
            issue_type,
            start_at,
            max_results_requested)

        response = requests.request(
            "GET",
            search_url,
            headers=headers,
            auth=auth
        )

        data = response.json()
        result_received = len(data["issues"])
        start_at = start_at + result_received

        keys = []
        for issue in data["issues"]:
            keys.append(issue["key"])

        if len(keys) > 0:
            with ThreadPoolExecutor() as executor:
                executor.map(migrate_issue, keys)


def migrate_comment(issue_key):
    start_at = 0
    max_results_requested = 10
    result_received = max_results_requested
    while max_results_requested == result_received:
        response = requests.request(
            "GET",
            url + "/rest/api/2/issue/{}/comment".format(str(issue_key)),
            headers=headers,
            auth=auth,
        )

        data = response.json()
        result_received = len(data["comments"])
        start_at = start_at + result_received

        for comment in data["comments"]:
            response = requests.request(
                "POST",
                url + "/rest/api/2/issue/{}/comment".format(issue_map[issue_key]),
                headers=headers,
                auth=auth,
                json={"body": comment["body"]}
            )

            if response.status_code > 201:
                print("Error in adding comment. Please file a bug if you think this is a bug", response.json(),
                      issue_map[issue_key], comment)
                non_migrated_issue[issue_key] = response.json()
                return
            print("Added comment in ", issue_map[issue_key])


def migrate_issue(issue_key):
    if issue_map.keys():
        print("Issue {} is already created. Ignoring it", issue_key)

    response = requests.request(
        "GET",
        url + "/rest/api/2/issue/" + str(issue_key),
        headers=headers,
        auth=auth
    )

    issue_fields = response.json()['fields']
    issue_key = response.json()['key']

    data = {
        'fields': {
            "summary": issue_fields["summary"],
            "description": issue_fields["description"],
            "issuetype": {
                "name": issue_fields['issuetype']['name']
            },
            "project": {
                "key": args.destkey
            },
        }
    }

    if field_exist(issue_fields, "customfield_10024"):
        data['fields']["customfield_10016"] = issue_fields["customfield_10024"]

    if field_exist(issue_fields, "priority"):
        data['fields']["priority"] = {"name": issue_fields["priority"]["name"]}

    fix_versions = list()
    for version in issue_fields["fixVersions"]:
        fix_versions.append({"name": version["name"]})

    if len(fix_versions) > 0:
        data['fields']["fixVersions"] = fix_versions

    if len(issue_fields["labels"]) > 0:
        data['fields']["labels"] = issue_fields["labels"]

    if field_exist(issue_fields, "assignee") and issue_fields["assignee"]["active"]:
        data['fields']["assignee"] = {"id": issue_fields["assignee"]["accountId"]}

    if field_exist(issue_fields, "reporter") and issue_fields["reporter"]["active"]:
        data['fields']["reporter"] = {"id": issue_fields["reporter"]["accountId"]}

    if field_exist(issue_fields, "parent"):
        data['fields']["parent"] = {"key": issue_map[issue_fields["parent"]["key"]]}

    response = requests.request(
        "POST",
        url + "/rest/api/2/issue",
        headers=headers,
        auth=auth,
        json=data
    )

    if response.status_code > 201:
        print("Error in creating issue. Please file a bug if you think this is a bug", issue_key, response.json(),
              data)
        non_migrated_issue[issue_key] = response.json()
        return

    key = response.json()["key"]
    print("Created issue {} for {}".format(key, issue_key))

    issue_map[issue_key] = key
    transition(key, issue_fields["status"]["name"])
    migrate_comment(issue_key)


def transition(issue_key, status):
    transitions(issue_key)
    data = {
        "transition": {
            "id": transition_map[status.upper()]
        }
    }

    response = requests.request(
        "POST",
        url + "/rest/api/2/issue/{}/transitions".format(issue_key),
        headers=headers,
        auth=auth,
        json=data
    )

    if response.status_code > 201:
        print("Error in transitioning issue. Please file a bug if you think this is a bug", issue_key, response.json(),
              data)
        non_migrated_issue[issue_key] = response.json()

    print("migrated {} to {}", issue_key, status)


def delete_release(release):
    response = requests.request(
        "DELETE",
        url + "/rest/api/2/version/" + release["id"],
        headers=headers,
        auth=auth
    )

    if response.status_code >= 400:
        print("Unable to delete release", release["name"], response.json())

    print("Deleted release", release["name"])


def delete_issue(issue):
    response = requests.request(
        "DELETE",
        url + "/rest/api/2/issue/" + issue["key"],
        headers=headers,
        auth=auth
    )

    if response.status_code >= 400:
        print("Unable to delete ssue", issue["key"], response.json())

    print("Deleted issue", issue["key"])


def clean_project():
    if not args.clean:
        print("Clean flag is off.")
        return

    response = requests.request(
        "GET",
        url + "/rest/api/2/project/" + args.destkey + "/versions",
        headers=headers,
        auth=auth
    )

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(delete_release, response.json())

    start_at = 0
    max_results_requested = 100
    result_received = 100
    while max_results_requested == result_received:
        search_url = url + "/rest/api/2/search?jql=project={}&startAt={}&maxResults={}".format(
            args.destkey,
            start_at,
            max_results_requested)

        response = requests.request(
            "GET",
            search_url,
            headers=headers,
            auth=auth
        )

        data = response.json()
        result_received = len(data["issues"])
        start_at = start_at + result_received

        with ThreadPoolExecutor() as executor:
            executor.map(delete_issue, data["issues"])


clean_project()

create_fix_versions()

for issue_type in ["Epic", "Story", "Task", "Bug", "Sub-task"]:
    try:
        create_issues(issue_type)
    except Exception as e:
        print('error in creating issue', e)

with open('migration.csv', 'w') as f:
    for key in issue_map.keys():
        f.write("%s,%s\n" % (key, issue_map[key]))

with open('errors.csv', 'w') as f:
    for key in non_migrated_issue.keys():
        f.write("%s,%s\n" % (key, non_migrated_issue[key]))

parting_msg = "{} issues are not migrated because of some error. If number of issues are less," \
              " you can go ahead and migrate them manually from Jira UI. If count is large and error " \
              "can be solved programmatically, Please raise a bug.\n"
print(parting_msg.format(len(non_migrated_issue)))
