import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, MCPTool
from openai.types.responses.response_input_param import McpApprovalResponse

load_dotenv()

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Define an MCP tool (example: GitMCP for Azure REST API specs) ---
mcp_tool = MCPTool(
    server_label="azure-docs",
    server_url="https://gitmcp.io/Azure/azure-rest-api-specs",
    require_approval="never",  # Options: "always", "never"
)

# --- Create agent with MCP tool ---
agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are a helpful assistant that can use MCP tools to answer questions. "
            "Use the available MCP tools to look up documentation and assist the user. "
            "Keep your answers short, concise, and easy to grasp."
        ),
        tools=[mcp_tool],
    ),
)
print(f"Agent created — {agent.name} v{agent.version}")

# --- Send a request that triggers the MCP tool ---
user_input = "Summarize the Azure REST API specifications README"
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)

print(f"Agent: {response.output_text}")

# --- Handle MCP approval requests ---
approval_inputs = []
for item in response.output:
    if item.type == "mcp_approval_request":
        print(f"  [MCP] Approval requested for server: {item.server_label}")
        # In production, implement actual approval logic here
        approval_inputs.append(
            McpApprovalResponse(
                type="mcp_approval_response",
                approve=True,
                approval_request_id=item.id,
            )
        )

if approval_inputs:
    # --- Send approval and get final response ---
    response = openai_client.responses.create(
        input=approval_inputs,
        previous_response_id=response.id,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    )

print(f"Agent: {response.output_text}")

# --- Cleanup ---
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("Cleaned up.")
