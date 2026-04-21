"""
Tool registry for context enrichment.

Only tools whose API keys are configured will be available to the orchestrator.
"""

from backend.context.tools.base import ContextTool


def _get_all_tool_classes() -> list[type]:
    """Lazy import to avoid circular deps and missing-module errors."""
    from backend.context.tools.web_search import WebSearchTool
    from backend.context.tools.google_places import GooglePlacesTool
    from backend.context.tools.news_search import NewsSearchTool
    from backend.context.tools.price_index import PriceIndexTool
    from backend.context.tools.weather_trends import WeatherTrendsTool
    from backend.context.tools.demographic import DemographicTool
    from backend.context.tools.review_analyzer import ReviewAnalyzerTool
    from backend.context.tools.social_sentiment import SocialSentimentTool
    from backend.context.tools.google_trends import GoogleTrendsTool
    from backend.context.tools.economic_data_tool import EconomicDataContextTool
    from backend.context.tools.market_data_tool import MarketDataContextTool

    return [
        WebSearchTool,
        GooglePlacesTool,
        NewsSearchTool,
        PriceIndexTool,
        WeatherTrendsTool,
        DemographicTool,
        ReviewAnalyzerTool,
        SocialSentimentTool,
        GoogleTrendsTool,
        EconomicDataContextTool,
        MarketDataContextTool,
    ]


def get_available_tools(settings) -> list[ContextTool]:
    """Return only tool instances whose required API keys are configured."""
    instances = []
    for cls in _get_all_tool_classes():
        tool = cls()
        if tool.available(settings):
            instances.append(tool)
    return instances


def get_tool_by_name(name: str) -> ContextTool:
    """Get a single tool instance by name."""
    for cls in _get_all_tool_classes():
        tool = cls()
        if tool.name == name:
            return tool
    raise ValueError(f"Unknown tool: {name}")


def get_tool_descriptions(settings) -> list[dict]:
    """Tool descriptions for the orchestrator prompt."""
    tools = get_available_tools(settings)
    return [
        {"name": t.name, "description": t.description}
        for t in tools
    ]
