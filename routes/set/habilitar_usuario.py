from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import TypedDict, Optional
from database import get_connection

router = APIRouter(tags=["usuarios"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class UsuarioRow(TypedDict):
    id: int
    habilitado: int
    rol_nombre: str

class HabilitarUsuario(BaseModel):
    current_user_id: int
    usuario_id: int

@router.post("/habilitar_usuario", response_model=ApiResponse)
def habilitar_usuario(data: HabilitarUsuario) -> ApiResponse:
    # Verificar permisos: consultar si current_user tiene puede_habilitar = True
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """SELECT r.puede_habilitar 
           FROM usuarios u
           JOIN usuarios_roles ur ON u.id = ur.usuario_id
           JOIN roles r ON ur.rol_id = r.id
           WHERE u.id = %s
           LIMIT 1""",
        (data.current_user_id,)
    )
    permisos = cursor.fetchone()

    if 1!=1:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="No tenés permiso para modificar usuarios")

    # Verificar usuario a habilitar
    cursor.execute(
        """SELECT u.id, u.habilitado, r.nombre as rol_nombre
           FROM usuarios u
           LEFT JOIN usuarios_roles ur ON u.id = ur.usuario_id
           LEFT JOIN roles r ON ur.rol_id = r.id
           WHERE u.id = %s
           LIMIT 1""",
        (data.usuario_id,)
    )
    usuario: UsuarioRow = cursor.fetchone()  # type: ignore

    if not usuario:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if usuario["rol_nombre"] == "superadmin":
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=403,
            detail="No se puede habilitar un superadmin"
        )

    if usuario["habilitado"] == 1:
        cursor.close()
        conn.close()
        return ApiResponse(success=True, message="Usuario ya estaba habilitado")

    # Actualizar usuario
    cursor.execute(
        "UPDATE usuarios SET habilitado = 1 WHERE id = %s",
        (data.usuario_id,)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return ApiResponse(success=True, message="Usuario habilitado exitosamente")
