from pydantic import BaseModel
from typing import List, Optional

class LLMChatRequest(BaseModel):
    prompt: str
    history: Optional[List[str]] = None

class LLMChatResponse(BaseModel):
    response: str
    usage_tokens: Optional[int] = None
