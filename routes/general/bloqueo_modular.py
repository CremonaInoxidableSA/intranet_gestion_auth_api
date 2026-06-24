from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_connection

router = APIRouter(tags=["general"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class BloqueoData(BaseModel):
    usuario_id: int
    modulo_id: int

@router.post("/bloquear-usuario-modulo", response_model=ApiResponse)
def bloqueo_modular(data: BloqueoData) -> ApiResponse:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Validar que exista el usuario
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (data.usuario_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe"
            )

        # Validar que no sea el superadmin
        if data.usuario_id == 1:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=403,
                detail="No se puede bloquear al superadmin"
            )

        # Validar que exista el módulo
        cursor.execute("SELECT id FROM modulos WHERE id = %s", (data.modulo_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="El módulo no existe"
            )

        # Verificar si ya existe un bloqueo
        cursor.execute(
            "SELECT 1 FROM usuarios_bloqueados WHERE usuario_id = %s AND modulo_id = %s",
            (data.usuario_id, data.modulo_id)
        )
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return ApiResponse(
                success=False,
                message="Ya existe un bloqueo a este modulo para el usuario referenciado"
            )

        # Crear el bloqueo
        cursor.execute(
            """INSERT INTO usuarios_bloqueados (usuario_id, modulo_id, bloqueado)
               VALUES (%s, %s, %s)""",
            (data.usuario_id, data.modulo_id, True)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return ApiResponse(
            success=True,
            message="Usuario bloqueado correctamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error al bloquear usuario: {str(e)}"
        )

@router.post("/desbloquear-usuario-modulo", response_model=ApiResponse)
def desbloqueo_modular(data: BloqueoData) -> ApiResponse:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Validar que exista el usuario
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (data.usuario_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="El usuario no existe"
            )

        # Validar que exista el módulo
        cursor.execute("SELECT id FROM modulos WHERE id = %s", (data.modulo_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=404,
                detail="El módulo no existe"
            )

        # Verificar si existe el bloqueo
        cursor.execute(
            "SELECT 1 FROM usuarios_bloqueados WHERE usuario_id = %s AND modulo_id = %s",
            (data.usuario_id, data.modulo_id)
        )
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return ApiResponse(
                success=False,
                message="No existe un bloqueo para ese usuario y modulo"
            )

        # Eliminar el bloqueo
        cursor.execute(
            "DELETE FROM usuarios_bloqueados WHERE usuario_id = %s AND modulo_id = %s",
            (data.usuario_id, data.modulo_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

        return ApiResponse(
            success=True,
            message="Usuario desbloqueado correctamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error al desbloquear usuario: {str(e)}"
        )