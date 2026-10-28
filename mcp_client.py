#pip install -qU langchain-mcp-adapters
# Start the server first in another terminal:  python mcp_weather_server2.py
# (it serves streamable-http on http://localhost:8000/mcp)

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import asyncio

load_dotenv(override=True)

async def main():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://localhost:8000/mcp",
            }
        }
    )

    # ---- Tools ----
    tools = await client.get_tools()
    print("Tools:", [t.name for t in tools])

    # ---- Resources ----
    async with client.session("weather") as session:
        listed = await session.list_resources()
        print("Resources:", [str(r.uri) for r in listed.resources])
        templates = await session.list_resource_templates()
        print("Resource templates:", [t.uriTemplate for t in templates.resourceTemplates])

    cities_blob = (await client.get_resources("weather", uris=["weather://cities"]))[0]
    print("\nSupported cities:\n" + cities_blob.as_string())

    forecast_blob = (await client.get_resources("weather", uris=["weather://forecast/Tokyo"]))[0]
    print("\n" + forecast_blob.as_string())

    # ---- Prompts ----
    async with client.session("weather") as session:
        listed_prompts = await session.list_prompts()
        print("\nPrompts:", [p.name for p in listed_prompts.prompts])

    report_messages = await client.get_prompt("weather", "weather_report", arguments={"location": "Mumbai"})
    compare_messages = await client.get_prompt(
        "weather", "compare_weather", arguments={"city1": "London", "city2": "Sydney"}
    )

    model = ChatOpenAI(
        model=os.getenv("CHAT_MODEL_DEPLOYMENT_NAME"),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    # Create agent and executor
    agent = create_agent(
        model=model,
        tools=tools
    )

    # Agent using a tool directly
    print("\nAsking for the weather...")
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(weather_response["messages"][-1].content)

    # Agent using a resource as context
    print("\nAsking with resource context...")
    resource_response = await agent.ainvoke(
        {"messages": [
            {"role": "user", "content": f"{forecast_blob.as_string()}\n\nShould I carry an umbrella on day 3?"}
        ]}
    )
    print(resource_response["messages"][-1].content)

    # Agent using MCP prompts (messages come from the server)
    print("\nRunning weather_report prompt...")
    prompt_response = await agent.ainvoke({"messages": report_messages})
    print(prompt_response["messages"][-1].content)

    print("\nRunning compare_weather prompt...")
    compare_response = await agent.ainvoke({"messages": compare_messages})
    print(compare_response["messages"][-1].content)

# Run the async function
asyncio.run(main())
