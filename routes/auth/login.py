from fastapi import APIRouter, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, cast
from database import get_connection
from auth import get_secret_key, ALGORITHM
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone
import bcrypt
import os

router = APIRouter(tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(credentials: LoginRequest, response: Response) -> Any:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "SELECT username, password_hash, rol, habilitado, email, nombre, apellido, reporte FROM Usuarios WHERE username = %s OR email = %s",
            (credentials.username, credentials.username),
        )
        user = cursor.fetchone()
        if not user:
            return JSONResponse(content={"success": False, "error": "Credenciales inválidas"}, status_code=status.HTTP_401_UNAUTHORIZED)

        user = cast(Dict[str, Any], user)

        habilitado = user.get("habilitado")
        if habilitado is not None and not bool(habilitado):
            return JSONResponse(content={"success": False, "error": "Usuario deshabilitado"}, status_code=status.HTTP_403_FORBIDDEN)

        password_hash = user.get("password_hash")
        if not password_hash or not isinstance(password_hash, str):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Formato inválido de password en la base de datos")

        password_matches = bcrypt.checkpw(
            credentials.password.encode("utf-8"),
            password_hash.encode("utf-8"),
        )

        if not password_matches:
            return JSONResponse(content={"success": False, "error": "Credenciales inválidas"}, status_code=status.HTTP_401_UNAUTHORIZED)

        expire_minutes = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
        expire = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)

        username = user.get("username")
        if not username:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Usuario sin username en la base de datos")

        payload: Dict[str, Any] = {
            "sub": username,
            "rol": user.get("rol"),
            "exp": int(expire.timestamp()),
        }

        token = jwt.encode(payload, get_secret_key(), algorithm=ALGORITHM)

        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=False,
            samesite="lax",
            path="/",
            max_age=expire_minutes * 60,
        )

        user_payload = {
            "username": user.get("username"),
            "email": user.get("email"),
            "nombre": user.get("nombre"),
            "apellido": user.get("apellido"),
            "rol": user.get("rol"),
            "habilitado": user.get("habilitado"),
            "reporte": user.get("reporte"),
        }

        return {"success": True, "data": {"token": token, "user": user_payload}}

    finally:
        cursor.close()
        conn.close()

@router.get("/check")
def check(request: Request) -> Dict[str, Any]:
    token = request.cookies.get("access_token")
    auth = request.headers.get("Authorization")
    if not token and auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]

    if not token:
        return {"success": True, "data": {}}

    try:
        payload = jwt.decode(token, get_secret_key(), algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return {"success": True, "data": {}}

        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT username, email, nombre, apellido, rol, habilitado, reporte FROM Usuarios WHERE username = %s",
            (username,),
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if not user:
            return {"success": True, "data": {}}

        return {"success": True, "data": {"user": user}}
    except JWTError:
        return {"success": True, "data": {}}


@router.post("/logout")
def logout(response: Response) -> Dict[str, Any]:
    response.delete_cookie("access_token", path="/")
    return {"success": True}