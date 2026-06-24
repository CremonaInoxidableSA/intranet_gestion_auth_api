from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from typing import List

router = APIRouter(tags=["produccion"])

MODULO_PRODUCCION_ID = 4

# Array de roles filtrados
roles_filtrado = [
    {"id": 3, "nombre": "Operario"},
    {"id": 4, "nombre": "Encargado"}
]

class OperarioResponse(BaseModel):
    id_operario: int
    nombre: str
    apellido: str
    legajo: int
    rol_nombre: str
    habilitado: bool

@router.get("/obtener_usuarios_produccion")
def obtener_usuarios_produccion() -> List[OperarioResponse]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener todos los usuarios de producción (rol_id 3 o 4) habilitados
    cursor.execute(
        """SELECT DISTINCT u.id, u.nombre, u.apellido, u.legajo, u.habilitado, ur.rol_id, r.nombre as rol_nombre
           FROM usuarios u
           JOIN usuarios_roles ur ON u.id = ur.usuario_id
           JOIN roles r ON ur.rol_id = r.id
           WHERE ur.rol_id IN (3, 4) AND u.habilitado = TRUE"""
    )
    usuarios_db = cursor.fetchall()

    if not usuarios_db:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="No existen operarios o encargados disponibles")

    usuarios_response = []
    
    for usuario in usuarios_db:
        # Verificar si el usuario tiene un bloqueo en el módulo de producción
        cursor.execute(
            """SELECT 1 FROM usuarios_bloqueados 
               WHERE usuario_id = %s AND modulo_id = %s AND bloqueado = TRUE""",
            (usuario["id"], MODULO_PRODUCCION_ID)
        )
        tiene_bloqueo = cursor.fetchone() is not None
        
        # Si tiene bloqueo, marcar como no habilitado (false)
        habilitado = not tiene_bloqueo
        
        usuarios_response.append(OperarioResponse(
            id_operario=usuario["id"],
            nombre=usuario["nombre"],
            apellido=usuario["apellido"],
            legajo=usuario["legajo"],
            rol_nombre=usuario["rol_nombre"],
            habilitado=habilitado
        ))

    cursor.close()
    conn.close()

    return usuarios_response