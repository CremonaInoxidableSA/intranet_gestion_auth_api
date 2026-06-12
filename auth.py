import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing import TypedDict, Optional

SECRET_KEY: Optional[str] = os.getenv("JWT_SECRET")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")

def get_secret_key() -> str:
  secret = os.getenv("JWT_SECRET")
  if not secret:
    raise RuntimeError("JWT_SECRET no definido. Define JWT_SECRET en el entorno.")
  return secret

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

class TokenUser(TypedDict):
  username: str
  rol: Optional[str]

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenUser:
  try:
    payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
    username = payload.get("sub") or payload.get("username")
    if not username:
      raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
    return {"username": username, "rol": payload.get("rol")}

  except JWTError:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
  except RuntimeError as e:
    # configuración faltante (p. ej. JWT_SECRET); devolver 500 en lugar de dejar que la excepción no manejada cause un traceback
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
