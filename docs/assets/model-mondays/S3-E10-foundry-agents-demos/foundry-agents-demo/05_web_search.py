import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WebSearchTool,
    WebSearchApproximateLocation,
)

load_dotenv()

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Create the Web Search tool with location context ---
tool = WebSearchTool(
    user_location=WebSearchApproximateLocation(
        type="approximate", country="US", city="New York", region="New York"
    )
)

# --- Create agent with Web Search ---
agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are TravelBuddy, a travel assistant with access to the web. "
            "Search the web for latest travel advisories, flight deals, and destination info. "
            "Always cite your sources with URLs. "
            "Keep your answers short, concise, and easy to grasp."
        ),
        tools=[tool],
    ),
)
print(f"Agent created — {agent.name} v{agent.version}")

# --- Stream a web-grounded response ---
conversation = openai_client.conversations.create()

user_input = "What are the current travel advisories for Southeast Asia?"
print(f"\n********\nUser: {user_input}")
stream = openai_client.responses.create(
    stream=True,
    conversation=conversation.id,
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)

print("Agent: ", end="")
citations = []
for event in stream:
    if event.type == "response.output_text.delta":
        print(event.delta, end="", flush=True)
    elif event.type == "response.output_item.done":
        if event.item.type == "message" and event.item.content:
            for content_part in event.item.content:
                if hasattr(content_part, "annotations"):
                    for ann in content_part.annotations:
                        if ann.type == "url_citation":
                            citations.append(ann.url)

print("\n")
if citations:
    print("Sources:")
    for url in citations:
        print(f"  - {url}")

# --- Cleanup ---
openai_client.conversations.delete(conversation_id=conversation.id)
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("Cleaned up.")
