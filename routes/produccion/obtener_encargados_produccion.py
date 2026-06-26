from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from typing import List

router = APIRouter(tags=["produccion"])

MODULO_PRODUCCION_ID = 4

class EncargadosResponse(BaseModel):
    id_operario: int
    nombre: str
    apellido: str
    legajo: int

@router.get("/obtener-encargados-produccion")
def obtener_encargados_produccion() -> List[EncargadosResponse]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """SELECT DISTINCT u.id, u.nombre, u.apellido, u.legajo, u.habilitado, ur.rol_id, r.nombre as rol_nombre
           FROM usuarios u
           JOIN usuarios_roles ur ON u.id = ur.usuario_id
           JOIN roles r ON ur.rol_id = r.id
           WHERE ur.rol_id IN (3) AND u.habilitado = TRUE"""
    )
    usuarios_db = cursor.fetchall()

    if not usuarios_db:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="No existen encargados disponibles")

    usuarios_response = []
    
    for usuario in usuarios_db:
        cursor.execute(
            """SELECT 1 FROM usuarios_bloqueados 
               WHERE usuario_id = %s AND modulo_id = %s AND bloqueado = TRUE""",
            (usuario["id"], MODULO_PRODUCCION_ID)
        )
        tiene_bloqueo = cursor.fetchone() is not None
        
        # Si tiene bloqueo, marcar como no habilitado (false)
        habilitado = not tiene_bloqueo
        
        usuarios_response.append(EncargadosResponse(
            id_operario=usuario["id"],
            nombre=usuario["nombre"],
            apellido=usuario["apellido"],
            legajo=usuario["legajo"]
        ))

    cursor.close()
    conn.close()

    usuarios_response.insert(0, EncargadosResponse(
        id_operario=0,
        nombre="Todos los encargados",
        apellido="",
        legajo=0
    ))

    return usuarios_response