from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from routes.produccion.notificaciones import notificar_nuevo_encargado

router = APIRouter(tags=["produccion"])

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

class EditarUsuarioProduccion(BaseModel):
    current_user_id: int
    id_operario: int
    nombre: str
    apellido: str
    viejo_rol_nombre: str
    rol_nombre: str

@router.post("/editar_usuario_produccion", response_model=ApiResponse)
async def editar_usuario_produccion(data: EditarUsuarioProduccion) -> ApiResponse:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        roles_validos = ["encargado-produccion", "operario"]
        
        if data.viejo_rol_nombre not in roles_validos:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="El rol anterior debe ser 'encargado-produccion' u 'operario'"
            )
        
        if data.rol_nombre not in roles_validos:
            cursor.close()
            conn.close()
            raise HTTPException(
                status_code=400,
                detail="El nuevo rol debe ser 'encargado-produccion' u 'operario'"
            )

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
            raise HTTPException(status_code=403, detail="No tenés permiso para editar usuarios")

        # Verificar que el usuario existe
        cursor.execute(
            """SELECT id, nombre, apellido FROM usuarios WHERE id = %s""",
            (data.id_operario,)
        )
        usuario = cursor.fetchone()

        if not usuario:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="El usuario no existe")

        # Actualizar nombre y apellido
        cursor.execute(
            """UPDATE usuarios SET nombre = %s, apellido = %s WHERE id = %s""",
            (data.nombre, data.apellido, data.id_operario)
        )
        conn.commit()

        # Verificar si el rol cambió
        if data.viejo_rol_nombre != data.rol_nombre:
            # Obtener el ID del viejo rol
            cursor.execute(
                """SELECT id FROM roles WHERE nombre = %s""",
                (data.viejo_rol_nombre,)
            )
            viejo_rol = cursor.fetchone()

            # Obtener el ID del nuevo rol
            cursor.execute(
                """SELECT id FROM roles WHERE nombre = %s""",
                (data.rol_nombre,)
            )
            nuevo_rol = cursor.fetchone()

            if not viejo_rol or not nuevo_rol:
                cursor.close()
                conn.close()
                raise HTTPException(status_code=400, detail="Rol inválido")

            viejo_rol_id = viejo_rol['id']
            nuevo_rol_id = nuevo_rol['id']

            # Borrar el viejo rol
            cursor.execute(
                """DELETE FROM usuarios_roles WHERE usuario_id = %s AND rol_id = %s""",
                (data.id_operario, viejo_rol_id)
            )

            # Insertar el nuevo rol
            cursor.execute(
                """INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)""",
                (data.id_operario, nuevo_rol_id)
            )
            conn.commit()

            # Si el nuevo rol es encargado-produccion, enviar notificación
            if data.rol_nombre == "encargado-produccion":
                # Obtener el legajo del usuario
                cursor.execute(
                    """SELECT legajo FROM usuarios WHERE id = %s""",
                    (data.id_operario,)
                )
                usuario_data = cursor.fetchone()
                if usuario_data:
                    await notificar_nuevo_encargado(
                        data.nombre,
                        data.apellido,
                        usuario_data['legajo']
                    )

        cursor.close()
        conn.close()

        return ApiResponse(
            success=True,
            message="Usuario de producción actualizado exitosamente"
        )

    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        conn.close()
        raise HTTPException(
            status_code=500,
            detail=f"Error al actualizar usuario: {str(e)}"
        )
