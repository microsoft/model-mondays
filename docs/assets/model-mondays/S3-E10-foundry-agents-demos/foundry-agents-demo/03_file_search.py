import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FileSearchTool

load_dotenv()

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Step 1: Create a vector store ---
vector_store = openai_client.vector_stores.create(name="TravelBuddyDocs")
print(f"Vector store created — id: {vector_store.id}")

# --- Step 2: Upload a file ---
file = openai_client.vector_stores.files.upload_and_poll(
    vector_store_id=vector_store.id,
    file=open("product_catalog.md", "rb"),
)
print(f"File uploaded — id: {file.id}")

# --- Step 3: Create agent with FileSearchTool ---
tool = FileSearchTool(vector_store_ids=[vector_store.id])

agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are TravelBuddy, a travel assistant. "
            "Use the file search tool to answer questions about our plans and products. "
            "Always cite which plan you're referring to. "
            "Keep your answers short, concise, and easy to grasp."
        ),
        tools=[tool],
    ),
)
print(f"Agent created — {agent.name} v{agent.version}")

# --- Step 4: Ask about the documents ---
conversation = openai_client.conversations.create()

user_input = "Which plan includes travel insurance? How much does it cost?"
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    conversation=conversation.id,
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)
print(f"Agent: {response.output_text}")

# Follow-up
user_input = "Compare the Adventurer and Globetrotter plans for me."
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
