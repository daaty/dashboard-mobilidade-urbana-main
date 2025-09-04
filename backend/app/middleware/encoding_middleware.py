"""
Middleware para corrigir problemas de codificação em todas as respostas da API
"""
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
import json
from app.utils.encoding_fix import fix_encoding_response

class EncodingFixMiddleware(BaseHTTPMiddleware):
    """
    Middleware que aplica correção de codificação a todas as respostas JSON da API
    """
    async def dispatch(self, request: Request, call_next):
        # Processar a requisição normalmente
        response = await call_next(request)
        
        # Verificar se é uma resposta JSON que precisa ser corrigida
        if response.headers.get("content-type") == "application/json":
            try:
                # Ler o conteúdo da resposta
                body = [chunk async for chunk in response.body_iterator]
                response.body_iterator = None
                
                # Decodificar os bytes para string
                body_str = b"".join(body).decode()
                
                # Converter para dicionário
                data = json.loads(body_str)
                
                # Aplicar a correção de codificação
                fixed_data = fix_encoding_response(data)
                
                # Criar uma nova resposta com os dados corrigidos
                new_body = json.dumps(fixed_data).encode()
                
                # Criar a nova resposta
                return Response(
                    content=new_body,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    media_type="application/json"
                )
                
            except Exception as e:
                # Em caso de erro, retornar a resposta original
                print(f"Erro ao processar codificação: {str(e)}")
                
        # Retornar a resposta original se não for JSON ou houver erro
        return response


def add_encoding_middleware(app: FastAPI):
    """
    Adiciona o middleware de correção de codificação ao aplicativo FastAPI
    
    Args:
        app: Aplicativo FastAPI
    """
    app.add_middleware(EncodingFixMiddleware)
