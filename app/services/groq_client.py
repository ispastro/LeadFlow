from groq import Groq
from config import settings
from typing import List, Dict


class GroqService:
    _instance = None
    _client: Groq = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._client = Groq(api_key=settings.groq_api_key)
        return cls._instance
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ) -> str:
        """Generate chat completion using Groq"""
        response = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
    
    def chat_completion_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama-3.1-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 1024
    ):
        """Stream chat completion using Groq"""
        stream = self._client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True
        )
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


# Singleton instance
groq_service = GroqService()
