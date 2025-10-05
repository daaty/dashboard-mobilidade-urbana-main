
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
    try:
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
        
        # Truncar senha para 72 caracteres (limite do bcrypt) - CORRIGIDO
        password_str = request.password[:72]  # Trunca a string, não os bytes
        
        # Cria novo usuário
        new_user = User(
            username=request.username,
            email=request.email,
            password_hash=bcrypt.hash(password_str),
            first_name=request.first_name,
            last_name=request.last_name,
            roles="user"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return SignupResponse(success=True, message="Usuário cadastrado com sucesso!")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        print(f"❌ ERRO NO SIGNUP: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao cadastrar usuário: {str(e)}")

@router.post("/auth/login", response_model=LoginResponse, tags=["Auth"])
def login(request: LoginRequest, db: Session = Depends(get_db)):
    try:
        # Busca usuário no banco
        user = db.query(User).filter(User.username == request.username).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
        
        # Truncar senha para 72 bytes (limite do bcrypt) - CORRIGIDO
        # Precisa converter para string novamente após truncar
        password_str = request.password[:72]  # Trunca a string, não os bytes
        
        # Verificar senha
        if not bcrypt.verify(password_str, user.password_hash):
            raise HTTPException(status_code=401, detail="Usuário ou senha incorretos.")
        
        if not user.is_active:
            raise HTTPException(status_code=401, detail="Usuário inativo.")
        
        # Atualizar último login (usando func.now() do SQLAlchemy)
        from sqlalchemy import func
        user.last_login = func.now()
        db.commit()
        
        # Por enquanto retorna token mock - depois implementamos JWT real
        return LoginResponse(access_token="mocked.jwt.token")
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ ERRO NO LOGIN: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro ao fazer login: {str(e)}")

@router.post("/auth/2fa", response_model=TwoFAResponse, tags=["Auth"])
def two_fa(request: TwoFARequest):
    # Mock: 2FA sempre sucesso
    return TwoFAResponse(success=True, message="2FA verificado")

@router.get("/auth/user", response_model=UserResponse, tags=["Auth"])
def get_user():
    # Mock: retorna usuário fixo
    return UserResponse(id=1, username="admin", email="admin@empresa.com", roles=["admin", "user"])
