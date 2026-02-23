import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition

load_dotenv()

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Step 1: Create an agent ---
agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are TravelBuddy, a friendly travel assistant. "
            "You help users plan trips, suggest destinations, and answer travel questions. "
            "Keep your answers short, concise, and easy to grasp."
        ),
    ),
)
print(f"Agent created — name: {agent.name}, version: {agent.version}")

# --- Step 2: Start a conversation ---
conversation = openai_client.conversations.create()
print(f"Conversation started — id: {conversation.id}")

# --- Step 3: First turn ---
user_input = "I have a week off in March. Suggest 3 warm destinations."
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    conversation=conversation.id,
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)
print(f"Agent: {response.output_text}")

# --- Step 4: Follow-up (multi-turn) ---
user_input = "Tell me more about the second option. What should I pack?"
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    conversation=conversation.id,
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)
print(f"Agent: {response.output_text}")

# --- Cleanup ---
openai_client.conversations.delete(conversation_id=conversation.id)
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("Cleaned up.")
