from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from typing import Dict, Any, cast, Optional

router = APIRouter(tags=["roles"])

class ModuloAcceso(BaseModel):
    nombre: str
    permiso: Optional[str] = None

class SubmoduloAcceso(BaseModel):
    nombre: str
    permiso: Optional[str] = None

class RolResponse(BaseModel):
    id: int
    nombre: str
    modulos: list[ModuloAcceso]
    submodulos: list[SubmoduloAcceso]

@router.get("/lista-roles", response_model=list[RolResponse])
def obtener_todos_los_roles() -> list[RolResponse]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Obtener todos los roles
        cursor.execute("SELECT id, nombre FROM roles")
        roles_db = cursor.fetchall()

        roles_response = []

        for rol in roles_db:
            rol_id = rol["id"]
            rol_nombre = rol["nombre"]

            # Obtener módulos del rol
            cursor.execute(
                """
                SELECT m.nombre, p.nombre as permiso
                FROM modulos m
                JOIN rol_modulos rm ON m.id = rm.modulo_id
                LEFT JOIN permisos p ON rm.permiso_id = p.id
                WHERE rm.rol_id = %s
                """,
                (rol_id,)
            )
            modulos_result = cursor.fetchall()
            modulos = [
                ModuloAcceso(nombre=row["nombre"], permiso=row["permiso"])
                for row in modulos_result
            ] if modulos_result else []

            # Obtener submódulos del rol
            cursor.execute(
                """
                SELECT sm.nombre, p.nombre as permiso
                FROM submodulos sm
                JOIN rol_submodulos rsm ON sm.id = rsm.submodulo_id
                LEFT JOIN permisos p ON rsm.permiso_id = p.id
                WHERE rsm.rol_id = %s
                """,
                (rol_id,)
            )
            submodulos_result = cursor.fetchall()
            submodulos = [
                SubmoduloAcceso(nombre=row["nombre"], permiso=row["permiso"])
                for row in submodulos_result
            ] if submodulos_result else []

            roles_response.append(RolResponse(
                id=int(rol_id),
                nombre=rol_nombre,
                modulos=modulos,
                submodulos=submodulos
            ))

        return roles_response

    finally:
        cursor.close()
        conn.close()
