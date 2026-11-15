from functools import lru_cache
from typing import Any

from langchain_core.messages import HumanMessage
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from config import settings
from prompt_library.prompt import SYSTEM_PROMPT
from tools.currency_conversion_tool import CurrencyConverterTool
from tools.expense_calculator_tool import CalculatorTool
from tools.place_search_tool import PlaceSearchTool
from tools.weather_tool import WeatherTool
from utils.model_loader import ModelLoader, ModelName


class GraphBuilder:
    def __init__(self, model_provider: ModelName | None = None):
        provider = model_provider or settings.model_provider
        self.model = ModelLoader(model_name=provider)()
        self.system_prompt = SYSTEM_PROMPT
        self.tools = self._build_tools()
        self.llm_with_tools = self.model.bind_tools(self.tools)
        self.graph = None

    @staticmethod
    def _build_tools() -> list[Any]:
        tool_groups = (
            WeatherTool().tools,
            PlaceSearchTool().tools,
            CurrencyConverterTool().tools,
            CalculatorTool().tools,
        )
        return [tool for group in tool_groups for tool in group]

    def agent_function(self, state: MessagesState) -> dict[str, list[Any]]:
        messages = [self.system_prompt, *state["messages"]]
        response = self.llm_with_tools.invoke(messages)
        return {"messages": [response]}

    def build_graph(self):
        graph_builder = StateGraph(MessagesState)
        graph_builder.add_node("agent", self.agent_function)
        graph_builder.add_node("tools", ToolNode(tools=self.tools))
        graph_builder.add_edge(START, "agent")
        graph_builder.add_conditional_edges("agent", tools_condition)
        graph_builder.add_edge("tools", "agent")
        graph_builder.add_edge("agent", END)
        self.graph = graph_builder.compile()
        return self.graph

    def invoke(self, question: str) -> dict[str, Any]:
        if not question.strip():
            raise ValueError("The travel question cannot be empty.")
        return self().invoke({"messages": [HumanMessage(content=question)]})

    def __call__(self):
        return self.graph or self.build_graph()


@lru_cache(maxsize=3)
def get_graph(model_provider: ModelName | None = None):
    return GraphBuilder(model_provider=model_provider)()
