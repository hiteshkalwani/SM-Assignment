"""
Chat API endpoints for the City Information Assistant.

This module provides REST API endpoints for chat functionality,
using both synchronous and streaming interfaces.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from app.core.config import settings
from app.tools import WeatherTool, TimeTool, CityFactsTool, PlanMyCityVisitTool
from app.utils.exceptions import ErrorResponse

# Create router
router = APIRouter()


class ChatMessage(BaseModel):
    """A message in the chat."""

    role: str = Field(..., description="The role of the message sender (user/assistant)")
    content: str = Field(..., description="The content of the message")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What's the weather like in London?"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""

    messages: List[ChatMessage] = Field(
        ...,
        description="The conversation history",
        min_items=1,
    )
    city: str = Field(..., description="The city to get information about")
    country: Optional[str] = Field(
        None,
        description="Optional country to disambiguate the city",
    )
    temperature: Optional[float] = Field(
        None,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0-2)",
    )
    max_tokens: Optional[int] = Field(
        None,
        gt=0,
        description="Maximum number of tokens to generate",
    )
    stream: bool = Field(
        False,
        description="Whether to stream the response",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "What's the weather like in London?"}
                ],
                "city": "London",
                "country": "UK",
                "temperature": 0.7,
                "max_tokens": 500,
                "stream": False,
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""

    message: ChatMessage = Field(..., description="The assistant's response")
    usage: Dict[str, int] = Field(
        ...,
        description="Token usage information",
        example={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30},
    )
    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Tool calls made during the response generation",
    )


class ChatStreamResponse(BaseModel):
    """Streaming response model for chat endpoint."""

    event: str = Field(..., description="Event type")
    data: Dict[str, Any] = Field(..., description="Event data")

    @classmethod
    def start(cls) -> "ChatStreamResponse":
        """Create a stream start event."""
        return cls(event="start", data={"timestamp": ""})

    @classmethod
    def token(cls, token: str) -> "ChatStreamResponse":
        """Create a token event."""
        return cls(event="token", data={"token": token})

    @classmethod
    def tool_call(cls, tool_call: Dict[str, Any]) -> "ChatStreamResponse":
        """Create a tool call event."""
        return cls(event="tool_call", data={"tool_call": tool_call})

    @classmethod
    def complete(
        cls,
        message: ChatMessage,
        usage: Dict[str, int],
    ) -> "ChatStreamResponse":
        """Create a completion event."""
        return cls(
            event="complete",
            data={
                "message": message.dict(),
                "usage": usage,
            },
        )

    @classmethod
    def error(cls, error: str) -> "ChatStreamResponse":
        """Create an error event."""
        return cls(event="error", data={"error": error})


async def process_chat_stream(
    messages: List[Dict[str, str]],
    city: str,
    country: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> AsyncGenerator[ChatStreamResponse, None]:
    """Process a chat request and yield streaming events."""
    # Initialize the Agent Executor
    llm = ChatOpenAI(
        model=settings.OPENAI_MODEL,
        max_tokens=max_tokens,
        temperature=temperature
    )
    tools = [WeatherTool(), TimeTool(), CityFactsTool(), PlanMyCityVisitTool()]

    # Create a simple prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful City Information Assistant for {city}{', ' + country if country else ''}. Use the available tools to provide accurate information about weather, time, city facts, and comprehensive visit planning."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Create the agent
    agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

    # Create the agent executor
    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )

    # Prepare the input for the agent
    agent_input = {
        "input": messages[-1]["content"] if messages else "",
        "chat_history": [],  # Simple empty list for now
    }

    # Start streaming
    try:
        # Yield start event
        yield ChatStreamResponse.start().model_dump_json() + "\n"

        # Execute the agent (not streaming since we don't have astream implemented)
        result = await agent_executor.ainvoke(agent_input)

        # Handle intermediate steps (tool calls)
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                tool_call = {
                    "tool": step[0].tool if hasattr(step[0], 'tool') else "unknown",
                    "input": step[0].tool_input if hasattr(step[0], 'tool_input') else {},
                    "output": step[1] if len(step) > 1 else ""
                }
                yield ChatStreamResponse.tool_call(tool_call).model_dump_json() + "\n"

        # Stream the final output token by token to simulate streaming
        output = result.get("output", "No response generated")
        for token in output.split():
            yield ChatStreamResponse.token(token + " ").model_dump_json() + "\n"

        # Yield completion event
        yield ChatStreamResponse.complete(
            message=ChatMessage(role="assistant", content=output),
            usage={"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0},
        ).model_dump_json() + "\n"

    except Exception as e:
        yield ChatStreamResponse.error(str(e)).model_dump_json() + "\n"


@router.post(
    "",
    response_model=ChatResponse,
    responses={
        200: {"model": ChatResponse},
        400: {"model": ErrorResponse, "description": "Invalid request"},
        422: {"model": ErrorResponse, "description": "Validation error"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def chat(
    request: ChatRequest,
) -> Dict[str, Any]:
    """
    Chat with the City Information Assistant.

    This endpoint allows you to have a conversation with the AI assistant
    about a specific city. The assistant can provide information about
    weather, local time, and interesting facts about the city.

    Args:
        request: The chat request containing messages and city information.

    Returns:
        The assistant's response with token usage information.
    """
    # Handle streaming requests
    if request.stream:
        return StreamingResponse(
            process_chat_stream(
                messages=[msg.dict() for msg in request.messages],
                city=request.city,
                country=request.country,
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1024,
            ),
            media_type="text/event-stream",
        )

    # Handle non-streaming requests
    try:
        # Initialize the Agent Executor
        llm = ChatOpenAI(
            model=settings.OPENAI_MODEL,
            max_tokens=request.max_tokens or 1024,
            temperature=request.temperature or 0.7
        )
        tools = [WeatherTool(), TimeTool(), CityFactsTool(), PlanMyCityVisitTool()]

        # Create a simple prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a helpful City Information Assistant for {request.city}{', ' + request.country if request.country else ''}. Use the available tools to provide accurate information about weather, time, city facts, and comprehensive visit planning."),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        # Create the agent
        agent = create_openai_tools_agent(llm=llm, tools=tools, prompt=prompt)

        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            return_intermediate_steps=True,
            handle_parsing_errors=True,
        )

        # Prepare the input for the agent
        agent_input = {
            "input": request.messages[-1].content if request.messages else "",
            "chat_history": [msg.dict() for msg in request.messages[:-1]] if len(request.messages) > 1 else [],
        }

        # Call the agent
        result = await agent_executor.ainvoke(agent_input)

        # Extract tool calls if any
        tool_calls = []
        if "intermediate_steps" in result:
            for step in result["intermediate_steps"]:
                tool_calls.append({
                    "tool": step[0].tool if hasattr(step[0], 'tool') else "unknown",
                    "input": step[0].tool_input if hasattr(step[0], 'tool_input') else {},
                    "output": step[1] if len(step) > 1 else ""
                })

        # Prepare the response
        return {
            "message": {
                "role": "assistant",
                "content": result.get("output", "I'm sorry, I couldn't process your request."),
            },
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0,
            },
            "tool_calls": tool_calls if tool_calls else None,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e)},
        )


@router.get("/stream")
async def chat_stream(
    request: Request,
    message: str,
    city: str,
    country: Optional[str] = None,
) -> StreamingResponse:
    """
    Stream chat responses from the assistant.

    This endpoint provides a server-sent events (SSE) stream of the assistant's
    response, allowing for a more interactive chat experience.

    Args:
        request: The incoming request.
        message: The user's message.
        city: The city to get information about.
        country: Optional country to disambiguate the city.

    Returns:
        A streaming response with server-sent events.
    """
    # Prepare the messages list
    messages = [{"role": "user", "content": message}]

    # Return the streaming response
    return StreamingResponse(
        process_chat_stream(
            messages=messages,
            city=city,
            country=country,
        ),
        media_type="text/event-stream",
    )
