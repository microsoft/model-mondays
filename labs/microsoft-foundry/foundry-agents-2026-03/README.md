# Spotlight On: Microsoft Foundry Agents

[Watch Live · Catch The Episode Replay](https://aka.ms/MM/feb23g)

![Banner](./../../../docs/assets/model-mondays/S3-E10.png)

## Summary

This lab is a progressive, hands-on walkthrough of **Microsoft Foundry Agents** using the `azure-ai-projects` Python SDK. Starting from a minimal conversational agent and building up to a fully multi-tool system, each script layers in a new capability so you can learn at your own pace. 

> [Watch Live · Catch The Episode Replay](https://aka.ms/MM/feb23g) to see a walkthrough demo of the lab from Bala.

| Script | Topic | What it covers |
|---|---|---|
| `01_basic_agent.py` | Hello Agent | Create an `AIProjectClient`, define an agent with `PromptAgentDefinition`, and hold a multi-turn conversation |
| `02_function_calling.py` | Function Calling | Give your agent custom skills by registering Python functions as `FunctionTool` so it can call real (or simulated) APIs |
| `03_file_search.py` | File Search | Upload documents to a vector store and ground the agent's responses with `FileSearchTool` |
| `04_code_interpreter.py` | Code Interpreter | Let the agent write and execute Python code at runtime using `CodeInterpreterTool` for calculations and data analysis |
| `05_web_search.py` | Web Search | Provide real-time internet access with `WebSearchTool`, including approximate user location context |
| `06_mcp_tool.py` | MCP Tool | Connect the agent to external servers via the **Model Context Protocol** using `MCPTool` |
| `07_multi_tool_agent.py` | Multi-Tool Agent | Combine Function Calling, File Search, Code Interpreter, and Web Search in a single production-style agent |

The companion file `foundry-agents-walkthrough.md` provides in-depth explanations and annotated code for every iteration, plus tips for taking agents to production. `product_catalog.md` is the sample document used in the File Search iteration.

**Prerequisites:** 

1. An active Microsoft Foundry project with a deployed model.
1. A Python environment with `azure-ai-projects>=2.0.0b4`, `python-dotenv`, `openai`, and `azure-identity` installed. 
1. A `.env` with `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` defined
