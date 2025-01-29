


import os
from typing import Dict, List, Optional
from langgraph.graph import Graph, StateGraph
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_vertexai import VertexAI
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate
from playwright.sync_api import sync_playwright
from git import Repo
import json
from dataclasses import dataclass
from jira import JIRA
from google.cloud import aiplatform
from vertexai.language_models import TextGenerationModel, CodeGenerationModel

# Initialize Vertex AI
aiplatform.init(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

# Data classes remain the same as before
@dataclass
class JiraStory:
    key: str
    summary: str
    description: str
    acceptance_criteria: List[str]
    attachments: List[str]

@dataclass
class CodeChange:
    repo_url: str
    branch_name: str
    files_changed: List[str]
    pr_url: Optional[str] = None

@dataclass
class AgentState:
    jira_story: Optional[JiraStory] = None
    refined_story: Optional[JiraStory] = None
    code_changes: Optional[CodeChange] = None
    messages: List[str] = None
    error: Optional[str] = None

# JiraTools class remains the same
class JiraTools:
    def __init__(self, jira_url: str, username: str, api_token: str):
        self.jira = JIRA(server=jira_url, basic_auth=(username, api_token))

    @tool("read_jira_story")
    def read_jira_story(self, issue_key: str) -> JiraStory:
        """Reads a Jira story and its attachments"""
        issue = self.jira.issue(issue_key)
        attachments = [
            attachment.filename 
            for attachment in issue.fields.attachment
        ]
        return JiraStory(
            key=issue_key,
            summary=issue.fields.summary,
            description=issue.fields.description,
            acceptance_criteria=[],
            attachments=attachments
        )

    @tool("update_jira_story")
    def update_jira_story(self, story: JiraStory) -> bool:
        """Updates a Jira story with refined content"""
        issue = self.jira.issue(story.key)
        issue.update(
            summary=story.summary,
            description=story.description,
            customfield_10001="\n".join(story.acceptance_criteria)
        )
        return True

# Updated Story refinement agent using Gemini
class StoryRefinementAgent:
    def __init__(self):
        # Initialize Gemini Pro model through Vertex AI
        self.llm = VertexAI(
            model_name="gemini-pro",
            max_output_tokens=2048,
            temperature=0.1,
            top_p=0.8,
            top_k=40
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert agile story refinement assistant.
            Analyze the given story and refine it according to INVEST principles:
            - Independent: The story should be self-contained
            - Negotiable: There should be room for discussion
            - Valuable: It must deliver value to stakeholders
            - Estimable: The team should be able to estimate the effort
            - Small: It should be completed within a sprint
            - Testable: Clear criteria for testing
            
            Create detailed acceptance criteria and BDD test cases in Gherkin format.
            
            Return the response in the following JSON format:
            {
                "summary": "refined story summary",
                "description": "refined description",
                "acceptance_criteria": ["criteria1", "criteria2"],
                "bdd_scenarios": [
                    {
                        "feature": "feature description",
                        "scenario": "scenario name",
                        "given": ["given steps"],
                        "when": ["when steps"],
                        "then": ["then steps"]
                    }
                ]
            }"""),
            ("human", "{story_description}")
        ])

    def refine_story(self, story: JiraStory) -> JiraStory:
        response = self.llm.invoke(
            self.prompt.format_messages(
                story_description=f"""
                Summary: {story.summary}
                Description: {story.description}
                Attachments: {story.attachments}
                """
            )
        )
        
        # Parse the response and update the story
        refined_content = json.loads(response.content)
        
        # Convert BDD scenarios to acceptance criteria format
        bdd_criteria = []
        for scenario in refined_content["bdd_scenarios"]:
            bdd_text = f"""Feature: {scenario['feature']}
Scenario: {scenario['scenario']}
Given {' and '.join(scenario['given'])}
When {' and '.join(scenario['when'])}
Then {' and '.join(scenario['then'])}"""
            bdd_criteria.append(bdd_text)
        
        return JiraStory(
            key=story.key,
            summary=refined_content["summary"],
            description=refined_content["description"],
            acceptance_criteria=refined_content["acceptance_criteria"] + bdd_criteria,
            attachments=story.attachments
        )

# Updated Code update agent using Gemini
class CodeUpdateAgent:
    def __init__(self, github_token: str):
        self.github_token = github_token
        # Initialize Gemini Pro for code generation
        self.code_llm = VertexAI(
            model_name="gemini-pro-code",
            max_output_tokens=2048,
            temperature=0.1,
            top_p=0.8,
            top_k=40
        )

    def clone_repo(self, repo_url: str, branch_name: str) -> str:
        """Clones the repository and creates a new branch"""
        repo_path = f"/tmp/{branch_name}"
        repo = Repo.clone_from(
            repo_url,
            repo_path,
            branch="main"
        )
        new_branch = repo.create_head(branch_name)
        new_branch.checkout()
        return repo_path

    def update_code(self, story: JiraStory, repo_url: str) -> CodeChange:
        branch_name = f"feature/{story.key.lower()}"
        repo_path = self.clone_repo(repo_url, branch_name)
        
        # Generate code changes using Gemini Pro Code
        code_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert developer. Generate code changes based on the story requirements.
            Provide the changes in the following JSON format:
            {
                "files": [
                    {
                        "path": "relative/path/to/file",
                        "content": "complete file content with changes",
                        "description": "description of changes"
                    }
                ]
            }"""),
            ("human", f"""
            Story: {story.summary}
            Description: {story.description}
            Acceptance Criteria:
            {chr(10).join(story.acceptance_criteria)}
            """)
        ])
        
        changes_response = self.code_llm.invoke(code_prompt.format_messages())
        changes = json.loads(changes_response.content)
        
        # Apply changes to files
        repo = Repo(repo_path)
        changed_files = []
        
        for file_change in changes["files"]:
            file_path = os.path.join(repo_path, file_change["path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w") as f:
                f.write(file_change["content"])
            
            changed_files.append(file_change["path"])
            repo.index.add(file_change["path"])
        
        # Commit changes
        commit_message = f"""feat({story.key}): {story.summary}

{story.description}

Acceptance Criteria:
{chr(10).join('- ' + ac for ac in story.acceptance_criteria)}"""
        
        repo.index.commit(commit_message)
        
        return CodeChange(
            repo_url=repo_url,
            branch_name=branch_name,
            files_changed=changed_files
        )

# PlaywrightAutomation class remains the same
class PlaywrightAutomation:
    def __init__(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.context = self.browser.new_context()
        self.page = self.context.new_page()

    def simulate_steps(self, story: JiraStory, code_changes: CodeChange):
        # Navigate to Jira
        self.page.goto(f"https://jira.company.com/browse/{story.key}")
        self.page.wait_for_selector(".issue-view")
        
        # Verify story updates
        assert story.summary in self.page.content()
        
        # Navigate to GitHub PR
        if code_changes.pr_url:
            self.page.goto(code_changes.pr_url)
            self.page.wait_for_selector(".pull-request-view")
            
            # Verify PR contents
            assert story.key in self.page.content()

# Main workflow function remains largely the same
def create_workflow(
    jira_tools: JiraTools,
    story_refinement_agent: StoryRefinementAgent,
    code_update_agent: CodeUpdateAgent,
    playwright_automation: PlaywrightAutomation
) -> Graph:
    workflow = StateGraph(AgentState)

    # Define nodes
    def read_story(state: AgentState) -> AgentState:
        story = jira_tools.read_jira_story(state.jira_story.key)
        return AgentState(jira_story=story)

    def refine_story(state: AgentState) -> AgentState:
        refined_story = story_refinement_agent.refine_story(state.jira_story)
        jira_tools.update_jira_story(refined_story)
        return AgentState(jira_story=state.jira_story, refined_story=refined_story)

    def update_code(state: AgentState) -> AgentState:
        code_changes = code_update_agent.update_code(
            state.refined_story,
            "https://github.com/company/repo"
        )
        return AgentState(
            jira_story=state.jira_story,
            refined_story=state.refined_story,
            code_changes=code_changes
        )

    def simulate_verification(state: AgentState) -> AgentState:
        playwright_automation.simulate_steps(state.refined_story, state.code_changes)
        return state

    # Add nodes to graph
    workflow.add_node("read_story", read_story)
    workflow.add_node("refine_story", refine_story)
    workflow.add_node("update_code", update_code)
    workflow.add_node("simulate_verification", simulate_verification)

    # Define edges
    workflow.add_edge("read_story", "refine_story")
    workflow.add_edge("refine_story", "update_code")
    workflow.add_edge("update_code", "simulate_verification")

    return workflow.compile()

# Updated main function with Vertex AI setup
def main():
    # Initialize components
    jira_tools = JiraTools(
        jira_url="https://jira.company.com",
        username=os.getenv("JIRA_USERNAME"),
        api_token=os.getenv("JIRA_API_TOKEN")
    )
    
    story_refinement_agent = StoryRefinementAgent()
    code_update_agent = CodeUpdateAgent(os.getenv("GITHUB_TOKEN"))
    playwright_automation = PlaywrightAutomation()

    # Create and run workflow
    workflow = create_workflow(
        jira_tools,
        story_refinement_agent,
        code_update_agent,
        playwright_automation
    )

    initial_state = AgentState(
        jira_story=JiraStory(
            key="PROJ-123",
            summary="",
            description="",
            acceptance_criteria=[],
            attachments=[]
        )
    )
    
    final_state = workflow.invoke(initial_state)
    
    print(f"Story refinement completed: {final_state.refined_story.key}")
    print(f"Code changes created: {final_state.code_changes.pr_url}")

if __name__ == "__main__":
    main()
