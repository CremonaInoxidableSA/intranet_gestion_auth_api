import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import TypedDict, Optional

SECRET_KEY: Optional[str] = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
REQUIRE_AUTH = os.getenv("REQUIRE_AUTH", "true").lower() == "true"

def get_secret_key() -> str:
  secret = os.getenv("JWT_SECRET")
  if not secret:
    raise RuntimeError("JWT_SECRET no definido. Define JWT_SECRET en el entorno.")
  return secret

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)

class TokenUser(TypedDict):
  username: str
  rol: Optional[str]

def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[TokenUser]:
  """
  Valida el token JWT. Si REQUIRE_AUTH=false en .env, permite acceso sin token.
  Si REQUIRE_AUTH=true, requiere token válido.
  """
  
  # Si no se requiere autenticación y no hay token, retorna None
  if not REQUIRE_AUTH and not token:
    return None
  
  # Si se requiere autenticación pero no hay token, lanza error
  if REQUIRE_AUTH and not token:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token requerido")
  
  if not token:
    return None
  
  try:
    payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    username = payload.get("sub") or payload.get("username")
    if not username:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return {"username": username, "rol": payload.get("rol")}

  except JWTError:
    if REQUIRE_AUTH:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return None
  except RuntimeError as e:
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
