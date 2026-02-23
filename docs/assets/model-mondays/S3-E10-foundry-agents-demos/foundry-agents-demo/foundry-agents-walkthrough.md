# Azure AI Foundry Agents — Progressive Walkthrough

> **Audience:** Developers new to Microsoft Foundry Agents.
> Each iteration builds on the previous one, gradually adding more powerful tools and patterns.

---
## Table of Contents

- [Azure AI Foundry Agents — Progressive Walkthrough](#azure-ai-foundry-agents--progressive-walkthrough)
  - [0. Prerequisites \& Environment Setup](#0-prerequisites--environment-setup)
  - [Iteration 1 — Hello Agent (Basic Conversational Agent)](#iteration-1--hello-agent-basic-conversational-agent)
  - [Iteration 2 — Function Calling (Give Your Agent Custom Skills)](#iteration-2--function-calling-give-your-agent-custom-skills)
  - [Iteration 3 — File Search (Ground Your Agent with Documents)](#iteration-3--file-search-ground-your-agent-with-documents)
  - [Iteration 4 — Code Interpreter (Let Your Agent Write \& Run Code)](#iteration-4--code-interpreter-let-your-agent-write--run-code)
  - [Iteration 5 — Web Search (Real-Time Internet Access)](#iteration-5--web-search-real-time-internet-access)
  - [Iteration 6 — MCP Tools (Connect to External Servers via Model Context Protocol)](#iteration-6--mcp-tools-connect-to-external-servers-via-model-context-protocol)
  - [Iteration 7 — Combining Multiple Tools](#iteration-7--combining-multiple-tools)
  - [Further Exploration](#further-exploration)
    - [More tools to try](#more-tools-to-try)
    - [Advanced patterns](#advanced-patterns)
    - [Key reference links](#key-reference-links)
    - [Tips for production](#tips-for-production)

---

## 0. Prerequisites & Environment Setup

### Create Foundry Resources (one-time)

Follow the official quickstart to create a Foundry project, deploy a model, and get your project endpoint:

📖 [Quickstart: Set up Microsoft Foundry resources](https://learn.microsoft.com/en-us/azure/ai-foundry/tutorials/quickstart-create-foundry-resources?view=foundry&tabs=azurecli)

### Local dev environment

```bash
# Install packages (use the preview version of azure-ai-projects)
pip install "azure-ai-projects>=2.0.0b4" python-dotenv openai azure-identity

# Authenticate
az login
```

### Environment variables

Create a `.env` file in your project root:

```ini
AZURE_AI_PROJECT_ENDPOINT=<your endpoint from the Foundry portal>
AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-4.1-mini
```

> **Tip:** Find your project endpoint on the welcome/overview screen of the [Microsoft Foundry portal](https://ai.azure.com/).

---

## Iteration 1 — Hello Agent (Basic Conversational Agent)

**Goal:** Create the simplest possible agent, send it a message, and hold a multi-turn conversation.

**What you'll learn:**
- Creating an `AIProjectClient`
- Defining a `PromptAgentDefinition` with instructions
- Creating a conversation and chatting across multiple turns

### Code — `01_basic_agent.py`

```python
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
```

**Key takeaways:**
- The agent retains conversation history — the follow-up question "the second option" works because context is maintained.
- `agent_reference` links the response call to your named agent.
- Always clean up agents and conversations when done to avoid accumulating unused resources.

---

## Iteration 2 — Function Calling (Give Your Agent Custom Skills)

**Goal:** Teach the agent to call *your own functions* — a weather lookup in this case — so it can take real actions.

**What you'll learn:**
- Defining a `FunctionTool` with a JSON schema
- Handling `function_call` items in the response
- Sending `FunctionCallOutput` back to complete the loop

### Code — `02_function_calling.py`

```python
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

# --- Setup clients ---
credential = DefaultAzureCredential()
project_client = AIProjectClient(
    endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"],
    credential=credential,
)
openai_client = project_client.get_openai_client()

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
```

**Key takeaways:**
- The model decides *when* to call the function based on the user's question — you don't hardcode it.
- `strict=True` ensures the model adheres exactly to your JSON schema.
- You can define multiple `FunctionTool`s and the agent will pick the right one(s).

---

## Iteration 3 — File Search (Ground Your Agent with Documents)

**Goal:** Upload documents and let the agent search through them to answer questions — great for internal knowledge bases, product docs, or FAQs.

**What you'll learn:**
- Creating a vector store and uploading files
- Using `FileSearchTool` to give the agent retrieval-augmented generation (RAG) capabilities

### Preparation

Create a file `product_catalog.md` with some sample content:

```markdown
# TravelBuddy Premium Plans

## Explorer Plan - $29/month
- 5 trip plans per month
- Basic weather forecasts
- Email support

## Adventurer Plan - $59/month
- Unlimited trip plans
- Detailed weather + packing lists
- Priority chat support
- Airport lounge access (2x/month)

## Globetrotter Plan - $99/month
- Everything in Adventurer
- Concierge booking service
- Travel insurance included
- Airport lounge unlimited access
```

### Code — `03_file_search.py`

```python
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
```

**Key takeaways:**
- The vector store indexes your files so the agent can retrieve relevant chunks at query time.
- You can upload multiple files (PDFs, Markdown, text) to the same vector store.
- This is essentially **RAG** (Retrieval-Augmented Generation) built right into the agent.

---

## Iteration 4 — Code Interpreter (Let Your Agent Write & Run Code)

**Goal:** Let the agent generate *and execute* Python code in a sandboxed environment — perfect for data analysis, calculations, and chart generation.

**What you'll learn:**
- Attaching a `CodeInterpreterTool`
- Extracting generated code from the response
- Having the agent perform dynamic computations

### Code — `04_code_interpreter.py`

```python
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
            "and analyze data when needed. "
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
```

**Key takeaways:**
- The agent writes and runs Python code in a sandboxed environment — you don't need to execute anything locally.
- `tool_choice="required"` forces the agent to use the code interpreter (useful when you know computation is needed).
- Great for: math, data transformations, chart generation, CSV/Excel analysis.

---

## Iteration 5 — Web Search (Real-Time Internet Access)

**Goal:** Give the agent access to live web data so it can answer questions about current events, prices, or real-time information.

**What you'll learn:**
- Using `WebSearchTool` (powered by Grounding with Bing)
- Streaming responses for real-time output
- Extracting URL citations from responses

> **Note:** Web Search uses Grounding with Bing, which has additional costs and terms.
> See [Bing Grounding legal terms](https://www.microsoft.com/bing/apis/grounding-legal-enterprise).

### Code — `05_web_search.py`

```python
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
```

**Key takeaways:**
- `WebSearchTool` gives the agent live internet access — responses are grounded in real search results.
- `stream=True` enables token-by-token streaming for responsive UX.
- `WebSearchApproximateLocation` can bias results toward a region — useful for localized results.
- Always show citations so users can verify information.

---

## Iteration 6 — MCP Tools (Connect to External Servers via Model Context Protocol)

**Goal:** Connect the agent to an external MCP (Model Context Protocol) server — a standardized way to expose tools from third-party services.

**What you'll learn:**
- Using `MCPTool` to connect to remote MCP servers
- Handling MCP approval flows
- The MCP pattern for extensibility

### Code — `06_mcp_tool.py`

```python
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
    require_approval="always",  # Options: "always", "never"
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
```

**Key takeaways:**
- MCP is an open protocol for exposing tools — any MCP-compatible server can be connected.
- `require_approval="always"` means the user (or your code) must approve each tool invocation — a safety net.
- You can find MCP servers in the **Foundry Tool Catalog** (Build > Tools in the Foundry portal).
- You can also build your own MCP servers and connect them.

---

## Iteration 7 — Combining Multiple Tools

**Goal:** Build the ultimate TravelBuddy agent by combining function calling, file search, code interpreter, and web search into a single agent.

**What you'll learn:**
- Attaching multiple tools to one agent
- The agent intelligently decides which tool to use for each query

### Code — `07_multi_tool_agent.py`

```python
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
```

**Key takeaways:**
- A single agent can have multiple tools — the model chooses which to invoke.
- The conversation context flows across all turns, so the agent can combine information from earlier tool calls.
- In production, you'd add error handling, retries, and logging around tool execution.

---

## Further Exploration

### More tools to try

| Tool | Description | Link |
|------|-------------|------|
| **Azure AI Search** | Ground agents with your own search index | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/azure-ai-search?view=foundry) |
| **Bing Grounding** | Internet search with Bing (alternative to Web Search) | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/bing-grounding?view=foundry) |
| **SharePoint** | Chat with private SharePoint documents | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/sharepoint?view=foundry) |
| **Image Generation** | Generate images as part of agent conversations | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/image-generation?view=foundry) |
| **OpenAPI tool** | Connect agents to external REST APIs via OpenAPI specs | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/openapi-spec?view=foundry) |
| **Computer Use** | Let agents interact with computer UIs | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/computer-use?view=foundry) |
| **Microsoft Fabric** | Integrate with Fabric for data analysis | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/fabric?view=foundry) |
| **Agent-to-Agent (A2A)** | Connect agents to other agents via A2A protocol | [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/agent-to-agent?view=foundry) |

### Advanced patterns

- **Streaming:** Use `stream=True` on `responses.create()` for real-time token-by-token output (shown in Iteration 5).
- **Structured Output:** Define a JSON schema for agent responses. See [sample_agent_structured_output.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_agent_structured_output.py).
- **Multi-Agent Workflows:** Orchestrate multiple agents working together. See [sample_workflow_multi_agent.py](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/ai/azure-ai-projects/samples/agents/sample_workflow_multi_agent.py).
- **Async operations:** Every sample has an `_async.py` variant for production-grade async/await usage.
- **Telemetry:** Enable OpenTelemetry tracing. See the [telemetry samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents/telemetry).
- **Private Tool Catalog:** Publish custom MCP servers for your organization. [Docs](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/private-tool-catalog?view=foundry).

### Key reference links

| Resource | URL |
|----------|-----|
| **Foundry Quickstart (resources)** | https://learn.microsoft.com/en-us/azure/ai-foundry/tutorials/quickstart-create-foundry-resources?view=foundry |
| **Foundry Quickstart (code)** | https://learn.microsoft.com/en-us/azure/ai-foundry/quickstarts/get-started-code?view=foundry |
| **Tool Catalog** | https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-catalog?view=foundry |
| **Tool Best Practices** | https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/tool-best-practice?view=foundry |
| **All Python SDK Samples** | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents |
| **Foundry Samples Repo** | https://github.com/azure-ai-foundry/foundry-samples |
| **MCP Server Guide** | https://learn.microsoft.com/en-us/azure/ai-foundry/mcp/build-your-own-mcp-server?view=foundry |
| **Foundry Portal** | https://ai.azure.com/ |

### Tips for production

1. **Error handling:** Wrap tool executions in try/except and return meaningful error messages to the agent.
2. **Approval flows:** For MCP and sensitive function calls, implement proper human-in-the-loop approval.
3. **Rate limiting:** Be mindful of API rate limits, especially when combining multiple tools.
4. **Cost management:** Web Search (Bing Grounding) and Code Interpreter have additional costs — monitor usage.
5. **Security:** Never pass credentials in prompts. Use managed identity (`DefaultAzureCredential`) and keep secrets in environment variables or Key Vault.

---

> **Package version note:** The code in this walkthrough uses `azure-ai-projects>=2.0.0b4` (preview). This is the *new* Foundry agents API and is **not** compatible with the 1.x GA version (Foundry classic). Make sure you install the correct version.
