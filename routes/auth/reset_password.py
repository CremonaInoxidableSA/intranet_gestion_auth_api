from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, TypedDict, cast, Dict, Any
from database import get_connection
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(tags=["auth"])

def require_env(name: str) -> str:
    """Obtiene variable de entorno requerida o lanza error"""
    value = os.getenv(name)
    if value is None or value.strip() == "":
        raise RuntimeError(f"Variable de entorno requerida no configurada: {name}")
    return value

# Configurar el mismo serializer que en la API de mail
# CRÍTICO: RESET_TOKEN_SECRET debe ser idéntico en ambas APIs
RESET_TOKEN_SECRET = require_env("RESET_TOKEN_SECRET")
RESET_TOKEN_EXP_MINUTES = int(os.getenv("RESET_TOKEN_EXP_MINUTES", "15"))
serializer = URLSafeTimedSerializer(RESET_TOKEN_SECRET)

class VerificarTokenRequest(BaseModel):
    token: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

class UsuarioData(TypedDict):
    username: str
    email: str

def verificar_token_recuperacion(token: str) -> Optional[Dict[str, Any]]:
    """Verifica que el token sea válido y no haya expirado"""
    try:
        payload = serializer.loads(token, max_age=RESET_TOKEN_EXP_MINUTES * 60)
        return payload
    except SignatureExpired:
        return None
    except BadSignature:
        return None
    except Exception:
        return None

@router.post("/verificar-token")
def verificar_token(data: VerificarTokenRequest):
    """Verifica que el token de recuperación sea válido"""
    payload = verificar_token_recuperacion(data.token)
    
    if payload is None:
        return JSONResponse(
            content={
                "success": False,
                "error": "Token inválido o expirado"
            },
            status_code=401
        )
    
    return JSONResponse(
        content={
            "success": True,
            "email": payload.get("email"),
            "message": "Token válido"
        },
        status_code=200
    )

@router.get("/reset-password")
def verificar_token_get(token: str = Query(...)):
    """Verifica que el token de recuperación sea válido (GET)"""
    payload = verificar_token_recuperacion(token)
    
    if payload is None:
        return JSONResponse(
            content={
                "success": False,
                "error": "Token inválido o expirado"
            },
            status_code=401
        )
    
    return JSONResponse(
        content={
            "success": True,
            "email": payload.get("email"),
            "message": "Token válido"
        },
        status_code=200
    )

@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest):
    """Cambia la contraseña usando un token válido"""
    payload = verificar_token_recuperacion(data.token)
    
    if payload is None:
        return JSONResponse(
            content={
                "success": False,
                "error": "Token inválido o expirado"
            },
            status_code=401
        )
    
    email = payload.get("email")
    if not email:
        return JSONResponse(
            content={
                "success": False,
                "error": "Token inválido"
            },
            status_code=401
        )
    
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar usuario por email
        cursor.execute("SELECT username FROM Usuarios WHERE email = %s", (email,))
        usuario = cast(Optional[UsuarioData], cursor.fetchone())
        
        if not usuario:
            cursor.close()
            conn.close()
            return JSONResponse(
                content={
                    "success": False,
                    "error": "Usuario no encontrado"
                },
                status_code=404
            )
        
        # Hash de la nueva contraseña
        new_hashed = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        
        # Actualizar contraseña
        cursor.execute(
            "UPDATE Usuarios SET password_hash = %s WHERE username = %s",
            (new_hashed, usuario["username"])
        )
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return JSONResponse(
            content={
                "success": True,
                "message": "Contraseña actualizada correctamente"
            },
            status_code=200
        )
    
    except Exception as e:
        cursor.close()
        conn.close()
        return JSONResponse(
            content={
                "success": False,
                "error": f"Error al actualizar la contraseña: {str(e)}"
            },
            status_code=500
        )
