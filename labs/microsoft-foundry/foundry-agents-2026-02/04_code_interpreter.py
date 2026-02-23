import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, CodeInterpreterTool

load_dotenv()

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Create agent with Code Interpreter ---
tool = CodeInterpreterTool()

agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are TravelBuddy, a travel assistant with data analysis skills. "
            "Use the code interpreter to perform calculations, generate charts, "
            "and analyze data when needed."
            "Keep your answers short, concise, and easy to grasp."
        ),
        tools=[tool],
    ),
)
print(f"Agent created — {agent.name} v{agent.version}")

# --- Ask the agent to do a calculation ---
conversation = openai_client.conversations.create()

user_input = (
    "I'm comparing flights to 3 destinations. "
    "Cancun: $450 round trip, Bali: $1200 round trip, Maldives: $1800 round trip. "
    "Hotel costs per night: Cancun $120, Bali $80, Maldives $250. "
    "I'm staying 7 nights. Calculate the total cost for each destination "
    "and create a comparison table."
)
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    conversation=conversation.id,
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    tool_choice="required",
)

# --- Extract and display code that was run ---
for output in response.output:
    if output.type == "code_interpreter_call":
        print("--- Code Interpreter executed: ---")
        print(output.code)
        print("--- End code ---\n")

print(f"Agent: {response.output_text}")

# --- Follow-up: ask for a chart ---
user_input = "Now generate a bar chart comparing the total costs."
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    conversation=conversation.id,
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
    tool_choice="required",
)

for output in response.output:
    if output.type == "code_interpreter_call":
        print("--- Code Interpreter executed: ---")
        print(output.code)
        print("--- End code ---\n")

print(f"Agent: {response.output_text}")

# --- Cleanup ---
openai_client.conversations.delete(conversation_id=conversation.id)
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("Cleaned up.")
