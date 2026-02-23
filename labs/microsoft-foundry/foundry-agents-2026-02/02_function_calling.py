import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition, FunctionTool
from openai.types.responses.response_input_param import FunctionCallOutput

load_dotenv()

# ---- Your custom function (could call a real API) ----
def get_weather(city: str, date: str) -> dict:
    """Simulate a weather API call."""
    fake_data = {
        "Cancun":   {"temp_f": 85, "condition": "Sunny"},
        "Bali":     {"temp_f": 82, "condition": "Partly cloudy"},
        "Maldives": {"temp_f": 88, "condition": "Sunny"},
    }
    weather = fake_data.get(city, {"temp_f": 75, "condition": "Unknown"})
    weather["city"] = city
    weather["date"] = date
    return weather

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Define the function tool ---
weather_tool = FunctionTool(
    name="get_weather",
    description="Get the weather forecast for a city on a specific date.",
    parameters={
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name, e.g. 'Cancun'",
            },
            "date": {
                "type": "string",
                "description": "Date in YYYY-MM-DD format",
            },
        },
        "required": ["city", "date"],
        "additionalProperties": False,
    },
    strict=True,
)

# --- Create agent with the function tool ---
agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are TravelBuddy, a travel assistant. "
            "When users ask about weather, use the get_weather function. "
            "Keep your answers short, concise, and easy to grasp."
        ),
        tools=[weather_tool],
    ),
)
print(f"Agent created — {agent.name} v{agent.version}")

# --- Ask a question that triggers the function ---
user_input = "What will the weather be like in Cancun on March 15, 2026?"
print(f"\n********\nUser: {user_input}")
response = openai_client.responses.create(
    input=user_input,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)

# --- Handle function calls ---
tool_outputs = []
for item in response.output:
    if item.type == "function_call" and item.name == "get_weather":
        args = json.loads(item.arguments)
        result = get_weather(**args)
        tool_outputs.append(
            FunctionCallOutput(
                type="function_call_output",
                call_id=item.call_id,
                output=json.dumps(result),
            )
        )
        print(f"  [Tool] get_weather({args}) → {result}")

# --- Send function results back for final answer ---
response = openai_client.responses.create(
    input=tool_outputs,
    previous_response_id=response.id,
    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
)
print(f"Agent: {response.output_text}")

# --- Cleanup ---
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("Cleaned up.")
