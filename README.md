# Jira classic to Next Gen Migration
Jira does not support CSV import facility in next gen project. This script allows you to migrate a classic project to next gen project.

### Dependency
- Python > 3.7

### Supported migration
- Epics
- Stories
- Tasks
- Bugs
- Sub-tasks
- Releases
- Comments

### Preparation
- Take backup of classic project
- Generate the Jira API token
- Create a next gen project in Jira
- Get admin access to the next gen project.
- Either make your next gen project public or add all the user manually who have either a assignee or reporter of issue in classic project.
- Jira does not enable all feature in next gen project by default. Enabled the all the features if you are not sure which one you need.
- Create all issue types available in classic project in next gen project as well. This setting is available in `project Setting` -> `Issue Types`. It is important issue names match exactly.
- Make sure your screen elements for issue types are matching in classic and next gen project. This setting is available in `project Setting` -> `Issue Types` -> `Select Type to edit`. e.g If old project has field summary enabled in the screen, enable it for new project as well. To make this easier, just before migration enable all elements for all card type. You can refine them after migration as well in Jira UI.
- Create all the workflow status lanes in the next jane project and make sure name is matching the statuses exactly. By default, Jira next gen comes with TO DO, In Progress and DONE statuses. Jira does not support creating workflows and new status in workflows programmatically.
- Jira next gen does not support multiple start and end status. So move all your card to one end status in Jira classic project. Otherwise, You will see unusually high number of cards in the backlog of next gen project.
- Disable notifications for the project so assignees and reporter of issues does not get spammed while this script create thousands of issues for you in new project.

### Note
- By default, this script cleans next gen project before starting. Using an existing project to migrate to is not recommended.
- Jira API does not allow a deactivated user as assignee or reporter while creating issue. This script will keep the assignee blank and person running this script will become the reporter in these cases.
- If there is no error, allmigrated issues would be listed in `migration.csv` and non migrated one in `error.csv`.
