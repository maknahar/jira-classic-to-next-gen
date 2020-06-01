# jira-classic-to-next-gen
Jira does not support CSV import facility in next gen project. This script allows you to migrate a classic project to next gen project.

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
- Create all the workflow status lanes in the next jane project and make sure name is matching the statuses exactly. By default, Jira next gen comes with TO DO, In Progress and DONE statuses. Jira does not support creating workflows and new status in workflows programmatically.
- Jira next gen does not support multiple start and end status. So move all your card to one end status in Jira classic project. Otherwise, You will see unusually high number od cards in the backlog of next gen project.
- By default, this script cleans next gen project before starting. Using an existing project to migrate to is not recommended.