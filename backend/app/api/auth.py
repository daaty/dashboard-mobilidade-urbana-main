
import os
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models.auth import LoginRequest, LoginResponse, TwoFARequest, TwoFAResponse, UserResponse, SignupRequest, SignupResponse
from app.models.user import User
from app.database.db import get_db
from passlib.hash import bcrypt

router = APIRouter()

@router.post("/auth/signup", response_model=SignupResponse, tags=["Auth"])
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    # Verifica o token secreto
    secret_token = os.getenv("SIGNUP_SECRET_TOKEN", "meu_token_super_secreto")
    if request.signup_token != secret_token:
        raise HTTPException(status_code=403, detail="Token de cadastro inválido.")
    
    # Verifica se usuário já existe
    existing_user = db.query(User).filter(
        (User.username == request.username) | (User.email == request.email)
    ).first()
    
    if existing_user:
        return SignupResponse(success=False, message="Usuário ou email já cadastrado.")
    
    # Cria novo usuário
    new_user = User(
        username=request.username,
        email=request.email,
        password_hash=bcrypt.hash(request.password),
        first_name=request.first_name,
        last_name=request.last_name,
        roles="user"
    )
    
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return SignupResponse(success=True, message="Usuário cadastrado com sucesso!")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar usuário: {str(e)}")

@router.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Busca usuário no banco
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not bcrypt.verify(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inativo.")
    
    # Atualizar último login (usando func.now() do SQLAlchemy)
    from sqlalchemy import func
    user.last_login = func.now()
    db.commit()
    
    # Por enquanto retorna token mock - depois implementamos JWT real
    return LoginResponse(access_token="mocked.jwt.token")

@router.post("/auth/2fa", response_model=TwoFAResponse, tags=["Auth"])
def two_fa(request: TwoFARequest):
    # Mock: 2FA sempre sucesso
    return TwoFAResponse(success=True, message="2FA verificado")

@router.get("/auth/user", response_model=UserResponse, tags=["Auth"])
def get_user():
    # Mock: retorna usuário fixo
    return UserResponse(id=1, username="admin", email="admin@empresa.com", roles=["admin", "user"])
