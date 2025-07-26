from fastapi import APIRouter
from backend.app.models.llm import LLMChatRequest, LLMChatResponse

router = APIRouter()

@router.post("/ia/llm", response_model=LLMChatResponse, tags=["Inteligência Artificial"])
def chat_llm(request: LLMChatRequest):
    # Mock: retorna resposta simulada
    return LLMChatResponse(response=f"Resposta simulada para: {request.prompt}", usage_tokens=42)
