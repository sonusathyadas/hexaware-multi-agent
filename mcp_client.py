#pip install -qU langchain-mcp-adapters

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
                "transport": "stdio",  # Local subprocess communication
                "command": "python",
                # Absolute path to your mcp_math_server.py file
                "args": ["C:\\Users\\sonusathyadas\\Desktop\\Multi-Agent\\mcp_weather_server.py"],  # Fixed path - should be relative or absolute
            }
        }
    )

    tools = await client.get_tools()  

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

    print("Asking for the weather...")
    weather_response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
    )
    print(weather_response["messages"][-1].content)

# Run the async function
asyncio.run(main())
