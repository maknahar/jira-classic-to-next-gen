# Jira classic to Next Gen Migration
Jira does not support CSV import facility in next gen project. Moving epics and issues manually from UI is cumbursome and time consuming. If you are in a situation where you need to migrate projects with thousands of issues, it is physically not possible. Also, Card migration does not migrate essential things like estimate and epic to issue linking.

This script allows you to migrate a classic project to next gen project in a automatic way while preserving all the information.

### Dependency
- Python > 3.7

### Supported migration
This script copy following data from classic project to next gen project
- Epics
- Stories
- Tasks
- Bugs
- Sub-tasks
- Story Points
- Epic to Stories connection
- Stories to Sub tasks linking
- Releases
- Releases to story connections
- Comments
- Tags
- Assignee and reporters

### Prerequisite
- Take backup of classic project
- Generate the Jira API token
- Create a next gen project in Jira if not created already
- Get admin access to the next gen project.
- Either make your next gen project public or add all the user manually who is either an assignee or reporter of any issue in classic project.
- Jira does not enable all feature in next gen project by default. Enabled the all the features if you are not sure which one you need.
- Create all issue types available in classic project in next gen project as well. This setting is available in `project Setting` -> `Issue Types`. It is important issue names match exactly.
- Make sure your screen elements for issue types are matching in classic and next gen project. This setting is available in `project Setting` -> `Issue Types` -> `Select Type to edit`. e.g If old project has field summary enabled in the screen, enable it for new project as well. To make this easier, just before migration enable all elements for all card type. You can refine them after migration as well in Jira UI.
- Create all the workflow status lanes in the next-gen project and make sure name is matching the statuses exactly. By default, Jira next gen comes with TO DO, In Progress and DONE statuses. Jira does not support creating workflows and new status in workflows programmatically.

### Recommendations
- Jira next gen does not support multiple start and end status. So move all your card to one end status in Jira classic project. Otherwise, You will see unusually high number of cards in the backlog of next gen project.
- Disable notifications for the next-gen project so assignees and reporter of issues does not get spammed while this script create thousands of issues for you in new project.

### Notes
- This script **DOES NOT MODIFY OR DELETE ANY DATA IN THE CLASSSIC PROJECT**. By the end of successful run of the script, you get a next gen project with same data as classic project. To ensure this, you may want to limit the access to viewer level in the classic project. 
- It is safe to run the script again if you think migration has not been done correctly due to some configuration issue.
- By default, this script cleans next gen project before starting. Using an existing project to migrate to is not recommended.
- Jira API does not allow a deactivated user as assignee or reporter while creating issue. This script will keep the assignee blank and person running this script will become the reporter in these cases.
- If there is no error, all migrated issues would be listed in `migration.csv` and non migrated one in `error.csv`.

### How To Execute

#### Command:

`python migrate.py -un {your_email_id} -pw {api_token} -ht {your_jira_host_name} -skey {key_of_classic_project} -dkey {key_of_next_gen_project}`

#### Example:

```
> python migrate.py -un maknahar@google.com -pw abc123xyz@1# -ht https://google.atlassian.net -skey GD -dkey GP
2020-06-06 03:09:47,951 INFO: Found 47 releases in new project. Deleting them
Progress: |██████████████████████████████████████████████████| 100.0% Complete
2020-06-06 03:09:55,057 INFO: Deleting 100 issues in next gen project from index 0
Progress: |██████████████████████████████████████████████████| 100.0% Complete
.
.
.
2020-06-06 03:10:46,880 INFO: Deleting 4 issues in next gen project from index 300
Progress: |██████████████████████████████████████████████████| 100.0% Complete
2020-06-06 03:10:47,812 INFO: Found 47 released in your source projects. Migrating them.
Progress: |██████████████████████████████████████████████████| 100.0% Complete
2020-06-06 03:10:59,221 INFO: Migrating 100 Epic from 0
Progress: |██████████████████████████████████████████████████| 100.0% Complete
2020-06-06 03:12:04,155 WARNING: Received 63 issues for Epic in last batch
Progress: |██████████████████████████████████████████████████| 100.0% Complete
2020-06-06 03:12:59,412 INFO: Migrating 100 Story from 0
Progress: |██████████████████████████████████████████████████| 100.0% Complete
.
.
.
2020-06-06 03:24:14,339 WARNING: Received 1 issues for Sub-task in last batch
Progress: |██████████████████████████████████████████████████| 100.0% Complete
2020-06-06 03:24:16,267 INFO: 2468 issues migrated successfully. 2 issues are not migrated fully or partially because of some error. If number of issues are less, you can go ahead and migrate/update them manually from Jira UI. If count is large and error can be solved programmatically, Please raise a bug.
```

### Support
I have migrated projects with thousands of issues and hundreds of releases/sprints. However, as Jira allows a lot of customizations, those customization will not be captured in this script. If you need support or require some custom change in the script for your project. You may reach out to me at maknahar@live.in. I will try to respond as soon as possible.
