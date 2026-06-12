from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, TypedDict, cast
from database import get_connection
from auth import get_current_user, TokenUser

router = APIRouter(tags=["usuarios"])

class UsuarioRol(TypedDict):
    rol: str

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class EliminarUsuario(BaseModel):
    username: str

@router.delete("/eliminar_usuario", response_model=ApiResponse)
def eliminar_usuario(
    data: EliminarUsuario,
    current_user: TokenUser = Depends(get_current_user),
) -> ApiResponse:

    # Bloquear auto-eliminación
    if data.username == current_user["username"]:
        raise HTTPException(
            status_code=403,
            detail="No podés eliminar tu propio usuario"
        )

    # Verificar permisos: usuarios con rol 'user' no pueden eliminar usuarios
    if not current_user.get("rol") or current_user.get("rol") == "user":
        raise HTTPException(
            status_code=403,
            detail="No tenés permiso para eliminar usuarios"
        )

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar que el usuario a eliminar exista
    cursor.execute(
        "SELECT rol FROM Usuarios WHERE username = %s",
        (data.username,)
    )
    usuario = cast(Optional[UsuarioRol], cursor.fetchone())

    if not usuario:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado"
        )

    # Proteger superadmin
    if usuario["rol"] == "superadmin":
        raise HTTPException(
            status_code=403,
            detail="No se puede eliminar un superadmin"
        )

    # Eliminar usuario
    cursor.execute(
        "DELETE FROM Usuarios WHERE username = %s",
        (data.username,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return ApiResponse(
        success=True,
        message="Usuario eliminado correctamente"
    )
