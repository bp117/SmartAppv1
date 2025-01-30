import os
import git
from jira import JIRA
import requests

# Configuration
JIRA_URL = 'https://your-jira-instance.atlassian.net'
JIRA_EMAIL = 'your-email@example.com'
JIRA_API_TOKEN = 'your-api-token'
GITHUB_REPO_OWNER = 'your-github-username'
GITHUB_REPO_NAME = 'your-repo-name'
GITHUB_TOKEN = 'your-github-token'
GIT_CLONE_DIR = '/path/to/clone/directory'

# Initialize Jira Client
jira_options = {'server': JIRA_URL}
jira = JIRA(options=jira_options, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# Function to clone the repository
def clone_repository():
    repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}.git'
    if not os.path.exists(GIT_CLONE_DIR):
        os.makedirs(GIT_CLONE_DIR)
    repo = git.Repo.clone_from(repo_url, GIT_CLONE_DIR)
    return repo

# Function to make code changes
def make_code_changes(repo, jira_description, attachments):
    # Example: Modify a README file with Jira description
    readme_path = os.path.join(GIT_CLONE_DIR, 'README.md')
    with open(readme_path, 'a') as f:
        f.write(f'\n\n## Jira Description\n{jira_description}\n')
    
    # Add and commit changes
    repo.index.add([readme_path])
    repo.index.commit('Update README with Jira description')

# Function to create a PR
def create_pr(branch_name, title, body):
    url = f'https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/pulls'
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }
    data = {
        'title': title,
        'head': branch_name,
        'base': 'main',  # or whatever your default branch is
        'body': body,
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()

# Function to update Jira with comments
def update_jira_with_comment(issue_key, comment):
    jira.add_comment(issue_key, comment)

# Main function
def main(issue_key):
    issue = jira.issue(issue_key)
    jira_description = issue.fields.description
    attachments = issue.fields.attachment

    # Clone the repository
    repo = clone_repository()

    # Create a new branch
    branch_name = f'feature/{issue_key}'
    repo.git.checkout('HEAD', b=branch_name)

    # Make code changes
    make_code_changes(repo, jira_description, attachments)

    # Push changes to remote
    origin = repo.remote(name='origin')
    origin.push(branch_name)

    # Create a PR
    pr_response = create_pr(branch_name, f'Fix for {issue_key}', jira_description)
    pr_url = pr_response['html_url']

    # Update Jira with PR URL
    update_jira_with_comment(issue_key, f'Created PR: {pr_url}')

if __name__ == '__main__':
    issue_key = 'PROJECT-123'  # Replace with your Jira issue key
    main(issue_key)
