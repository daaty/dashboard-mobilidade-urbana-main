from fastapi import APIRouter
from app.models.auth import LoginRequest, LoginResponse, TwoFARequest, TwoFAResponse, UserResponse

router = APIRouter()

@router.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
def login(request: LoginRequest):
    # Mock: autenticação sempre retorna token
    return LoginResponse(access_token="mocked.jwt.token")

@router.post("/auth/2fa", response_model=TwoFAResponse, tags=["Auth"])
def two_fa(request: TwoFARequest):
    # Mock: 2FA sempre sucesso
    return TwoFAResponse(success=True, message="2FA verificado")

@router.get("/auth/user", response_model=UserResponse, tags=["Auth"])
def get_user():
    # Mock: retorna usuário fixo
    return UserResponse(id=1, username="admin", email="admin@empresa.com", roles=["admin", "user"])
