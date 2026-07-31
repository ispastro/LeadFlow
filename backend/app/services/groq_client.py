import logging
from typing import Dict, List, Optional

from groq import Groq
from langchain_groq import ChatGroq

from config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# LangChain-compatible LLM factory
# ---------------------------------------------------------------------------
_DEFAULT_MODEL = "llama-3.3-70b-versatile"


def get_llm(
    model: str = _DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> ChatGroq:
    """
    Return a ChatGroq instance.
    LangSmith tracing is enabled automatically when LANGSMITH_TRACING=true
    and LANGSMITH_API_KEY are present in the environment — no extra code needed.
    """
    return ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
        groq_api_key=settings.groq_api_key,
    )


def get_json_llm(
    model: str = _DEFAULT_MODEL,
    temperature: float = 0.1,
) -> ChatGroq:
    """
    LLM configured for deterministic structured-JSON output.
    Lower temperature + json_mode reduces hallucinated fields.
    """
    return ChatGroq(
        model=model,
        temperature=temperature,
        max_tokens=2048,
        groq_api_key=settings.groq_api_key,
        model_kwargs={"response_format": {"type": "json_object"}},
    )


# ---------------------------------------------------------------------------
# Legacy raw Groq SDK (backwards-compatible with old chat.py)
# ---------------------------------------------------------------------------
class GroqService:
    _instance: Optional["GroqService"] = None
    _client: Optional[Groq] = None

    def __new__(cls) -> "GroqService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = Groq(api_key=settings.groq_api_key)
        return cls._instance

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = _DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = _DEFAULT_MODEL,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ):
        stream = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


groq_service = GroqService()
