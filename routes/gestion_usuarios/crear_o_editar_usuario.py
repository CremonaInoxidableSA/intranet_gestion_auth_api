from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from database import get_connection
import bcrypt

router = APIRouter(tags=["usuarios"])

class CrearEditarUsuario(BaseModel):
    id_usuario: int
    nombre: str
    apellido: str
    legajo: int
    dni: Optional[int] = None
    email: EmailStr
    rol_ids: list[int]
    username: str
    password: str

class ApiResponse(BaseModel):
    success: bool
    message: Optional[str] = None

@router.post("/crear_o_editar_usuario", response_model=ApiResponse)
def crear_editar_usuario(data: CrearEditarUsuario) -> ApiResponse:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        if data.id_usuario == 0:
            # CREAR nuevo usuario
            # Verificar duplicados de username, email y legajo
            cursor.execute(
                "SELECT 1 FROM Usuarios WHERE username = %s OR email = %s OR legajo = %s",
                (data.username, data.email, data.legajo)
            )

            if cursor.fetchone():
                raise HTTPException(
                    status_code=400,
                    detail="El usuario, email o legajo ya existen"
                )

            # Hash de contraseña
            hashed_password = bcrypt.hashpw(
                data.password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # Insertar nuevo usuario
            cursor.execute(
                """
                INSERT INTO Usuarios
                (email, username, nombre, apellido, password_hash, habilitado, legajo, dni, cambiar_contra)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    data.email,
                    data.username,
                    data.nombre,
                    data.apellido,
                    hashed_password,
                    1,
                    data.legajo,
                    data.dni,
                    0
                )
            )
            conn.commit()
            nuevo_usuario_id = cursor.lastrowid

            # Asignar roles al usuario
            for rol_id in data.rol_ids:
                cursor.execute(
                    "INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)",
                    (nuevo_usuario_id, rol_id)
                )
            conn.commit()

            message = "Usuario creado correctamente"

        else:
            # EDITAR usuario existente
            # Verificar que el usuario existe
            cursor.execute(
                "SELECT email, username, legajo FROM Usuarios WHERE id = %s",
                (data.id_usuario,)
            )
            usuario_actual = cursor.fetchone()

            if not usuario_actual:
                raise HTTPException(
                    status_code=404,
                    detail="Usuario no encontrado"
                )

            # Verificar duplicados de email, username y legajo si cambiaron
            if (usuario_actual["email"] != data.email or usuario_actual["username"] != data.username or usuario_actual["legajo"] != data.legajo):
                cursor.execute(
                    "SELECT 1 FROM Usuarios WHERE (username = %s OR email = %s OR legajo = %s) AND id != %s",
                    (data.username, data.email, data.legajo, data.id_usuario)
                )
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=400,
                        detail="El usuario, email o legajo ya existen"
                    )

            # Hash de contraseña
            hashed_password = bcrypt.hashpw(
                data.password.encode("utf-8"),
                bcrypt.gensalt()
            ).decode("utf-8")

            # Actualizar usuario
            cursor.execute(
                """
                UPDATE Usuarios
                SET email = %s, username = %s, nombre = %s, apellido = %s, 
                    password_hash = %s, legajo = %s, dni = %s
                WHERE id = %s
                """,
                (
                    data.email,
                    data.username,
                    data.nombre,
                    data.apellido,
                    hashed_password,
                    data.legajo,
                    data.dni,
                    data.id_usuario
                )
            )
            conn.commit()

            # Actualizar roles del usuario
            # Primero eliminar roles anteriores
            cursor.execute(
                "DELETE FROM usuarios_roles WHERE usuario_id = %s",
                (data.id_usuario,)
            )
            conn.commit()
            
            # Insertar nuevos roles
            for rol_id in data.rol_ids:
                cursor.execute(
                    "INSERT INTO usuarios_roles (usuario_id, rol_id) VALUES (%s, %s)",
                    (data.id_usuario, rol_id)
                )
            conn.commit()

            message = "Usuario actualizado correctamente"

    except HTTPException:
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()

    return ApiResponse(success=True, message=message)
