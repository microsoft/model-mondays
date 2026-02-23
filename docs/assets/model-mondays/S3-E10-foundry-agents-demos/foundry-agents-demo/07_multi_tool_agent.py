import os
import json
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    FunctionTool,
    FileSearchTool,
    CodeInterpreterTool,
    WebSearchTool,
    WebSearchApproximateLocation,
)
from openai.types.responses.response_input_param import FunctionCallOutput

load_dotenv()


# ---- Custom functions ----
def book_flight(origin: str, destination: str, date: str) -> dict:
    """Simulate booking a flight."""
    return {
        "confirmation": f"FL-{hash(origin + destination + date) % 10000:04d}",
        "origin": origin,
        "destination": destination,
        "date": date,
        "status": "confirmed",
    }


def get_weather(city: str, date: str) -> dict:
    """Simulate a weather lookup."""
    import random
    return {
        "city": city,
        "date": date,
        "temp_f": random.randint(70, 95),
        "condition": random.choice(["Sunny", "Partly Cloudy", "Clear"]),
    }


FUNCTIONS = {"book_flight": book_flight, "get_weather": get_weather}

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

# --- Define all tools ---
weather_tool = FunctionTool(
    name="get_weather",
    description="Get the weather forecast for a city on a specific date.",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "City name"},
            "date": {"type": "string", "description": "Date (YYYY-MM-DD)"},
        },
        "required": ["city", "date"],
        "additionalProperties": False,
    },
    strict=True,
)

booking_tool = FunctionTool(
    name="book_flight",
    description="Book a flight from origin to destination on a given date.",
    parameters={
        "type": "object",
        "properties": {
            "origin": {"type": "string", "description": "Departure city"},
            "destination": {"type": "string", "description": "Arrival city"},
            "date": {"type": "string", "description": "Travel date (YYYY-MM-DD)"},
        },
        "required": ["origin", "destination", "date"],
        "additionalProperties": False,
    },
    strict=True,
)

code_tool = CodeInterpreterTool()

web_tool = WebSearchTool(
    user_location=WebSearchApproximateLocation(type="approximate", country="US", city="New York", region="New York")
)

# Optionally add FileSearchTool if you have a vector store:
# file_tool = FileSearchTool(vector_store_ids=["vs_xxx"])

# --- Create the multi-tool agent ---
agent = project_client.agents.create_version(
    agent_name="TravelBuddy",
    definition=PromptAgentDefinition(
        model=os.environ["AZURE_AI_MODEL_DEPLOYMENT_NAME"],
        instructions=(
            "You are TravelBuddy, an all-in-one travel assistant.\n"
            "Answer the users question. DO not provide extra information or recommendations."
            "Your users are busy. Keep your answers short and to the point."
            "- Use get_weather to check weather at destinations.\n"
            "- Use book_flight to book flights for the user.\n"
            "- Use the code interpreter for calculations, comparisons, and charts.\n"
            "- Use web search for real-time travel info, advisories, and deals.\n"
            "Choose the right tool(s) for each question."
            
        ),
        tools=[weather_tool, booking_tool, code_tool, web_tool]
    ),
)
print(f"Agent created — {agent.name} v{agent.version}")


# --- Helper to process function calls ---
def handle_function_calls(resp, conversation_id):
    """Process any function calls in a response and return the final response."""
    while True:
        tool_outputs = []
        for item in resp.output:
            if item.type == "function_call" and item.name in FUNCTIONS:
                args = json.loads(item.arguments)
                result = FUNCTIONS[item.name](**args)
                tool_outputs.append(
                    FunctionCallOutput(
                        type="function_call_output",
                        call_id=item.call_id,
                        output=json.dumps(result),
                    )
                )
                print(f"  [Tool] {item.name}({args}) → {result}")

        if not tool_outputs:
            return resp

        resp = openai_client.responses.create(
            conversation=conversation_id,
            input=tool_outputs,
            extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        )


# --- Demo conversation ---
conversation = openai_client.conversations.create()

queries = [
    "What's the weather like in Bali on March 20, 2026?",
    "Search the web for the best time to visit Bali.",
    "Calculate the total cost if flights are $1200, hotel is $80/night for 7 nights, and food is $50/day.",
    "Book me a flight from New York to Bali on March 20, 2026.",
]

for query in queries:
    print(f"\n********\nUser: {query}")
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=query,
        extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
        tool_choice="required",
    )
    response = handle_function_calls(response, conversation.id)
    print(f"Agent: {response.output_text}")

# --- Cleanup ---
openai_client.conversations.delete(conversation_id=conversation.id)
project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
print("\nCleaned up.")