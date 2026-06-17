from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from typing import Optional, List

router = APIRouter(tags=["usuarios"])

class ObtenerUsuariosRequest(BaseModel):
    current_user_id: int

class UsuarioResponse(BaseModel):
    email: Optional[str]
    username: Optional[str]
    nombre: str
    apellido: str
    roles: List[str]
    habilitado: bool

@router.post("/usuarios")
def obtener_usuarios(data: ObtenerUsuariosRequest) -> List[UsuarioResponse]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar que current_user tenga permiso de puede_consultar
    cursor.execute(
        """SELECT r.puede_consultar 
           FROM usuarios u
           JOIN usuarios_roles ur ON u.id = ur.usuario_id
           JOIN roles r ON ur.rol_id = r.id
           WHERE u.id = %s
           LIMIT 1""",
        (data.current_user_id,)
    )
    permisos = cursor.fetchone()

    if not permisos or not permisos.get("puede_consultar"):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="No tenés permiso para consultar usuarios")

    # Obtener todos los usuarios
    cursor.execute(
        """SELECT u.id, u.email, u.username, u.nombre, u.apellido, u.habilitado
           FROM usuarios u"""
    )
    usuarios_db = cursor.fetchall()

    usuarios_response = []
    
    for usuario in usuarios_db:
        # Obtener roles de cada usuario
        cursor.execute(
            """SELECT r.nombre
               FROM roles r
               JOIN usuarios_roles ur ON r.id = ur.rol_id
               WHERE ur.usuario_id = %s""",
            (usuario["id"],)
        )
        roles_result = cursor.fetchall()
        roles = [row["nombre"] for row in roles_result] if roles_result else []

        usuarios_response.append(UsuarioResponse(
            email=usuario["email"],
            username=usuario["username"],
            nombre=usuario["nombre"],
            apellido=usuario["apellido"],
            roles=roles,
            habilitado=bool(usuario["habilitado"])
        ))

    cursor.close()
    conn.close()

    return usuarios_response