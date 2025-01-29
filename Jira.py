from langchain import OpenAI, LLMChain
from langchain.prompts import PromptTemplate
from langchain.agents import initialize_agent, Tool
from langchain.tools import BaseTool
import playwright.sync_api as pw
import requests
import os
import git
from github import Github

# Set environment variables or constants for API keys and configuration
JIRA_API_BASE = "https://your-jira-instance.atlassian.net/rest/api/2"
JIRA_USERNAME = "your-email@example.com"
JIRA_API_TOKEN = "your-jira-api-token"
GITHUB_TOKEN = "your-github-token"

# Step 1: Fetch Jira Story and Attachments
def fetch_jira_story(jira_id):
    url = f"{JIRA_API_BASE}/issue/{jira_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    response = requests.get(url, auth=auth)
    response.raise_for_status()
    return response.json()

def fetch_jira_attachments(issue):
    attachments = issue.get("fields", {}).get("attachment", [])
    files = []
    for attachment in attachments:
        response = requests.get(attachment['content'], auth=(JIRA_USERNAME, JIRA_API_TOKEN))
        response.raise_for_status()
        files.append((attachment['filename'], response.content))
    return files

# Step 2: Refine Story with INVEST Principles and Generate Test Cases
class StoryRefinerTool(BaseTool):
    name = "story_refiner"
    description = "Refines a Jira story using INVEST principles, generates acceptance criteria and BDD test cases."

    def __init__(self, llm):
        self.llm = llm

    def _run(self, jira_story):
        prompt = f"Refine the following Jira story based on INVEST principles, generate acceptance criteria, and BDD test cases:\n\n{jira_story}"
        return self.llm(prompt)

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError("Async not supported")

# Step 3: Update Jira Story
def update_jira_story(jira_id, refined_story):
    url = f"{JIRA_API_BASE}/issue/{jira_id}"
    auth = (JIRA_USERNAME, JIRA_API_TOKEN)
    payload = {
        "fields": {
            "description": refined_story
        }
    }
    response = requests.put(url, json=payload, auth=auth)
    response.raise_for_status()

# Step 4: Git Operations
class GitHandler:
    def __init__(self, github_token):
        self.github = Github(github_token)

    def clone_repo(self, repo_url, local_path):
        return git.Repo.clone_from(repo_url, local_path)

    def create_branch_and_commit(self, repo_path, branch_name, file_changes):
        repo = git.Repo(repo_path)
        repo.git.checkout('HEAD', b=branch_name)
        for file_path, content in file_changes.items():
            with open(os.path.join(repo_path, file_path), 'w') as f:
                f.write(content)
        repo.git.add(all=True)
        repo.index.commit("Automated changes by Agentic AI")

    def create_pull_request(self, repo_name, branch_name, pr_title, pr_body):
        repo = self.github.get_repo(repo_name)
        repo.create_pull(title=pr_title, body=pr_body, head=branch_name, base="main")

# Step 5: Automate Browser Actions with Playwright
def showcase_actions(jira_id):
    with pw.sync_api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # Showcase opening Jira story
        page.goto(f"{JIRA_API_BASE.replace('/rest/api/2', '')}/browse/{jira_id}")

        # Simulate GitHub actions
        page.goto("https://github.com")
        page.wait_for_timeout(5000)
        browser.close()

# Combine into LangChain Workflow
def main(jira_id, repo_url, local_path, repo_name):
    llm = OpenAI(model="text-davinci-003")
    story_refiner_tool = StoryRefinerTool(llm=llm)
    agent = initialize_agent(tools=[story_refiner_tool], llm=llm, agent="zero-shot-react-description")

    # Step 1: Fetch Jira story and attachments
    jira_story = fetch_jira_story(jira_id)
    attachments = fetch_jira_attachments(jira_story)

    # Step 2: Refine story
    refined_story = agent.run(jira_story["fields"]["description"])

    # Step 3: Update Jira
    update_jira_story(jira_id, refined_story)

    # Step 4: Git operations
    git_handler = GitHandler(GITHUB_TOKEN)
    git_handler.clone_repo(repo_url, local_path)
    file_changes = {"README.md": "# Updated by Agentic AI"}  # Example changes
    branch_name = f"feature/{jira_id}"
    git_handler.create_branch_and_commit(local_path, branch_name, file_changes)
    git_handler.create_pull_request(repo_name, branch_name, "Automated PR", "This PR was created by Agentic AI.")

    # Step 5: Showcase actions
    showcase_actions(jira_id)

# Example Usage
if __name__ == "__main__":
    main(jira_id="PROJECT-123", repo_url="https://github.com/your-org/your-repo.git", local_path="/tmp/your-repo", repo_name="your-org/your-repo")
