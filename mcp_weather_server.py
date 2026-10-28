from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Weather")

@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return f"It's always sunny in {location}"

# Resources
@mcp.resource("weather://cities")
def list_supported_cities() -> str:
    """List of cities with weather data available."""
    return "\n".join(["London", "New York", "Tokyo", "Mumbai", "Sydney"])

@mcp.resource("weather://forecast/{city}")
def get_forecast(city: str) -> str:
    """Get a 3-day forecast for a city."""
    return (
        f"3-day forecast for {city}:\n"
        "Day 1: Sunny, 28°C\n"
        "Day 2: Partly cloudy, 26°C\n"
        "Day 3: Light showers, 23°C"
    )

# Prompts
@mcp.prompt()
def weather_report(location: str) -> str:
    """Ask for a detailed weather report for a location."""
    return (
        f"Use the get_weather tool to fetch the weather for {location}, "
        "then write a short, friendly weather report including what to wear."
    )

@mcp.prompt()
def compare_weather(city1: str, city2: str) -> str:
    """Compare the weather between two cities."""
    return (
        f"Get the weather for {city1} and {city2} using the get_weather tool, "
        "then compare them and say which city is better to visit today."
    )

if __name__ == "__main__":
    # mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")