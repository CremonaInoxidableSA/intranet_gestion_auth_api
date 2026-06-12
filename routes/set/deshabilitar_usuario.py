from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import TypedDict, Optional
from database import get_connection
from auth import get_current_user, TokenUser

router = APIRouter(tags=["usuarios"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class UsuarioRow(TypedDict):
    rol: str
    habilitado: int

class DeshabilitarUsuario(BaseModel):
    username: str

@router.post("/deshabilitar_usuario", response_model=ApiResponse)
def deshabilitar_usuario(data: DeshabilitarUsuario, current_user: TokenUser = Depends(get_current_user)) -> ApiResponse:
    # Verificar permisos: usuarios con rol 'user' no pueden deshabilitar usuarios
    if not current_user.get("rol") or current_user.get("rol") == "user":
        raise HTTPException(status_code=403, detail="No tenés permiso para modificar usuarios")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar usuario
    cursor.execute(
        "SELECT rol, habilitado FROM Usuarios WHERE username = %s",
        (data.username,)
    )
    usuario: UsuarioRow = cursor.fetchone()  # type: ignore

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario["rol"] == "superadmin":
        raise HTTPException(
            status_code=403,
            detail="No se puede deshabilitar un superadmin"
        )

    if usuario["habilitado"] == 0:
        return ApiResponse(success=True, message="Usuario ya estaba deshabilitado")

    cursor.execute(
        "UPDATE Usuarios SET habilitado = 0 WHERE username = %s",
        (data.username,)
    )
  
    conn.commit()
    cursor.close()
    conn.close()

    return ApiResponse(success=True, message="Usuario deshabilitado exitosamente")
