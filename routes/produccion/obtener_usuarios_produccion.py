from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database import get_connection
from typing import List

router = APIRouter(tags=["produccion"])

class OperarioResponse(BaseModel):
    id_operario: int
    nombre: str
    apellido: str
    habilitado: bool

@router.get("/obtener_usuarios_produccion")
def obtener_usuarios_produccion() -> List[OperarioResponse]:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener todos los usuarios de producción (rol_id 3 o 4) habilitados
    cursor.execute(
        """SELECT DISTINCT u.id, u.nombre, u.apellido, u.habilitado
           FROM usuarios u
           JOIN usuarios_roles ur ON u.id = ur.usuario_id
           WHERE ur.rol_id IN (3, 4)"""
    )
    usuarios_db = cursor.fetchall()

    if not usuarios_db:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="No existen operarios o encargados disponibles")

    usuarios_response = []
    
    for usuario in usuarios_db:
        usuarios_response.append(OperarioResponse(
            id_operario=usuario["id"],
            nombre=usuario["nombre"],
            apellido=usuario["apellido"],
            habilitado=usuario["habilitado"]
        ))

    cursor.close()
    conn.close()

    return usuarios_response