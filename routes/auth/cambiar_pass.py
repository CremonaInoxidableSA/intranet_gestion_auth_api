from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, TypedDict, cast
from database import get_connection
from auth import get_current_user, TokenUser
import bcrypt

router = APIRouter(tags=["auth"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class ChangePassword(BaseModel):
    current_password: str
    new_password: str

class UsuarioPass(TypedDict):
    password_hash: str

@router.post("/cambiar_password", response_model=ApiResponse)
def cambiar_password(data: ChangePassword, current_user: TokenUser = Depends(get_current_user)) -> ApiResponse:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT password_hash FROM Usuarios WHERE username = %s", (current_user["username"],))
    usuario = cast(Optional[UsuarioPass], cursor.fetchone())

    if not usuario:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    password_hash = usuario["password_hash"]
    if not password_hash:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=500, detail="Formato inválido de password en la base de datos")

    if not bcrypt.checkpw(data.current_password.encode("utf-8"), password_hash.encode("utf-8")):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="Contraseña actual incorrecta")

    new_hashed = bcrypt.hashpw(data.new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute("UPDATE Usuarios SET password_hash = %s WHERE username = %s", (new_hashed, current_user["username"]))
    conn.commit()

    cursor.close()
    conn.close()

    return ApiResponse(success=True, message="Contraseña actualizada correctamente")
