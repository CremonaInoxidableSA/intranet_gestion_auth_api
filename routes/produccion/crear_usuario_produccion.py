from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Literal
from database import get_connection

router = APIRouter(tags=["produccion"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class CrearUsuarioProduccion(BaseModel):
    current_user_id: int
    nombre: str
    apellido: str
    legajo: int
    rol: Literal["encargado", "operario"]

@router.post("/crear_usuario_produccion", response_model=ApiResponse)
def crear_usuario_produccion(data: CrearUsuarioProduccion) -> ApiResponse:
    # Mapear rol a rol_id
    rol_mapping = {
        "encargado": 3,
        "operario": 4
    }
    rol_id = rol_mapping.get(data.rol)
    
    if not rol_id:
        raise HTTPException(status_code=400, detail="Rol inválido. Use 'encargado' o 'operario'")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar permisos del current_user
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

    if not permisos or not permisos.get("puede_habilitar"):
        cursor.close()
        conn.close()
        raise HTTPException(status_code=403, detail="No tenés permiso para crear usuarios")

    # Verificar que no exista un usuario con el mismo legajo
    cursor.execute(
        """SELECT nombre, apellido FROM usuarios WHERE legajo = %s""",
        (data.legajo,)
    )
    usuario_existente = cursor.fetchone()

    if usuario_existente:
        cursor.close()
        conn.close()
        nombre_existente = usuario_existente.get("nombre")
        apellido_existente = usuario_existente.get("apellido")
        raise HTTPException(
            status_code=400,
            detail=f"Ya existe un usuario en el sistema con el legajo indicado. Este usuario es {nombre_existente} {apellido_existente}"
        )

    # Crear usuario con campos vacíos
    cursor.execute(
        """INSERT INTO usuarios (nombre, apellido, legajo, password_hash, email, username, habilitado, dni, cambiar_contra)
           VALUES (%s, %s, %s, NULL, NULL, NULL, 1, NULL, 0)""",
        (data.nombre, data.apellido, data.legajo)
    )

    usuario_id = cursor.lastrowid

    # Asignar rol al usuario
    cursor.execute(
        """INSERT INTO usuarios_roles (usuario_id, rol_id)
           VALUES (%s, %s)""",
        (usuario_id, rol_id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return ApiResponse(
        success=True,
        message="Usuario de producción creado exitosamente"
    )
