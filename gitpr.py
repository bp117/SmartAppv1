import os
import git
from jira import JIRA
import requests
import logging
from datetime import datetime
from google.cloud import aiplatform

# Configuration
JIRA_URL = 'https://your-jira-instance.atlassian.net'
JIRA_EMAIL = 'your-email@example.com'
JIRA_API_TOKEN = 'your-api-token'
GITHUB_REPO_OWNER = 'your-github-username'
GITHUB_REPO_NAME = 'your-repo-name'
GITHUB_TOKEN = 'your-github-token'
GIT_CLONE_DIR = '/path/to/clone/directory'
VERTEX_PROJECT_ID = 'your-gcp-project-id'
VERTEX_LOCATION = 'us-central1'
GEMINI_MODEL_ID = 'your-gemini-model-id'

# Setup Logging
logging.basicConfig(
    filename='agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Jira Client
jira_options = {'server': JIRA_URL}
jira = JIRA(options=jira_options, basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN))

# Initialize Vertex AI Client
client = aiplatform.gapic.PredictionServiceClient(client_options={"api_endpoint": f"{VERTEX_LOCATION}-aiplatform.googleapis.com:443"})

# Function to clone the repository
def clone_repository():
    repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}.git'
    try:
        if not os.path.exists(GIT_CLONE_DIR):
            os.makedirs(GIT_CLONE_DIR)
        repo = git.Repo.clone_from(repo_url, GIT_CLONE_DIR)
        logging.info(f'Repository cloned successfully to {GIT_CLONE_DIR}')
        return repo
    except Exception as e:
        logging.error(f'Failed to clone repository: {e}')
        raise

# Function to make code changes based on Gemini model output
def make_code_changes(repo, issue_key, jira_description, acceptance_criteria, attachments):
    try:
        # Prepare prompt for Gemini model
        prompt = (
            f"Based on the following Jira description and acceptance criteria, determine the specific code changes needed:\n"
            f"Jira Description:\n{jira_description}\n\n"
            f"Acceptance Criteria:\n{acceptance_criteria}\n\n"
            f"Attachments:\n"
        )
        for attachment in attachments:
            prompt += f"- {attachment.filename}\n"

        # Call Gemini model
        endpoint_id = GEMINI_MODEL_ID
        location = VERTEX_LOCATION
        parent = f"projects/{VERTEX_PROJECT_ID}/locations/{location}/endpoints/{endpoint_id}"

        response = client.predict(
            endpoint=parent,
            instances=[{"text": prompt}],
            parameters={"temperature": 0.2, "max_output_tokens": 1024},
        )

        # Extract response
        code_changes = response.predictions[0]["content"]
        logging.info(f'Gemini model response: {code_changes}')

        # Apply code changes
        # This is a placeholder for applying the code changes. You need to parse the code_changes string and apply it to the correct files.
        # For demonstration, let's assume the code_changes string contains instructions to modify a specific file.
        # Example: "Modify file1.py by adding a new function `def new_function(): pass`"
        # You need to implement the logic to parse and apply these changes.

        # Example: Modify a README file with Jira description and acceptance criteria
        readme_path = os.path.join(GIT_CLONE_DIR, 'README.md')
        with open(readme_path, 'a') as f:
            f.write(f'\n\n## Jira Description for {issue_key}\n{jira_description}\n')
            f.write(f'\n## Acceptance Criteria for {issue_key}\n{acceptance_criteria}\n')
        
        # Process attachments
        for attachment in attachments:
            attachment_url = attachment.content
            attachment_filename = os.path.join(GIT_CLONE_DIR, attachment.filename)
            response = requests.get(attachment_url, auth=(JIRA_EMAIL, JIRA_API_TOKEN))
            if response.status_code == 200:
                with open(attachment_filename, 'wb') as f:
                    f.write(response.content)
                repo.index.add([attachment_filename])
                logging.info(f'Attachment {attachment.filename} added successfully.')
            else:
                logging.error(f'Failed to download attachment {attachment.filename}: {response.status_code}')
        
        # Add and commit changes
        repo.index.add([readme_path])
        repo.index.commit(f'Update README and add attachments for {issue_key}')
        logging.info(f'Code changes committed successfully for {issue_key}')
    except Exception as e:
        logging.error(f'Failed to make code changes: {e}')
        raise

# Function to push changes to a new branch
def push_changes_to_new_branch(repo, branch_name):
    try:
        origin = repo.remote(name='origin')
        origin.push(branch_name)
        logging.info(f'Changes pushed to branch {branch_name} successfully')
    except Exception as e:
        logging.error(f'Failed to push changes to branch {branch_name}: {e}')
        raise

# Function to create a PR
def create_pr(branch_name, title, body):
    try:
        url = f'https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/pulls'
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json',
        }
        data = {
            'title': title,
            'head': branch_name,
            'base': 'main',  # Assuming 'main' is your default branch
            'body': body,
        }
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        logging.info(f'PR created successfully: {response.json()["html_url"]}')
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        logging.error(f'HTTP error occurred while creating PR: {http_err}')
        raise
    except Exception as e:
        logging.error(f'Failed to create PR: {e}')
        raise

# Function to update Jira with comments
def update_jira_with_comment(issue_key, comment):
    try:
        jira.add_comment(issue_key, comment)
        logging.info(f'Comment added to Jira issue {issue_key} successfully')
    except Exception as e:
        logging.error(f'Failed to update Jira issue {issue_key} with comment: {e}')
        raise

# Main function
def main(issue_key):
    try:
        logging.info(f'Starting process for issue {issue_key}')
        issue = jira.issue(issue_key)
        jira_description = issue.fields.description
        acceptance_criteria = issue.fields.customfield_12345  # Replace with the actual custom field ID for acceptance criteria
        attachments = issue.fields.attachment

        # Clone the repository
        repo = clone_repository()

        # Create a new branch
        branch_name = f'feature/{issue_key}'
        repo.git.checkout('HEAD', b=branch_name)
        logging.info(f'Created and checked out branch {branch_name}')

        # Make code changes
        make_code_changes(repo, issue_key, jira_description, acceptance_criteria, attachments)

        # Push changes to the new branch
        push_changes_to_new_branch(repo, branch_name)

        # Create a PR
        pr_response = create_pr(branch_name, f'Fix for {issue_key}', jira_description)
        pr_url = pr_response['html_url']

        # Update Jira with PR URL
        update_jira_with_comment(issue_key, f'Created PR: {pr_url}')
        logging.info(f'Process completed successfully for issue {issue_key}')
    except Exception as e:
        logging.error(f'An error occurred during the process for issue {issue_key}: {e}')

if __name__ == '__main__':
    issue_key = 'PROJECT-123'  # Replace with your Jira issue key
    main(issue_key)
