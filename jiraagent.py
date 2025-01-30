from langchain.graphs import langgraph
from jira import JIRA
import openai
from playwright.sync_api import sync_playwright

# Step 1: Initialize Jira Client
jira = JIRA(server="https://your-jira-instance.atlassian.net", basic_auth=("your-email", "your-api-token"))

# Step 2: Initialize OpenAI Client
openai.api_key = "your-openai-api-key"

# Step 3: Define Functions for Each Node in the Graph

def fetch_jira_issue(issue_key):
    """Fetch Jira issue details."""
    issue = jira.issue(issue_key)
    return {
        "issue_key": issue.key,
        "summary": issue.fields.summary,
        "description": issue.fields.description,
        "attachments": [att.filename for att in issue.fields.attachment]
    }

def refine_story(description):
    """Refine the story using OpenAI GPT."""
    prompt = f"""
    Refine the following user story based on INVEST principles:
    - Add clear acceptance criteria.
    - Write BDD-style test cases (Given, When, Then).

    User Story Description:
    {description}

    Refined Story:
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def update_jira_issue(issue_key, refined_story):
    """Update the Jira issue with the refined story."""
    issue = jira.issue(issue_key)
    issue.update(fields={"description": refined_story})
    return {"issue_key": issue_key, "status": "updated"}

def replay_steps_with_playwright(issue_key, description, refined_story):
    """Replay steps in a browser using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open Jira issue
        page.goto(f"https://your-jira-instance.atlassian.net/browse/{issue_key}")
        page.wait_for_selector("h1[data-testid='issue.views.issue-base.foundation.summary.heading']")

        # Simulate refining the story
        print(f"Original Description: {description}")
        print(f"Refined Story: {refined_story}")

        # Update Jira issue
        page.click("button[aria-label='Edit']")
        page.fill("textarea[data-testid='issue.views.field.description.edit']", refined_story)
        page.click("button[data-testid='issue.views.field.description.save']")

        browser.close()
    return {"issue_key": issue_key, "replay_status": "completed"}

# Step 4: Define the Workflow Using langGraph

def build_workflow():
    graph = langgraph.Graph()

    # Add nodes
    graph.add_node("fetch_jira_issue", fetch_jira_issue)
    graph.add_node("refine_story", refine_story)
    graph.add_node("update_jira_issue", update_jira_issue)
    graph.add_node("replay_steps_with_playwright", replay_steps_with_playwright)

    # Define edges
    graph.add_edge("fetch_jira_issue", "refine_story")
    graph.add_edge("refine_story", "update_jira_issue")
    graph.add_edge("update_jira_issue", "replay_steps_with_playwright")

    # Set entry point
    graph.set_entry_point("fetch_jira_issue")

    # Compile the graph
    return graph.compile()

# Step 5: Execute the Workflow

def main():
    # Build the workflow
    workflow = build_workflow()

    # Input data
    issue_key = "PROJ-123"

    # Run the workflow
    result = workflow.invoke({"fetch_jira_issue": {"issue_key": issue_key}})
    print("Workflow Completed:", result)

if __name__ == "__main__":
    main()
