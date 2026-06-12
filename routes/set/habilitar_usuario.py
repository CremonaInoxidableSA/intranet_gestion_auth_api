from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import TypedDict, Optional, cast
from database import get_connection
from auth import get_current_user, TokenUser

router = APIRouter(tags=["usuarios"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class UsuarioRow(TypedDict):
    rol: str
    habilitado: int

class HabilitarUsuario(BaseModel):
  username: str

@router.post("/habilitar_usuario", response_model=ApiResponse)
def habilitar_usuario(data: HabilitarUsuario, current_user: TokenUser = Depends(get_current_user)) -> ApiResponse:
    if not current_user.get("rol") or current_user.get("rol") == "user":
        raise HTTPException(status_code=403, detail="No tenés permiso para modificar usuarios")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT rol, habilitado FROM Usuarios WHERE username = %s",
        (data.username,)
    )
    usuario = cast(UsuarioRow, cursor.fetchone())

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario["rol"] == "superadmin":
        raise HTTPException(
            status_code=403,
            detail="No se puede deshabilitar un superadmin"
        )

    if usuario["habilitado"] == 1:
        return ApiResponse(success=True, message="Usuario ya estaba habilitado")

    cursor.execute(
        "UPDATE Usuarios SET habilitado = 1 WHERE username = %s",
        (data.username,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return ApiResponse(success=True, message="Usuario habilitado exitosamente")
