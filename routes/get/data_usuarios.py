from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from typing import Dict, Any, cast, Optional

router = APIRouter(tags=["usuarios"])

class DatosUsuarioRequest(BaseModel):
    current_user_id: int
    usuario_id: int

class DatosUsuarioResponse(BaseModel):
    id: int
    email: Optional[str]
    username: Optional[str]
    nombre: str
    apellido: str
    roles: list[str]
    habilitado: bool
    legajo: int
    dni: Optional[int]
    cambiar_contra: bool

@router.post("/data_usuario", response_model=DatosUsuarioResponse)
def obtener_datos_usuario(data: DatosUsuarioRequest) -> DatosUsuarioResponse:
    if data.current_user_id != data.usuario_id:
        # Verificar que current_user tenga permisos para ver datos de otros usuarios
        conn_perm = get_connection()
        cursor_perm = conn_perm.cursor(dictionary=True)
        
        cursor_perm.execute(
            """SELECT r.puede_consultar 
               FROM usuarios u
               JOIN usuarios_roles ur ON u.id = ur.usuario_id
               JOIN roles r ON ur.rol_id = r.id
               WHERE u.id = %s
               LIMIT 1""",
            (data.current_user_id,)
        )
        permisos = cursor_perm.fetchone()
        cursor_perm.close()
        conn_perm.close()
        
        if not permisos or not permisos.get("puede_consultar"):
            raise HTTPException(status_code=403, detail="No tenés permiso para ver estos datos")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener datos del usuario
        cursor.execute(
            """
            SELECT u.id, u.email, u.username, u.nombre, u.apellido, u.habilitado, u.legajo, u.dni, u.cambiar_contra
            FROM usuarios u
            WHERE u.id = %s
            """,
            (data.usuario_id,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        usuario = cast(Dict[str, Any], usuario)

        # Obtener roles del usuario
        cursor.execute(
            """
            SELECT r.nombre
            FROM roles r
            JOIN usuarios_roles ur ON r.id = ur.rol_id
            WHERE ur.usuario_id = %s
            """,
            (data.usuario_id,)
        )
        roles_result = cursor.fetchall()
        roles = [row["nombre"] for row in roles_result] if roles_result else []

        return DatosUsuarioResponse(
            id=int(usuario["id"]),
            email=usuario["email"],
            username=usuario["username"],
            nombre=usuario["nombre"],
            apellido=usuario["apellido"],
            roles=roles,
            habilitado=bool(usuario["habilitado"]),
            legajo=int(usuario["legajo"]),
            dni=usuario["dni"],
            cambiar_contra=bool(usuario["cambiar_contra"])
        )
    finally:
        cursor.close()
        conn.close()
